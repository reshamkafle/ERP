"""Warehouse-aware inventory movements for production orders."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import InventoryTransactionType, StockQualityStatus
from app.models.inventory_transaction import InventoryTransaction
from app.models.manufacturing_ops import ProductionMaterialIssue, ProductionOrder
from app.models.product import Product
from app.models.stock_balance import StockBalance


async def _get_or_create_balance(
    db: AsyncSession,
    *,
    product_id: int,
    warehouse_id: int,
    location_id: int | None = None,
    lot_number: str | None = None,
) -> StockBalance:
    q = select(StockBalance).where(
        StockBalance.product_id == product_id,
        StockBalance.warehouse_id == warehouse_id,
    )
    if location_id is not None:
        q = q.where(StockBalance.location_id == location_id)
    else:
        q = q.where(StockBalance.location_id.is_(None))
    if lot_number is not None:
        q = q.where(StockBalance.lot_number == lot_number)
    else:
        q = q.where(StockBalance.lot_number.is_(None))
    result = await db.execute(q)
    bal = result.scalar_one_or_none()
    if bal is None:
        bal = StockBalance(
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            lot_number=lot_number,
            on_hand=0,
            available=0,
            reserved=0,
            quality_status=StockQualityStatus.APPROVED,
        )
        db.add(bal)
        await db.flush()
    return bal


async def adjust_stock_balance(
    db: AsyncSession,
    *,
    product: Product,
    warehouse_id: int,
    location_id: int | None,
    delta: int,
    transaction_type: InventoryTransactionType,
    reference_document: str | None = None,
    user_id: int | None = None,
    lot_number: str | None = None,
    serial_number: str | None = None,
    unit_cost: Decimal | None = None,
) -> None:
    bal = await _get_or_create_balance(
        db,
        product_id=product.id,
        warehouse_id=warehouse_id,
        location_id=location_id,
        lot_number=lot_number,
    )
    new_on_hand = bal.on_hand + delta
    if new_on_hand < 0:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product {product.sku} in warehouse {warehouse_id}",
        )
    bal.on_hand = new_on_hand
    bal.available = max(0, bal.available + delta)
    product.stock = max(0, product.stock + delta)

    txn = InventoryTransaction(
        product_id=product.id,
        transaction_type=transaction_type,
        quantity=abs(delta),
        from_warehouse_id=warehouse_id if delta < 0 else None,
        to_warehouse_id=warehouse_id if delta > 0 else None,
        from_location_id=location_id if delta < 0 else None,
        to_location_id=location_id if delta > 0 else None,
        reference_document=reference_document,
        user_id=user_id,
        lot_number=lot_number,
        serial_number=serial_number,
        unit_cost=unit_cost or product.cost_price,
    )
    db.add(txn)


async def reserve_for_production_order(db: AsyncSession, po: ProductionOrder) -> None:
    """Reserve FG/components — simplified: bump reserved on default warehouse balance."""
    if po.warehouse_id is None:
        return
    product = await db.get(Product, po.product_id)
    if product is None:
        return
    bal = await _get_or_create_balance(
        db, product_id=product.id, warehouse_id=po.warehouse_id
    )
    qty = int(po.quantity_planned)
    if bal.available < qty:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Insufficient available stock to reserve for production",
        )
    bal.reserved += qty
    bal.available -= qty


async def issue_material_for_po(
    db: AsyncSession,
    *,
    po: ProductionOrder,
    component_product: Product,
    quantity: Decimal,
    warehouse_id: int,
    user_id: int | None,
    lot_number: str | None,
    serial_number: str | None,
    issue_method,
    material_roll_id: int | None = None,
) -> ProductionMaterialIssue:
    if component_product.roll_tracking_enabled:
        if material_roll_id is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Material roll required for roll-tracked fabric",
            )
        from app.models.material_roll import MaterialRoll
        from app.schemas.material_roll import MaterialRollIssueIn
        from app.services import material_roll_service as roll_svc

        roll = await db.get(MaterialRoll, material_roll_id)
        if roll is None or roll.product_id != component_product.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid material roll")
        await roll_svc.issue_roll_quantity(
            db,
            roll,
            MaterialRollIssueIn(
                quantity=quantity,
                reference_type="production_order",
                reference_id=po.id,
                reference_document=po.order_number,
            ),
            user_id=user_id,
        )
        lot_number = roll.roll_number
    elif component_product.batch_lot_flag and not lot_number:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Lot number required")
    if component_product.serial_number_flag and not serial_number:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Serial number required")

    if not component_product.roll_tracking_enabled:
        qty_int = int(quantity)
        await adjust_stock_balance(
            db,
            product=component_product,
            warehouse_id=warehouse_id,
            location_id=None,
            delta=-qty_int,
            transaction_type=InventoryTransactionType.PRODUCTION_ISSUE,
            reference_document=po.order_number,
            user_id=user_id,
            lot_number=lot_number,
            serial_number=serial_number,
        )
    from app.models.manufacturing import ManufacturingItem

    mfg_item = (
        await db.execute(
            select(ManufacturingItem).where(
                ManufacturingItem.product_id == component_product.id,
            ),
        )
    ).scalar_one_or_none()
    if mfg_item is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Component has no manufacturing item")

    issue = ProductionMaterialIssue(
        production_order_id=po.id,
        component_item_id=mfg_item.id,
        quantity=quantity,
        issue_method=issue_method,
        lot_number=lot_number,
        serial_number=serial_number,
        material_roll_id=material_roll_id,
        warehouse_id=warehouse_id,
        issued_by_id=user_id,
    )
    db.add(issue)
    await db.flush()
    return issue


async def receive_finished_goods(
    db: AsyncSession,
    *,
    po: ProductionOrder,
    quantity: Decimal,
    user_id: int | None,
) -> None:
    if po.warehouse_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="FG warehouse required")
    product = await db.get(Product, po.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    qty_int = int(quantity)
    await adjust_stock_balance(
        db,
        product=product,
        warehouse_id=po.warehouse_id,
        location_id=None,
        delta=qty_int,
        transaction_type=InventoryTransactionType.PRODUCTION_RECEIPT,
        reference_document=po.order_number,
        user_id=user_id,
    )
