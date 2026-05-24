from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import module_record as module_record_crud
from app.crud import crm as crm_crud
from app.models.crm import CrmActivity
from app.models.customer import Customer
from app.models.module_record import ModuleRecord
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.sale import Sale, SaleItem
from app.models.supplier import Supplier
from app.modules.catalog import MODULE_BY_CODE, ErpModuleDef
from app.schemas.module_record import (
    ModuleFeatureCount,
    ModuleIntegrationMetric,
    ModuleOverviewResponse,
)


async def _sales_revenue(db: AsyncSession) -> Decimal:
    result = await db.execute(
        select(
            func.coalesce(
                func.sum(SaleItem.quantity * SaleItem.price_at_sale),
                0,
            )
        )
    )
    return Decimal(str(result.scalar_one()))


async def _integration_metrics(db: AsyncSession, module: ErpModuleDef) -> list[ModuleIntegrationMetric]:
    metrics: list[ModuleIntegrationMetric] = []
    code = module.code

    if code in ("finance", "sales", "platform"):
        revenue = await _sales_revenue(db)
        metrics.append(
            ModuleIntegrationMetric(
                label="Sales revenue (all time)",
                value=f"{revenue:,.2f}",
                hint="From POS and sales orders",
            )
        )

    if code in ("finance", "procurement", "scm"):
        po_count = (await db.execute(select(func.count()).select_from(Purchase))).scalar_one()
        metrics.append(
            ModuleIntegrationMetric(
                label="Purchase orders",
                value=str(po_count),
                hint="Linked from Purchases module",
            )
        )

    if code in ("warehouse", "scm", "manufacturing", "procurement"):
        sku_count = (await db.execute(select(func.count()).select_from(Product))).scalar_one()
        low_stock = (
            await db.execute(
                select(func.count()).where(Product.stock <= Product.low_stock_threshold)
            )
        ).scalar_one()
        metrics.append(
            ModuleIntegrationMetric(label="Active SKUs", value=str(sku_count))
        )
        metrics.append(
            ModuleIntegrationMetric(label="Low stock SKUs", value=str(low_stock))
        )

    if code in ("procurement", "scm"):
        supplier_count = (await db.execute(select(func.count()).select_from(Supplier))).scalar_one()
        metrics.append(
            ModuleIntegrationMetric(label="Suppliers", value=str(supplier_count))
        )

    if code in ("crm", "sales"):
        customer_count = (await db.execute(select(func.count()).select_from(Customer))).scalar_one()
        metrics.append(
            ModuleIntegrationMetric(label="Customers", value=str(customer_count))
        )

    if code == "crm":
        open_leads = await crm_crud.count_open_leads(db)
        metrics.append(ModuleIntegrationMetric(label="Open leads", value=str(open_leads)))
        _, pipeline_value = await crm_crud.pipeline_summary(db)
        metrics.append(
            ModuleIntegrationMetric(
                label="Pipeline value (open)",
                value=f"{pipeline_value:,.2f}",
            )
        )
        activity_count = (
            await db.execute(select(func.count()).select_from(CrmActivity))
        ).scalar_one()
        metrics.append(ModuleIntegrationMetric(label="Activities logged", value=str(activity_count)))
        ticket_count = (
            await db.execute(
                select(func.count()).where(
                    ModuleRecord.module_code == "crm",
                    ModuleRecord.feature_code == "support_tickets",
                )
            )
        ).scalar_one()
        metrics.append(ModuleIntegrationMetric(label="Support tickets", value=str(ticket_count)))

    if code == "sales":
        order_count = (await db.execute(select(func.count()).select_from(Sale))).scalar_one()
        metrics.append(
            ModuleIntegrationMetric(label="Sales orders", value=str(order_count))
        )

    return metrics


async def build_module_overview(db: AsyncSession, module_code: str) -> ModuleOverviewResponse | None:
    module = MODULE_BY_CODE.get(module_code)
    if module is None:
        return None

    counts = await module_record_crud.count_records_by_feature(db, module_code)
    features = [
        ModuleFeatureCount(
            code=f.code,
            name=f.name,
            description=f.description,
            record_count=counts.get(f.code, 0),
        )
        for f in module.features
    ]
    integration = await _integration_metrics(db, module)

    return ModuleOverviewResponse(
        module_code=module.code,
        module_name=module.name,
        description=module.description,
        features=features,
        integration_metrics=integration,
        total_records=sum(counts.values()),
    )
