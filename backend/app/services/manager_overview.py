from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CrmLead
from app.models.enums import (
    DocumentPaymentStatus,
    ItemLifecycleStatus,
    LeadStatus,
    ProductionOrderStatus,
    PurchaseStatus,
)
from app.models.manufacturing_ops import ProductionOrder
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.sale import Sale, SaleItem
from app.schemas.dashboard import (
    ExceptionAlertRow,
    ManagerOverviewChartPoint,
    ManagerOverviewResponse,
)


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


async def build_manager_overview(db: AsyncSession, *, period: str) -> ManagerOverviewResponse:
    start, end, normalized = _period_bounds(period)
    today = _utc_now().date()

    line_total = SaleItem.quantity * SaleItem.price_at_sale

    sales_bucket = func.date_trunc("day", Sale.created_at)
    sales_chart_rows = (
        await db.execute(
            select(
                func.to_char(sales_bucket, "Dy Mon DD").label("label"),
                func.coalesce(func.sum(line_total), 0),
            )
            .select_from(Sale)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.created_at >= start, Sale.created_at <= end)
            .group_by(sales_bucket)
            .order_by(sales_bucket),
        )
    ).all()

    po_bucket = func.date_trunc("day", Purchase.created_at)
    po_chart_rows = (
        await db.execute(
            select(
                func.to_char(po_bucket, "Dy Mon DD").label("label"),
                func.coalesce(func.sum(Purchase.total), 0),
            )
            .where(Purchase.created_at >= start, Purchase.created_at <= end)
            .group_by(po_bucket)
            .order_by(po_bucket),
        )
    ).all()

    po_by_label = {row.label or "": Decimal(str(row[1])) for row in po_chart_rows}
    chart: list[ManagerOverviewChartPoint] = []
    for row in sales_chart_rows:
        label = row.label or ""
        chart.append(
            ManagerOverviewChartPoint(
                label=label,
                revenue=Decimal(str(row[1])).quantize(Decimal("0.01")),
                purchase_spend=po_by_label.get(label, Decimal("0")).quantize(Decimal("0.01")),
            )
        )
    for label, spend in po_by_label.items():
        if not any(point.label == label for point in chart):
            chart.append(
                ManagerOverviewChartPoint(
                    label=label,
                    revenue=Decimal("0"),
                    purchase_spend=spend.quantize(Decimal("0.01")),
                )
            )

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

    unpaid_po_count = (
        await db.execute(
            select(func.count())
            .select_from(Purchase)
            .where(Purchase.payment_status != DocumentPaymentStatus.PAID),
        )
    ).scalar_one()

    open_po_count = (
        await db.execute(
            select(func.count()).select_from(Purchase).where(Purchase.status == PurchaseStatus.DRAFT),
        )
    ).scalar_one()

    stale_leads_count = (
        await db.execute(
            select(func.count())
            .select_from(CrmLead)
            .where(
                CrmLead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED]),
                CrmLead.updated_at < _utc_now() - timedelta(days=14),
            ),
        )
    ).scalar_one()

    overdue_production_count = (
        await db.execute(
            select(func.count())
            .select_from(ProductionOrder)
            .where(
                ProductionOrder.end_date.is_not(None),
                ProductionOrder.end_date < today,
                ProductionOrder.status.notin_(
                    [
                        ProductionOrderStatus.COMPLETED,
                        ProductionOrderStatus.CLOSED,
                        ProductionOrderStatus.CANCELLED,
                    ]
                ),
            ),
        )
    ).scalar_one()

    total_revenue = (
        await db.execute(
            select(func.coalesce(func.sum(line_total), 0))
            .select_from(Sale)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.created_at >= start, Sale.created_at <= end),
        )
    ).scalar_one()

    total_po_spend = (
        await db.execute(
            select(func.coalesce(func.sum(Purchase.total), 0)).where(
                Purchase.created_at >= start,
                Purchase.created_at <= end,
            ),
        )
    ).scalar_one()

    stock_value = (
        await db.execute(
            select(func.coalesce(func.sum(Product.stock * Product.cost_price), 0))
            .select_from(Product)
            .where(Product.lifecycle_status == ItemLifecycleStatus.ACTIVE),
        )
    ).scalar_one()

    alerts: list[ExceptionAlertRow] = []
    if int(low_stock_count) > 0:
        alerts.append(
            ExceptionAlertRow(
                severity="warning",
                category="inventory",
                message=f"{low_stock_count} SKU(s) at or below low-stock threshold",
            )
        )
    if int(unpaid_po_count) > 0:
        alerts.append(
            ExceptionAlertRow(
                severity="warning",
                category="finance",
                message=f"{unpaid_po_count} purchase order(s) with outstanding AP balance",
            )
        )
    if int(open_po_count) > 0:
        alerts.append(
            ExceptionAlertRow(
                severity="info",
                category="procurement",
                message=f"{open_po_count} draft purchase order(s) awaiting receipt",
            )
        )
    if int(stale_leads_count) > 0:
        alerts.append(
            ExceptionAlertRow(
                severity="warning",
                category="marketing",
                message=f"{stale_leads_count} lead(s) stale for 14+ days",
            )
        )
    if int(overdue_production_count) > 0:
        alerts.append(
            ExceptionAlertRow(
                severity="critical",
                category="manufacturing",
                message=f"{overdue_production_count} production order(s) past end date",
            )
        )

    return ManagerOverviewResponse(
        period=normalized,
        total_revenue=Decimal(str(total_revenue)).quantize(Decimal("0.01")),
        total_purchase_spend=Decimal(str(total_po_spend)).quantize(Decimal("0.01")),
        inventory_value=Decimal(str(stock_value)).quantize(Decimal("0.01")),
        low_stock_count=int(low_stock_count),
        open_po_count=int(open_po_count),
        chart=chart,
        alerts=alerts,
    )
