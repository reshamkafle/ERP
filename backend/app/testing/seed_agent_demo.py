"""Idempotent demo data for procurement and promotion agent testing."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.enums import ItemLifecycleStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.supplier import Supplier

DEMO_SKU_ANCHOR = "AGENT-DEMO-ANCHOR"
DEMO_SKU_REL = "AGENT-DEMO-REL"
DEMO_SKU_LOW = "AGENT-DEMO-LOW"
DEMO_SKU_FAST = "AGENT-DEMO-FAST"
DEMO_SKU_PROMO = "AGENT-DEMO-PROMO"
DEMO_CATEGORY = "Agent Demo"
DEMO_SUPPLIER = "Agent Demo Supplier"

DEMO_SKUS = (
    DEMO_SKU_ANCHOR,
    DEMO_SKU_REL,
    DEMO_SKU_LOW,
    DEMO_SKU_FAST,
    DEMO_SKU_PROMO,
)


def ensure_procurement_run_enum_sync() -> None:
    """Add IN_PROGRESS to procurementrunstatus (sync; safe outside asyncio loops)."""
    try:
        import psycopg2

        from app.core.config import get_settings

        dsn = get_settings().database_url.replace("postgresql+asyncpg://", "postgresql://")
        with psycopg2.connect(dsn) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(
                    "ALTER TYPE procurementrunstatus ADD VALUE IF NOT EXISTS 'IN_PROGRESS'",
                )
    except Exception:
        pass


async def seed_agent_demo_data(db: AsyncSession) -> dict[str, int | str]:
    """Insert supplier, category, products, and co-purchase sales if not present."""
    existing = await db.scalar(select(Product.id).where(Product.sku == DEMO_SKU_ANCHOR))
    if existing is not None:
        return {"skipped": True, "reason": "demo products already exist"}

    cat_row = (await db.execute(select(Category).where(Category.name == DEMO_CATEGORY))).scalar_one_or_none()
    if cat_row is None:
        cat_row = Category(name=DEMO_CATEGORY)
        db.add(cat_row)
        await db.flush()

    sup_row = (
        await db.execute(select(Supplier).where(Supplier.name == DEMO_SUPPLIER))
    ).scalar_one_or_none()
    if sup_row is None:
        sup_row = Supplier(name=DEMO_SUPPLIER, email="agent-demo@example.com")
        db.add(sup_row)
        await db.flush()

    def add_product(
        *,
        sku: str,
        name: str,
        stock: int,
        price: str,
        cost: str,
        low: int = 5,
        promo_boost: bool = False,
    ) -> Product:
        p = Product(
            sku=sku,
            name=name,
            price=Decimal(price),
            cost_price=Decimal(cost),
            stock=stock,
            low_stock_threshold=low,
            category_id=cat_row.id,
            default_supplier_id=sup_row.id,
            lifecycle_status=ItemLifecycleStatus.ACTIVE,
            promotion_reorder_boost=promo_boost,
            product_line="AgentDemo",
        )
        db.add(p)
        return p

    anchor = add_product(
        sku=DEMO_SKU_ANCHOR,
        name="Agent Demo Anchor",
        stock=30,
        price="24.99",
        cost="10.00",
        low=5,
    )
    related = add_product(
        sku=DEMO_SKU_REL,
        name="Agent Demo Related",
        stock=40,
        price="9.99",
        cost="4.00",
        low=5,
    )
    low_stock = add_product(
        sku=DEMO_SKU_LOW,
        name="Agent Demo Low Stock",
        stock=2,
        price="14.99",
        cost="6.00",
        low=10,
    )
    fast = add_product(
        sku=DEMO_SKU_FAST,
        name="Agent Demo Fast Mover",
        stock=25,
        price="19.99",
        cost="8.00",
        low=5,
    )
    promo = add_product(
        sku=DEMO_SKU_PROMO,
        name="Agent Demo Promo Boost",
        stock=6,
        price="11.99",
        cost="5.00",
        low=5,
        promo_boost=True,
    )
    await db.flush()

    now = datetime.now(UTC)
    for day_offset in (1, 3, 7):
        sale = Sale(created_at=now - timedelta(days=day_offset))
        db.add(sale)
        await db.flush()
        db.add(
            SaleItem(
                sale_id=sale.id,
                product_id=anchor.id,
                quantity=3,
                price_at_sale=anchor.price,
            ),
        )
        db.add(
            SaleItem(
                sale_id=sale.id,
                product_id=related.id,
                quantity=2,
                price_at_sale=related.price,
            ),
        )
        db.add(
            SaleItem(
                sale_id=sale.id,
                product_id=fast.id,
                quantity=5,
                price_at_sale=fast.price,
            ),
        )

    return {
        "skipped": False,
        "supplier_id": sup_row.id,
        "category_id": cat_row.id,
        "product_ids": [anchor.id, related.id, low_stock.id, fast.id, promo.id],
    }
