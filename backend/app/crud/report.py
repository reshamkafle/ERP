from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.crm import CrmLead, CrmOpportunity
from app.models.customer import Customer
from app.models.enums import (
    DocumentPaymentStatus,
    ItemLifecycleStatus,
    LeadStatus,
    PaymentDirection,
    PaymentStatus,
    PurchaseStatus,
    XyzClass,
)
from app.models.payment import Payment
from app.models.permission import Permission
from app.models.procurement_run import ProcurementRun
from app.models.product import Product
from app.models.promotion_run import PromotionRun
from app.models.purchase import Purchase
from app.models.role import Role, UserRoleAssignment
from app.models.sale import Sale, SaleItem
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.report import (
    CashFlowChartPoint,
    CustomerGrowthPoint,
    DeadStockRow,
    FinanceSummaryReportResponse,
    InventoryPerformanceReportResponse,
    ItOverviewReportResponse,
    LowStockRow,
    MarketingFunnelReportResponse,
    OutstandingDocumentRow,
    PurchaseOrderChartPoint,
    PurchaseOrderSummaryRow,
    PurchaseOrdersReportResponse,
    RoleSummaryRow,
    AgentRunStatusRow,
    SaleSummaryRow,
    SalesChartPoint,
    SalesReportResponse,
    SellThroughRow,
    StageCountRow,
    StatusCountRow,
    StockValueRow,
    StockValueReportResponse,
    TopProductRow,
    TopProductsReportResponse,
    VendorSpendRow,
)

TOP_PRODUCTS_LIMIT = 10
LOW_STOCK_LIMIT = 25
DEAD_STOCK_LIMIT = 25
SELL_THROUGH_LIMIT = 25
OPEN_PO_LIMIT = 25
VENDOR_SPEND_LIMIT = 10


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _start_of_today(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_week(now: datetime) -> datetime:
    start_today = _start_of_today(now)
    return start_today - timedelta(days=start_today.weekday())


def _start_of_month(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _period_bounds(period: str, now: datetime | None = None) -> tuple[datetime, datetime, str]:
    now = now or _utc_now()
    if period == "month":
        return _start_of_month(now), now, "month"
    if period == "week":
        return _start_of_week(now), now, "week"
    return _start_of_today(now), now, "today"


def _line_total_expr():
    return SaleItem.quantity * SaleItem.price_at_sale


def _chart_bucket_and_label(period: str):
    if period == "today":
        return func.date_trunc("hour", Sale.created_at), "HH24:00"
    return func.date_trunc("day", Sale.created_at), "Dy Mon DD"


def _po_chart_bucket_and_label(period: str):
    if period == "today":
        return func.date_trunc("hour", Purchase.created_at), "HH24:00"
    return func.date_trunc("day", Purchase.created_at), "Dy Mon DD"


async def get_sales_report(db: AsyncSession, *, period: str) -> SalesReportResponse:
    start, end, normalized = _period_bounds(period)
    line_total = _line_total_expr()

    totals = (
        await db.execute(
            select(
                func.coalesce(func.sum(line_total), 0),
                func.count(func.distinct(Sale.id)),
            )
            .select_from(Sale)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.created_at >= start, Sale.created_at <= end),
        )
    ).one()
    total_revenue, sale_count = totals[0], totals[1]

    bucket, label_fmt = _chart_bucket_and_label(normalized)

    chart_rows = (
        await db.execute(
            select(
                func.to_char(bucket, label_fmt).label("label"),
                func.coalesce(func.sum(line_total), 0),
                func.count(func.distinct(Sale.id)),
            )
            .select_from(Sale)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.created_at >= start, Sale.created_at <= end)
            .group_by(bucket)
            .order_by(bucket),
        )
    ).all()

    sale_totals = (
        select(
            Sale.id.label("sale_id"),
            func.coalesce(func.sum(line_total), 0).label("total"),
            func.count(SaleItem.id).label("item_count"),
        )
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .where(Sale.created_at >= start, Sale.created_at <= end)
        .group_by(Sale.id)
        .subquery()
    )

    sales_rows = (
        await db.execute(
            select(Sale.id, Sale.created_at, sale_totals.c.item_count, sale_totals.c.total)
            .join(sale_totals, sale_totals.c.sale_id == Sale.id)
            .order_by(Sale.created_at.desc())
            .limit(50),
        )
    ).all()

    return SalesReportResponse(
        period=normalized,
        total_revenue=Decimal(str(total_revenue)),
        sale_count=int(sale_count),
        chart=[
            SalesChartPoint(
                label=row.label or "",
                revenue=Decimal(str(row[1])),
                sale_count=int(row[2]),
            )
            for row in chart_rows
        ],
        sales=[
            SaleSummaryRow(
                id=row.id,
                created_at=row.created_at,
                item_count=int(row.item_count),
                total=Decimal(str(row.total)),
            )
            for row in sales_rows
        ],
    )


