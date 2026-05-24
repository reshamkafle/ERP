"""Production order lifecycle: release, confirm, close."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import manufacturing_ops as mfg_crud
from app.manufacturing.bom.service import BOMService
from app.manufacturing.bom.sql_repository import SqlBOMRepository
from app.models.enums import MaterialIssueMethod, ProductionOrderStatus
from app.models.manufacturing import ManufacturingItem
from app.models.manufacturing_ops import (
    ProductionConfirmation,
    ProductionOrder,
    ProductionOrderCost,
    ShopFloorEntry,
)
from app.models.product import Product
from app.schemas.manufacturing import (
    MaterialIssueIn,
    ProductionConfirmationIn,
    ShopFloorEntryIn,
)
from app.services.manufacturing_inventory import (
    issue_material_for_po,
    receive_finished_goods,
    reserve_for_production_order,
)
from app.services.production_costing import accumulate_confirmation_cost, close_order_costing


async def release_production_order(db: AsyncSession, po: ProductionOrder) -> ProductionOrder:
    if po.status != ProductionOrderStatus.PLANNED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Only PLANNED orders can be released")
    try:
        await reserve_for_production_order(db, po)
    except HTTPException:
        pass  # reservation optional when no warehouse
    po.status = ProductionOrderStatus.RELEASED
    await db.flush()
    return po


async def start_production_order(db: AsyncSession, po: ProductionOrder) -> ProductionOrder:
    if po.status not in (ProductionOrderStatus.RELEASED, ProductionOrderStatus.PLANNED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid status for start")
    po.status = ProductionOrderStatus.IN_PROGRESS
    if not po.start_date:
        po.start_date = datetime.now(timezone.utc).date()
    await db.flush()
    return po


async def issue_material(
    db: AsyncSession,
    po: ProductionOrder,
    payload: MaterialIssueIn,
    user_id: int | None,
) -> ProductionOrder:
    if po.status not in (
        ProductionOrderStatus.RELEASED,
        ProductionOrderStatus.IN_PROGRESS,
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Order not open for issuing")
    if po.contract_id:
        from app.services.cmt_service import record_cmt_consumption, validate_cmt_material_issue

        await validate_cmt_material_issue(
            db, po.contract_id, payload.component_item_id, payload.quantity
        )
    comp_item = await db.get(ManufacturingItem, payload.component_item_id)
    if comp_item is None or comp_item.product_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Component not linked to product")
    product = await db.get(Product, comp_item.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    wh_id = payload.warehouse_id or po.wip_warehouse_id or po.warehouse_id
    if wh_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Warehouse required for issue")
    await issue_material_for_po(
        db,
        po=po,
        component_product=product,
        quantity=payload.quantity,
        warehouse_id=wh_id,
        user_id=user_id,
        lot_number=payload.lot_number,
        serial_number=payload.serial_number,
        issue_method=payload.issue_method,
        material_roll_id=payload.material_roll_id,
    )
    db.add(
        ProductionOrderCost(
            production_order_id=po.id,
            cost_type="MATERIAL",
            amount=payload.quantity * (product.cost_price or Decimal("0")),
        ),
    )
    if po.contract_id:
        from app.services.cmt_service import record_cmt_consumption

        await record_cmt_consumption(db, po.contract_id, payload.component_item_id, payload.quantity)
    await db.flush()
    return po


async def _backflush_components(
    db: AsyncSession,
    po: ProductionOrder,
    qty_confirmed: Decimal,
    user_id: int | None,
) -> None:
    if po.bom_parent_item_id is None:
        return
    parent = await db.get(ManufacturingItem, po.bom_parent_item_id)
    if parent is None:
        return
    svc = BOMService(SqlBOMRepository(db))
    try:
        explosion = await svc.explode_bom(parent.sku, order_quantity=int(qty_confirmed))
    except Exception:
        return
    wh_id = po.wip_warehouse_id or po.warehouse_id
    if wh_id is None:
        return
    for line in explosion.lines:
        comp = await db.get(ManufacturingItem, line.item_id)
        if comp is None or comp.product_id is None:
            continue
        product = await db.get(Product, comp.product_id)
        if product is None:
            continue
        issue_qty = line.total_qty
        if issue_qty <= 0:
            continue
        await issue_material_for_po(
            db,
            po=po,
            component_product=product,
            quantity=issue_qty,
            warehouse_id=wh_id,
            user_id=user_id,
            lot_number=None,
            serial_number=None,
            issue_method=MaterialIssueMethod.BACKFLUSH,
        )


async def confirm_production(
    db: AsyncSession,
    po: ProductionOrder,
    payload: ProductionConfirmationIn,
    user_id: int | None,
) -> ProductionOrder:
    if po.status not in (
        ProductionOrderStatus.RELEASED,
        ProductionOrderStatus.IN_PROGRESS,
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Order not open for confirmation")
    if po.status == ProductionOrderStatus.RELEASED:
        po.status = ProductionOrderStatus.IN_PROGRESS

    conf = ProductionConfirmation(
        production_order_id=po.id,
        operation_id=payload.operation_id,
        quantity_completed=payload.quantity_completed,
        quantity_rejected=payload.quantity_rejected,
        quantity_rework=payload.quantity_rework,
        confirmed_by_id=user_id,
        notes=payload.notes,
    )
    db.add(conf)
    po.quantity_completed += payload.quantity_completed
    po.quantity_scrapped += payload.quantity_rejected
    po.quantity_rework += payload.quantity_rework

    if payload.backflush and payload.quantity_completed > 0:
        await _backflush_components(db, po, payload.quantity_completed, user_id)

    if payload.quantity_completed > 0:
        await receive_finished_goods(
            db, po=po, quantity=payload.quantity_completed, user_id=user_id
        )

    await accumulate_confirmation_cost(db, po, payload)
    await db.flush()
    return po


async def record_shop_floor(
    db: AsyncSession,
    po: ProductionOrder,
    payload: ShopFloorEntryIn,
    user_id: int | None,
) -> ShopFloorEntry:
    entry = ShopFloorEntry(
        production_order_id=po.id,
        operation_id=payload.operation_id,
        actual_time_minutes=payload.actual_time_minutes,
        output_quantity=payload.output_quantity,
        scrap_quantity=payload.scrap_quantity,
        downtime_minutes=payload.downtime_minutes,
        downtime_reason=payload.downtime_reason,
        recorded_by_id=user_id,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def complete_production_order(db: AsyncSession, po: ProductionOrder) -> ProductionOrder:
    if po.status != ProductionOrderStatus.IN_PROGRESS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Order must be IN_PROGRESS")
    po.status = ProductionOrderStatus.COMPLETED
    po.end_date = datetime.now(timezone.utc).date()
    await db.flush()
    return po


async def close_production_order(
    db: AsyncSession, po: ProductionOrder, user_id: int | None
) -> ProductionOrder:
    if po.status not in (ProductionOrderStatus.COMPLETED, ProductionOrderStatus.IN_PROGRESS):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Order must be completed first")
    await close_order_costing(db, po, user_id)
    po.status = ProductionOrderStatus.CLOSED
    await db.flush()
    return po
