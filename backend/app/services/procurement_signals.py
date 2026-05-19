"""Deterministic procurement signals for agent input (no LLM)."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem


@dataclass(frozen=True)
class ThresholdProduct:
    product_id: int
    sku: str
    name: str
    stock: int
    low_stock_threshold: int
    cost_price: Decimal
    default_supplier_id: int | None


@dataclass(frozen=True)
class VelocityProduct:
    product_id: int
    sku: str
    name: str
    quantity_sold: int
    stock: int
    cost_price: Decimal
    default_supplier_id: int | None


@dataclass(frozen=True)
class PromotionProduct:
    product_id: int
    sku: str
    name: str
    stock: int
    cost_price: Decimal
    default_supplier_id: int | None


@dataclass
class ProcurementSignals:
    threshold_candidates: list[ThresholdProduct]
    velocity_candidates: list[VelocityProduct]
    promotion_candidates: list[PromotionProduct]
    warnings: list[str]


def _utc_now() -> datetime:
    return datetime.now(UTC)


async def fetch_procurement_signals(
    db: AsyncSession,
    *,
    sales_lookback_days: int,
    velocity_limit: int = 30,
) -> ProcurementSignals:
    warnings: list[str] = []
    now = _utc_now()
    start = now - timedelta(days=max(1, sales_lookback_days))

    thr_rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.stock,
                Product.low_stock_threshold,
                Product.cost_price,
                Product.default_supplier_id,
            ).where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.stock < Product.low_stock_threshold,
            ),
        )
    ).all()

    threshold_candidates: list[ThresholdProduct] = []
    for row in thr_rows:
        if row.default_supplier_id is None:
            warnings.append(
                f"SKU {row.sku} is below threshold but has no default supplier — skipped for auto PO",
            )
            continue
        threshold_candidates.append(
            ThresholdProduct(
                product_id=int(row.id),
                sku=row.sku,
                name=row.name,
                stock=int(row.stock),
                low_stock_threshold=int(row.low_stock_threshold),
                cost_price=Decimal(str(row.cost_price)),
                default_supplier_id=int(row.default_supplier_id)
                if row.default_supplier_id is not None
                else None,
            ),
        )

    vel_rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                func.coalesce(func.sum(SaleItem.quantity), 0),
                Product.stock,
                Product.cost_price,
                Product.default_supplier_id,
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(
                Sale.created_at >= start,
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
            )
            .group_by(
                Product.id,
                Product.sku,
                Product.name,
                Product.stock,
                Product.cost_price,
                Product.default_supplier_id,
            )
            .order_by(func.coalesce(func.sum(SaleItem.quantity), 0).desc())
            .limit(velocity_limit),
        )
    ).all()

    velocity_candidates: list[VelocityProduct] = []
    for row in vel_rows:
        qty_sold = int(row[3])
        if qty_sold <= 0:
            continue
        if row.default_supplier_id is None:
            warnings.append(
                f"SKU {row.sku} is popular in the window but has no default supplier — skipped for auto PO",
            )
            continue
        velocity_candidates.append(
            VelocityProduct(
                product_id=int(row.id),
                sku=row.sku,
                name=row.name,
                quantity_sold=qty_sold,
                stock=int(row.stock),
                cost_price=Decimal(str(row.cost_price)),
                default_supplier_id=int(row.default_supplier_id)
                if row.default_supplier_id is not None
                else None,
            ),
        )

    promo_rows = (
        await db.execute(
            select(
                Product.id,
                Product.sku,
                Product.name,
                Product.stock,
                Product.cost_price,
                Product.default_supplier_id,
            ).where(
                Product.lifecycle_status == ItemLifecycleStatus.ACTIVE,
                Product.promotion_reorder_boost.is_(True),
            ),
        )
    ).all()

    promotion_candidates: list[PromotionProduct] = []
    for row in promo_rows:
        if row.default_supplier_id is None:
            warnings.append(
                f"SKU {row.sku} is marked promotion boost but has no default supplier — skipped for auto PO",
            )
            continue
        promotion_candidates.append(
            PromotionProduct(
                product_id=int(row.id),
                sku=row.sku,
                name=row.name,
                stock=int(row.stock),
                cost_price=Decimal(str(row.cost_price)),
                default_supplier_id=int(row.default_supplier_id)
                if row.default_supplier_id is not None
                else None,
            ),
        )

    return ProcurementSignals(
        threshold_candidates=threshold_candidates,
        velocity_candidates=velocity_candidates,
        promotion_candidates=promotion_candidates,
        warnings=warnings,
    )