async def get_top_products_report(db: AsyncSession) -> TopProductsReportResponse:
    now = _utc_now()
    start, end, _ = _period_bounds("week", now)
    line_total = _line_total_expr()

    rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                func.coalesce(func.sum(SaleItem.quantity), 0),
                func.coalesce(func.sum(line_total), 0),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(Sale.created_at >= start, Sale.created_at <= end)
            .group_by(Product.id, Product.sku, Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(TOP_PRODUCTS_LIMIT),
        )
    ).all()

    return TopProductsReportResponse(
        products=[
            TopProductRow(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                quantity_sold=int(row[3]),
                revenue=Decimal(str(row[4])),
            )
            for row in rows
        ],
    )


async def get_stock_value_report(db: AsyncSession) -> StockValueReportResponse:
    line_value = Product.stock * Product.cost_price

    total_row = (
        await db.execute(
            select(
                func.coalesce(func.sum(line_value), 0),
                func.count(Product.id),
            ).where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE),
        )
    ).one()

    items = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.stock,
                Product.cost_price,
                line_value,
            )
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
            .order_by(line_value.desc())
            .limit(25),
        )
    ).all()

    return StockValueReportResponse(
        total_value=Decimal(str(total_row[0])),
        product_count=int(total_row[1]),
        items=[
            StockValueRow(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                stock=row.stock,
                cost_price=row.cost_price,
                line_value=Decimal(str(row[5])),
            )
            for row in items
        ],
    )


async def get_purchase_orders_report(
    db: AsyncSession, *, period: str
) -> PurchaseOrdersReportResponse:
    start, end, normalized = _period_bounds(period)
    bucket, label_fmt = _po_chart_bucket_and_label(normalized)

    totals = (
        await db.execute(
            select(
                func.coalesce(func.sum(Purchase.total), 0),
                func.count(Purchase.id),
            ).where(Purchase.created_at >= start, Purchase.created_at <= end),
        )
    ).one()

    open_totals = (
        await db.execute(
            select(
                func.count(Purchase.id),
                func.coalesce(func.sum(Purchase.total), 0),
            ).where(Purchase.status == PurchaseStatus.DRAFT),
        )
    ).one()

    chart_rows = (
        await db.execute(
            select(
                func.to_char(bucket, label_fmt).label("label"),
                func.coalesce(func.sum(Purchase.total), 0),
                func.count(Purchase.id),
            )
            .where(Purchase.created_at >= start, Purchase.created_at <= end)
            .group_by(bucket)
            .order_by(bucket),
        )
    ).all()

    supplier = aliased(Supplier)
    purchase_rows = (
        await db.execute(
            select(
                Purchase.id,
                Purchase.created_at,
                supplier.name,
                Purchase.status,
                Purchase.total,
            )
            .outerjoin(supplier, supplier.id == Purchase.supplier_id)
            .where(Purchase.created_at >= start, Purchase.created_at <= end)
            .order_by(Purchase.created_at.desc())
            .limit(50),
        )
    ).all()

    return PurchaseOrdersReportResponse(
        period=normalized,
        total_spend=Decimal(str(totals[0])),
        po_count=int(totals[1]),
        open_po_count=int(open_totals[0]),
        open_po_value=Decimal(str(open_totals[1])),
        chart=[
            PurchaseOrderChartPoint(
                label=row.label or "",
                spend=Decimal(str(row[1])),
                po_count=int(row[2]),
            )
            for row in chart_rows
        ],
        purchases=[
            PurchaseOrderSummaryRow(
                id=row.id,
                created_at=row.created_at,
                supplier_name=row[2],
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                total=Decimal(str(row.total)),
            )
            for row in purchase_rows
        ],
    )


