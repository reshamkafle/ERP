from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import InventoryTransactionType
from app.models.inventory_transaction import InventoryTransaction
from app.models.product import Product
from app.models.stock_balance import StockBalance


async def record_stock_movement(
    db: AsyncSession,
    *,
    product: Product,
    transaction_type: InventoryTransactionType,
    quantity: int,
    reference_document: str | None = None,
    user_id: int | None = None,
    unit_cost: Decimal | None = None,
    remarks: str | None = None,
) -> InventoryTransaction:
    txn = InventoryTransaction(
        product_id=product.id,
        transaction_type=transaction_type,
        transaction_at=datetime.now(timezone.utc),
        reference_document=reference_document,
        quantity=quantity,
        unit_cost=unit_cost or product.cost_price,
        user_id=user_id,
        remarks=remarks,
    )
    db.add(txn)
    return txn


async def adjust_product_stock(
    db: AsyncSession,
    product: Product,
    delta: int,
    *,
    transaction_type: InventoryTransactionType,
    reference_document: str | None = None,
    user_id: int | None = None,
) -> None:
    product.stock = max(0, product.stock + delta)
    await record_stock_movement(
        db,
        product=product,
        transaction_type=transaction_type,
        quantity=abs(delta),
        reference_document=reference_document,
        user_id=user_id,
    )
