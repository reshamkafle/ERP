from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.sale import SaleItem
from app.schemas.inventory import InventoryAnalyticsRead


async def compute_product_analytics(db: AsyncSession, product: Product) -> InventoryAnalyticsRead:
    cost = product.cost_price or Decimal("0")
    stock_value = cost * Decimal(product.stock)

    sales_result = await db.execute(
        select(func.coalesce(func.sum(SaleItem.quantity), 0)).where(
            SaleItem.product_id == product.id,
        ),
    )
    qty_sold = int(sales_result.scalar_one() or 0)
    turnover = (
        Decimal(qty_sold) / Decimal(product.stock)
        if product.stock > 0
        else Decimal("0")
    )

    dead_value = Decimal("0")
    if product.xyz_class and product.xyz_class.value == "NON_MOVING":
        dead_value = stock_value

    holding = stock_value * Decimal("0.02")

    return InventoryAnalyticsRead(
        turnover_ratio=turnover.quantize(Decimal("0.0001")),
        inventory_accuracy_pct=Decimal("100"),
        stock_value=stock_value.quantize(Decimal("0.01")),
        dead_stock_value=dead_value.quantize(Decimal("0.01")),
        inventory_holding_cost=holding.quantize(Decimal("0.01")),
    )