async def _fetch_open_purchase_rows(db: AsyncSession, limit: int) -> list[PurchaseOrderSummaryRow]:
    supplier = aliased(Supplier)
    rows = (
        await db.execute(
            select(
                Purchase.id,
                Purchase.created_at,
                supplier.name,
                Purchase.status,
                Purchase.total,
            )
            .outerjoin(supplier, supplier.id == Purchase.supplier_id)
            .where(Purchase.status == PurchaseStatus.DRAFT)
            .order_by(Purchase.created_at.desc())
            .limit(limit),
        )
    ).all()
    return [
        PurchaseOrderSummaryRow(
            id=row.id,
            created_at=row.created_at,
            supplier_name=row[2],
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            total=Decimal(str(row.total)),
        )
        for row in rows
    ]


async def get_inventory_performance_report(db: AsyncSession) -> InventoryPerformanceReportResponse:
    line_value = Product.stock * Product.cost_price

    low_stock_count = (
        await db.execute(
            select(func.count())
            .select_from(Product)
            .where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.stock <= Product.low_stock_threshold,
            ),
        )
    ).scalar_one()

    dead_stock_value = (
        await db.execute(
            select(func.coalesce(func.sum(line_value), 0))
            .select_from(Product)
            .where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.xyz_class == XyzClass.NON_MOVING,
            ),
        )
    ).scalar_one()

    total_stock_value = (
        await db.execute(
            select(func.coalesce(func.sum(line_value), 0))
            .select_from(Product)
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE),
        )
    ).scalar_one()

    qty_sold_subq = (
        select(
            SaleItem.product_id.label("product_id"),
            func.coalesce(func.sum(SaleItem.quantity), 0).label("qty_sold"),
        )
        .group_by(SaleItem.product_id)
        .subquery()
    )

    turnover_rows = (
        await db.execute(
            select(
                Product.id,
                Product.stock,
                func.coalesce(qty_sold_subq.c.qty_sold, 0),
            )
            .outerjoin(qty_sold_subq, qty_sold_subq.c.product_id == Product.id)
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE, Product.stock > 0),
        )
    ).all()

    turnover_ratios: list[Decimal] = []
    for row in turnover_rows:
        qty_sold = int(row[2])
        turnover_ratios.append(Decimal(qty_sold) / Decimal(row.stock))
    avg_turnover = (
        sum(turnover_ratios, start=Decimal("0")) / Decimal(len(turnover_ratios))
        if turnover_ratios
        else Decimal("0")
    )

    low_stock_items = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.stock,
                Product.low_stock_threshold,
                line_value,
            )
            .where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.stock <= Product.low_stock_threshold,
            )
            .order_by(Product.stock.asc())
            .limit(LOW_STOCK_LIMIT),
        )
    ).all()

    dead_stock_items = (
        await db.execute(
            select(Product.id, Product.sku, Product.name, Product.stock, line_value)
            .where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.xyz_class == XyzClass.NON_MOVING,
            )
            .order_by(line_value.desc())
            .limit(DEAD_STOCK_LIMIT),
        )
    ).all()

    sell_through_rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                func.coalesce(qty_sold_subq.c.qty_sold, 0),
                Product.stock,
            )
            .outerjoin(qty_sold_subq, qty_sold_subq.c.product_id == Product.id)
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE)
            .order_by(func.coalesce(qty_sold_subq.c.qty_sold, 0).desc())
            .limit(SELL_THROUGH_LIMIT),
        )
    ).all()

    open_po_count = (
        await db.execute(
            select(func.count()).select_from(Purchase).where(Purchase.status == PurchaseStatus.DRAFT),
        )
    ).scalar_one()

    open_po_items = await _fetch_open_purchase_rows(db, OPEN_PO_LIMIT)

    sell_through_items: list[SellThroughRow] = []
    for row in sell_through_rows:
        units_sold = int(row[3])
        stock = int(row[4])
        denominator = units_sold + stock
        pct = (
            (Decimal(units_sold) / Decimal(denominator) * Decimal("100")).quantize(Decimal("0.01"))
            if denominator > 0
            else Decimal("0")
        )
        sell_through_items.append(
            SellThroughRow(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                units_sold=units_sold,
                stock=stock,
                sell_through_pct=pct,
            )
        )

    return InventoryPerformanceReportResponse(
        low_stock_count=int(low_stock_count),
        dead_stock_value=Decimal(str(dead_stock_value)).quantize(Decimal("0.01")),
        total_stock_value=Decimal(str(total_stock_value)).quantize(Decimal("0.01")),
        avg_turnover_ratio=avg_turnover.quantize(Decimal("0.0001")),
        low_stock_items=[
            LowStockRow(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                stock=row.stock,
                low_stock_threshold=row.low_stock_threshold,
                line_value=Decimal(str(row[5])).quantize(Decimal("0.01")),
            )
            for row in low_stock_items
        ],
        dead_stock_items=[
            DeadStockRow(
                product_id=row.id,
                sku=row.sku,
                name=row.name,
                stock=row.stock,
                line_value=Decimal(str(row[4])).quantize(Decimal("0.01")),
            )
            for row in dead_stock_items
        ],
        sell_through_items=sell_through_items,
        open_po_count=int(open_po_count),
        open_po_items=open_po_items,
    )


