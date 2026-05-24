"""Per-product sales metrics for inventory grid view (last 30 days)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.report import _line_total_expr
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.models.user import User

LOOKBACK_DAYS = 30


@dataclass(frozen=True)
class SalesDailyPoint:
    date: str
    quantity_sold: int = 0
    revenue: Decimal = Decimal("0")


@dataclass(frozen=True)
class ProductSalesInsight:
    quantity_sold: int = 0
    revenue: Decimal = Decimal("0")
    top_buyer_name: str | None = None
    top_seller_name: str | None = None
    daily_chart: tuple[SalesDailyPoint, ...] = ()


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _chart_window(now: datetime | None = None) -> tuple[datetime, datetime, list[date]]:
    now = now or _utc_now()
    end_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_day = end_day - timedelta(days=LOOKBACK_DAYS - 1)
    days = [start_day.date() + timedelta(days=i) for i in range(LOOKBACK_DAYS)]
    return start_day, now, days


def _build_daily_series(
    days: list[date],
    by_day: dict[date, tuple[int, Decimal]],
) -> tuple[SalesDailyPoint, ...]:
    return tuple(
        SalesDailyPoint(
            date=d.isoformat(),
            quantity_sold=by_day.get(d, (0, Decimal("0")))[0],
            revenue=by_day.get(d, (0, Decimal("0")))[1],
        )
        for d in days
    )


async def batch_inventory_sales_insights(
    db: AsyncSession,
    product_ids: list[int],
) -> dict[int, ProductSalesInsight]:
    if not product_ids:
        return {}

    start, end, days = _chart_window()
    line_total = _line_total_expr()
    sale_window = (Sale.created_at >= start, Sale.created_at <= end)
    day_bucket = func.date_trunc("day", Sale.created_at)

    totals_rows = (
        await db.execute(
            select(
                SaleItem.product_id,
                func.coalesce(func.sum(SaleItem.quantity), 0),
                func.coalesce(func.sum(line_total), 0),
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(SaleItem.product_id.in_(product_ids), *sale_window)
            .group_by(SaleItem.product_id),
        )
    ).all()

    daily_rows = (
        await db.execute(
            select(
                SaleItem.product_id,
                day_bucket,
                func.coalesce(func.sum(SaleItem.quantity), 0),
                func.coalesce(func.sum(line_total), 0),
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(SaleItem.product_id.in_(product_ids), *sale_window)
            .group_by(SaleItem.product_id, day_bucket)
            .order_by(SaleItem.product_id, day_bucket),
        )
    ).all()

    daily_by_product: dict[int, dict[date, tuple[int, Decimal]]] = {}
    for row in daily_rows:
        pid = int(row[0])
        bucket: datetime = row[1]
        day = bucket.date() if hasattr(bucket, "date") else bucket
        daily_by_product.setdefault(pid, {})[day] = (int(row[2]), Decimal(str(row[3])))

    buyer_agg = (
        select(
            SaleItem.product_id.label("product_id"),
            func.coalesce(Customer.name, "Walk-in").label("buyer_name"),
            func.sum(SaleItem.quantity).label("qty"),
        )
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .outerjoin(Customer, Customer.id == Sale.customer_id)
        .where(SaleItem.product_id.in_(product_ids), *sale_window)
        .group_by(SaleItem.product_id, Customer.name)
    ).subquery()

    buyer_ranked = (
        select(
            buyer_agg.c.product_id,
            buyer_agg.c.buyer_name,
            func.row_number()
            .over(
                partition_by=buyer_agg.c.product_id,
                order_by=buyer_agg.c.qty.desc(),
            )
            .label("rn"),
        )
    ).subquery()

    buyer_rows = (
        await db.execute(
            select(buyer_ranked.c.product_id, buyer_ranked.c.buyer_name).where(
                buyer_ranked.c.rn == 1,
            ),
        )
    ).all()

    seller_agg = (
        select(
            SaleItem.product_id.label("product_id"),
            func.coalesce(User.email, "Unknown").label("seller_name"),
            func.sum(SaleItem.quantity).label("qty"),
        )
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .outerjoin(User, User.id == Sale.created_by_id)
        .where(SaleItem.product_id.in_(product_ids), *sale_window)
        .group_by(SaleItem.product_id, User.email)
    ).subquery()

    seller_ranked = (
        select(
            seller_agg.c.product_id,
            seller_agg.c.seller_name,
            func.row_number()
            .over(
                partition_by=seller_agg.c.product_id,
                order_by=seller_agg.c.qty.desc(),
            )
            .label("rn"),
        )
    ).subquery()

    seller_rows = (
        await db.execute(
            select(seller_ranked.c.product_id, seller_ranked.c.seller_name).where(
                seller_ranked.c.rn == 1,
            ),
        )
    ).all()

    result: dict[int, ProductSalesInsight] = {
        pid: ProductSalesInsight(
            daily_chart=_build_daily_series(days, daily_by_product.get(pid, {})),
        )
        for pid in product_ids
    }

    for row in totals_rows:
        pid = int(row[0])
        existing = result[pid]
        result[pid] = ProductSalesInsight(
            quantity_sold=int(row[1]),
            revenue=Decimal(str(row[2])),
            top_buyer_name=existing.top_buyer_name,
            top_seller_name=existing.top_seller_name,
            daily_chart=existing.daily_chart,
        )

    for row in buyer_rows:
        pid = int(row[0])
        existing = result[pid]
        result[pid] = ProductSalesInsight(
            quantity_sold=existing.quantity_sold,
            revenue=existing.revenue,
            top_buyer_name=row[1],
            top_seller_name=existing.top_seller_name,
            daily_chart=existing.daily_chart,
        )

    for row in seller_rows:
        pid = int(row[0])
        existing = result[pid]
        result[pid] = ProductSalesInsight(
            quantity_sold=existing.quantity_sold,
            revenue=existing.revenue,
            top_buyer_name=existing.top_buyer_name,
            top_seller_name=row[1],
            daily_chart=existing.daily_chart,
        )

    return result
