from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.report import (
    SaleSummaryRow,
    SalesChartPoint,
    SalesReportResponse,
    StockValueRow,
    StockValueReportResponse,
    TopProductRow,
    TopProductsReportResponse,
)

TOP_PRODUCTS_LIMIT = 10


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _start_of_today(now: datetime) -> datetime:
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _start_of_week(now: datetime) -> datetime:
    # Monday as first day of week
    start_today = _start_of_today(now)
    return start_today - timedelta(days=start_today.weekday())


def _period_bounds(period: str, now: datetime | None = None) -> tuple[datetime, datetime, str]:
    now = now or _utc_now()
    if period == "week":
        return _start_of_week(now), now, "week"
    return _start_of_today(now), now, "today"


def _line_total_expr():
    return SaleItem.quantity * SaleItem.price_at_sale


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

    if normalized == "today":
        bucket = func.date_trunc("hour", Sale.created_at)
        label_fmt = "HH24:00"
    else:
        bucket = func.date_trunc("day", Sale.created_at)
        label_fmt = "Dy Mon DD"

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