async def get_finance_summary_report(db: AsyncSession, *, period: str) -> FinanceSummaryReportResponse:
    start, end, normalized = _period_bounds(period)
    confirmed = Payment.status == PaymentStatus.CONFIRMED

    payments_in = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(
                confirmed,
                Payment.direction == PaymentDirection.INBOUND,
                Payment.payment_date >= start.date(),
                Payment.payment_date <= end.date(),
            ),
        )
    ).scalar_one()

    payments_out = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(
                confirmed,
                Payment.direction == PaymentDirection.OUTBOUND,
                Payment.payment_date >= start.date(),
                Payment.payment_date <= end.date(),
            ),
        )
    ).scalar_one()

    bucket = func.date_trunc("day", Payment.payment_date)
    chart_rows = (
        await db.execute(
            select(
                func.to_char(bucket, "Dy Mon DD").label("label"),
                func.coalesce(
                    func.sum(Payment.amount).filter(Payment.direction == PaymentDirection.INBOUND),
                    0,
                ),
                func.coalesce(
                    func.sum(Payment.amount).filter(Payment.direction == PaymentDirection.OUTBOUND),
                    0,
                ),
            )
            .where(
                confirmed,
                Payment.payment_date >= start.date(),
                Payment.payment_date <= end.date(),
            )
            .group_by(bucket)
            .order_by(bucket),
        )
    ).all()

    ap_outstanding = (
        await db.execute(
            select(func.coalesce(func.sum(Purchase.total - Purchase.amount_paid), 0)).where(
                Purchase.payment_status != DocumentPaymentStatus.PAID,
            ),
        )
    ).scalar_one()

    ar_outstanding = (
        await db.execute(
            select(func.coalesce(func.sum(Sale.total - Sale.amount_paid), 0)).where(
                Sale.payment_status != DocumentPaymentStatus.PAID,
            ),
        )
    ).scalar_one()

    line_total = _line_total_expr()
    revenue = (
        await db.execute(
            select(func.coalesce(func.sum(line_total), 0))
            .select_from(Sale)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.created_at >= start, Sale.created_at <= end),
        )
    ).scalar_one()

    cogs_approx = (
        await db.execute(
            select(
                func.coalesce(func.sum(SaleItem.quantity * Product.cost_price), 0),
            )
            .select_from(SaleItem)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .join(Product, Product.id == SaleItem.product_id)
            .where(Sale.created_at >= start, Sale.created_at <= end),
        )
    ).scalar_one()

    revenue_dec = Decimal(str(revenue))
    cogs_dec = Decimal(str(cogs_approx))
    gross_margin_pct = (
        ((revenue_dec - cogs_dec) / revenue_dec * Decimal("100")).quantize(Decimal("0.01"))
        if revenue_dec > 0
        else Decimal("0")
    )

    supplier = aliased(Supplier)
    ap_rows = (
        await db.execute(
            select(
                Purchase.id,
                func.coalesce(supplier.name, "Unknown supplier"),
                Purchase.total,
                Purchase.amount_paid,
            )
            .outerjoin(supplier, supplier.id == Purchase.supplier_id)
            .where(Purchase.payment_status != DocumentPaymentStatus.PAID)
            .order_by((Purchase.total - Purchase.amount_paid).desc())
            .limit(10),
        )
    ).all()

    vendor_rows = (
        await db.execute(
            select(
                Purchase.supplier_id,
                func.coalesce(supplier.name, "Unknown supplier"),
                func.coalesce(func.sum(Purchase.total), 0),
                func.count(Purchase.id),
            )
            .outerjoin(supplier, supplier.id == Purchase.supplier_id)
            .where(Purchase.created_at >= start, Purchase.created_at <= end)
            .group_by(Purchase.supplier_id, supplier.name)
            .order_by(func.sum(Purchase.total).desc())
            .limit(VENDOR_SPEND_LIMIT),
        )
    ).all()

    return FinanceSummaryReportResponse(
        period=normalized,
        payments_in=Decimal(str(payments_in)).quantize(Decimal("0.01")),
        payments_out=Decimal(str(payments_out)).quantize(Decimal("0.01")),
        ap_outstanding=Decimal(str(ap_outstanding)).quantize(Decimal("0.01")),
        ar_outstanding=Decimal(str(ar_outstanding)).quantize(Decimal("0.01")),
        revenue=revenue_dec.quantize(Decimal("0.01")),
        cogs_approx=cogs_dec.quantize(Decimal("0.01")),
        gross_margin_pct=gross_margin_pct,
        chart=[
            CashFlowChartPoint(
                label=row.label or "",
                inbound=Decimal(str(row[1])).quantize(Decimal("0.01")),
                outbound=Decimal(str(row[2])).quantize(Decimal("0.01")),
            )
            for row in chart_rows
        ],
        ap_by_supplier=[
            OutstandingDocumentRow(
                id=row.id,
                party_name=row[1],
                total=Decimal(str(row.total)).quantize(Decimal("0.01")),
                amount_paid=Decimal(str(row.amount_paid)).quantize(Decimal("0.01")),
                outstanding=Decimal(str(row.total - row.amount_paid)).quantize(Decimal("0.01")),
            )
            for row in ap_rows
        ],
        po_spend_by_vendor=[
            VendorSpendRow(
                supplier_id=row[0],
                supplier_name=row[1],
                total_spend=Decimal(str(row[2])).quantize(Decimal("0.01")),
                po_count=int(row[3]),
            )
            for row in vendor_rows
        ],
    )


async def get_marketing_funnel_report(db: AsyncSession) -> MarketingFunnelReportResponse:
    total_leads = (await db.execute(select(func.count()).select_from(CrmLead))).scalar_one()

    lead_status_rows = (
        await db.execute(
            select(CrmLead.status, func.count())
            .group_by(CrmLead.status)
            .order_by(func.count().desc()),
        )
    ).all()

    total_opportunities = (
        await db.execute(select(func.count()).select_from(CrmOpportunity))
    ).scalar_one()

    opp_stage_rows = (
        await db.execute(
            select(
                CrmOpportunity.stage,
                func.count(),
                func.coalesce(func.sum(CrmOpportunity.expected_value), 0),
            )
            .group_by(CrmOpportunity.stage)
            .order_by(func.count().desc()),
        )
    ).all()

    total_customers = (await db.execute(select(func.count()).select_from(Customer))).scalar_one()

    now = _utc_now()
    thirty_days_ago = now - timedelta(days=30)
    new_customers_30d = (
        await db.execute(
            select(func.count())
            .select_from(Customer)
            .where(Customer.created_at >= thirty_days_ago),
        )
    ).scalar_one()

    bucket = func.date_trunc("day", Customer.created_at)
    growth_rows = (
        await db.execute(
            select(
                func.to_char(bucket, "Dy Mon DD").label("label"),
                func.count(),
            )
            .where(Customer.created_at >= thirty_days_ago)
            .group_by(bucket)
            .order_by(bucket),
        )
    ).all()

    return MarketingFunnelReportResponse(
        total_leads=int(total_leads),
        leads_by_status=[
            StatusCountRow(
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                count=int(row[1]),
            )
            for row in lead_status_rows
        ],
        total_opportunities=int(total_opportunities),
        opportunities_by_stage=[
            StageCountRow(
                stage=row.stage.value if hasattr(row.stage, "value") else str(row.stage),
                count=int(row[1]),
                total_value=Decimal(str(row[2])).quantize(Decimal("0.01")),
            )
            for row in opp_stage_rows
        ],
        total_customers=int(total_customers),
        new_customers_30d=int(new_customers_30d),
        customer_growth_chart=[
            CustomerGrowthPoint(label=row.label or "", count=int(row[1])) for row in growth_rows
        ],
    )


async def get_it_overview_report(db: AsyncSession) -> ItOverviewReportResponse:
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    active_user_count = (
        await db.execute(select(func.count()).select_from(User).where(User.is_active.is_(True)))
    ).scalar_one()

    role_count = (await db.execute(select(func.count()).select_from(Role))).scalar_one()
    permission_count = (await db.execute(select(func.count()).select_from(Permission))).scalar_one()

    role_rows = (
        await db.execute(
            select(Role.name, func.count(UserRoleAssignment.id))
            .outerjoin(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .group_by(Role.id, Role.name)
            .order_by(func.count(UserRoleAssignment.id).desc())
            .limit(15),
        )
    ).all()

    proc_rows = (
        await db.execute(
            select(ProcurementRun.status, func.count())
            .group_by(ProcurementRun.status)
            .order_by(func.count().desc()),
        )
    ).all()

    promo_rows = (
        await db.execute(
            select(PromotionRun.status, func.count())
            .group_by(PromotionRun.status)
            .order_by(func.count().desc()),
        )
    ).all()

    agent_runs: list[AgentRunStatusRow] = [
        AgentRunStatusRow(
            run_type="procurement",
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            count=int(row[1]),
        )
        for row in proc_rows
    ] + [
        AgentRunStatusRow(
            run_type="promotion",
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            count=int(row[1]),
        )
        for row in promo_rows
    ]

    return ItOverviewReportResponse(
        api_status="ok",
        db_status=db_status,
        active_user_count=int(active_user_count),
        role_count=int(role_count),
        permission_count=int(permission_count),
        roles=[
            RoleSummaryRow(role_name=row.name, user_count=int(row[1])) for row in role_rows
        ],
        agent_runs=agent_runs,
    )
