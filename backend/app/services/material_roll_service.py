"""Business logic for fabric roll / lot tracking."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import (
    InventoryTransactionType,
    MaterialRollMovementType,
    MaterialRollStatus,
    StockQualityStatus,
)
from app.models.inventory_transaction import InventoryTransaction
from app.models.material_roll import (
    MaterialRoll,
    MaterialRollInspection,
    MaterialRollMovement,
)
from app.models.product import Product
from app.schemas.material_roll import (
    MaterialRollBulkReceiveIn,
    MaterialRollCreate,
    MaterialRollInspectionIn,
    MaterialRollIssueIn,
    MaterialRollQuarantineIn,
    MaterialRollReceiveIn,
    MaterialRollReturnIn,
    MaterialRollScanIn,
    MaterialRollTransferIn,
    MaterialRollUpdate,
    TraceabilityNode,
)


async def _next_roll_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"ROLL-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(MaterialRoll)
        .where(MaterialRoll.roll_number.like(f"{prefix}%")),
    )
    seq = int(result.scalar_one() or 0) + 1
    return f"{prefix}{seq:06d}"


def _rollup_integer_qty(remaining: Decimal, conversion_factor: Decimal | None) -> int:
    if conversion_factor and conversion_factor > 0:
        return int((remaining / conversion_factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return int(remaining.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


async def sync_product_stock_from_rolls(db: AsyncSession, product_id: int) -> None:
    """Recompute product.stock from sum of roll remaining quantities."""
    product = await db.get(Product, product_id)
    if product is None:
        return
    result = await db.execute(
        select(func.coalesce(func.sum(MaterialRoll.remaining_quantity), 0)).where(
            MaterialRoll.product_id == product_id,
            MaterialRoll.status.in_(
                [
                    MaterialRollStatus.IN_STOCK,
                    MaterialRollStatus.ALLOCATED,
                    MaterialRollStatus.ON_HOLD,
                ],
            ),
        ),
    )
    total_remaining = Decimal(str(result.scalar_one()))
    product.stock = max(0, _rollup_integer_qty(total_remaining, product.conversion_factor))


async def _record_movement(
    db: AsyncSession,
    *,
    roll: MaterialRoll,
    movement_type: MaterialRollMovementType,
    quantity_delta: Decimal,
    user_id: int | None,
    reference_type: str | None = None,
    reference_id: int | None = None,
    reference_document: str | None = None,
    remarks: str | None = None,
    from_warehouse_id: int | None = None,
    to_warehouse_id: int | None = None,
    from_location_id: int | None = None,
    to_location_id: int | None = None,
) -> MaterialRollMovement:
    movement = MaterialRollMovement(
        material_roll_id=roll.id,
        movement_type=movement_type,
        quantity_delta=quantity_delta,
        uom=roll.primary_uom,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        reference_type=reference_type,
        reference_id=reference_id,
        reference_document=reference_document,
        user_id=user_id,
        remarks=remarks,
    )
    db.add(movement)
    return movement


async def _inventory_txn_for_roll(
    db: AsyncSession,
    *,
    roll: MaterialRoll,
    product: Product,
    delta_int: int,
    transaction_type: InventoryTransactionType,
    reference_document: str | None,
    user_id: int | None,
    quantity_decimal: Decimal | None = None,
) -> None:
    if delta_int == 0:
        return
    txn = InventoryTransaction(
        product_id=product.id,
        transaction_type=transaction_type,
        quantity=abs(delta_int),
        quantity_decimal=quantity_decimal,
        material_roll_id=roll.id,
        reference_document=reference_document,
        user_id=user_id,
        lot_number=roll.roll_number,
    )
    db.add(txn)


async def receive_roll(
    db: AsyncSession,
    payload: MaterialRollReceiveIn | MaterialRollCreate,
    *,
    user_id: int | None,
) -> MaterialRoll:
    product = await db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    roll_number = getattr(payload, "roll_number", None) or await _next_roll_number(db)
    existing = await db.execute(
        select(MaterialRoll).where(MaterialRoll.roll_number == roll_number),
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Roll number already exists")

    barcode = payload.barcode or roll_number
    if barcode:
        dup = await db.execute(select(MaterialRoll).where(MaterialRoll.barcode == barcode))
        if dup.scalar_one_or_none():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Barcode already in use")

    qty = payload.initial_quantity
    unit_cost = payload.unit_cost or product.cost_price
    total_cost = (unit_cost or Decimal("0")) * qty if unit_cost else None

    roll = MaterialRoll(
        roll_number=roll_number,
        barcode=barcode,
        rfid_tag=payload.rfid_tag,
        serial_number=payload.serial_number,
        product_id=payload.product_id,
        material_type=payload.material_type,
        composition=payload.composition,
        color=payload.color or product.color,
        dye_lot=payload.dye_lot,
        pattern=payload.pattern,
        gsm=payload.gsm,
        width=payload.width or product.width,
        thickness=payload.thickness,
        grade=payload.grade,
        finish_type=payload.finish_type,
        initial_quantity=qty,
        remaining_quantity=qty,
        initial_weight_kg=payload.initial_weight_kg,
        remaining_weight_kg=payload.initial_weight_kg,
        primary_uom=payload.primary_uom,
        secondary_uom=payload.secondary_uom,
        conversion_factor=payload.conversion_factor or product.conversion_factor,
        supplier_id=payload.supplier_id,
        supplier_lot_number=payload.supplier_lot_number,
        purchase_id=getattr(payload, "purchase_id", None),
        purchase_item_id=getattr(payload, "purchase_item_id", None),
        po_number=payload.po_number,
        grn_reference=payload.grn_reference,
        invoice_number=payload.invoice_number,
        receipt_date=payload.receipt_date or date.today(),
        unit_cost=unit_cost,
        total_cost=total_cost,
        currency_code=payload.currency_code,
        manufacture_date=payload.manufacture_date,
        expiry_date=payload.expiry_date,
        status=MaterialRollStatus.IN_STOCK,
        warehouse_id=payload.warehouse_id or product.default_warehouse_id,
        location_id=payload.location_id or product.default_location_id,
        quality_status=payload.quality_status,
        inspection_passed=payload.inspection_passed,
        inspection_notes=payload.inspection_notes,
        certifications=payload.certifications,
        defect_log=payload.defect_log,
        shrinkage_test_data=payload.shrinkage_test_data,
        custom_attributes=payload.custom_attributes,
        attachments=payload.attachments,
    )
    db.add(roll)
    await db.flush()

    await _record_movement(
        db,
        roll=roll,
        movement_type=MaterialRollMovementType.RECEIPT,
        quantity_delta=qty,
        user_id=user_id,
        reference_type="purchase" if roll.purchase_id else "manual",
        reference_id=roll.purchase_id,
        reference_document=roll.grn_reference or f"ROLL-RECEIPT-{roll.roll_number}",
        to_warehouse_id=roll.warehouse_id,
        to_location_id=roll.location_id,
    )

    delta_int = _rollup_integer_qty(qty, roll.conversion_factor)
    product.stock = max(0, product.stock + delta_int)
    await _inventory_txn_for_roll(
        db,
        roll=roll,
        product=product,
        delta_int=delta_int,
        transaction_type=InventoryTransactionType.RECEIPT,
        reference_document=roll.grn_reference or f"ROLL-{roll.roll_number}",
        user_id=user_id,
        quantity_decimal=qty,
    )
    if product.roll_tracking_enabled is False and product.item_type.value == "RAW":
        product.roll_tracking_enabled = True

    await db.flush()
    return roll


async def bulk_receive_rolls(
    db: AsyncSession,
    payload: MaterialRollBulkReceiveIn,
    *,
    user_id: int | None,
) -> list[MaterialRoll]:
    rolls: list[MaterialRoll] = []
    for line in payload.lines:
        for _ in range(line.roll_count):
            receive = MaterialRollReceiveIn(
                product_id=line.product_id,
                initial_quantity=line.quantity_per_roll,
                primary_uom=line.primary_uom,
                dye_lot=line.dye_lot,
                color=line.color,
                supplier_lot_number=line.supplier_lot_number,
                warehouse_id=line.warehouse_id,
                location_id=line.location_id,
                unit_cost=line.unit_cost,
                supplier_id=payload.supplier_id,
                purchase_id=payload.purchase_id,
                grn_reference=payload.grn_reference,
                receipt_date=payload.receipt_date,
            )
            rolls.append(await receive_roll(db, receive, user_id=user_id))
    return rolls


async def get_roll(db: AsyncSession, roll_id: int, *, detail: bool = False) -> MaterialRoll | None:
    stmt = select(MaterialRoll).where(MaterialRoll.id == roll_id)
    if detail:
        stmt = stmt.options(
            selectinload(MaterialRoll.movements),
            selectinload(MaterialRoll.inspections),
            selectinload(MaterialRoll.allocations),
            selectinload(MaterialRoll.product),
        )
    else:
        stmt = stmt.options(selectinload(MaterialRoll.product))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_rolls(
    db: AsyncSession,
    *,
    product_id: int | None = None,
    status: MaterialRollStatus | None = None,
    warehouse_id: int | None = None,
    dye_lot: str | None = None,
    supplier_id: int | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[MaterialRoll], int]:
    stmt = select(MaterialRoll).options(selectinload(MaterialRoll.product))
    count_stmt = select(func.count()).select_from(MaterialRoll)

    if product_id is not None:
        stmt = stmt.where(MaterialRoll.product_id == product_id)
        count_stmt = count_stmt.where(MaterialRoll.product_id == product_id)
    if status is not None:
        stmt = stmt.where(MaterialRoll.status == status)
        count_stmt = count_stmt.where(MaterialRoll.status == status)
    if warehouse_id is not None:
        stmt = stmt.where(MaterialRoll.warehouse_id == warehouse_id)
        count_stmt = count_stmt.where(MaterialRoll.warehouse_id == warehouse_id)
    if dye_lot:
        stmt = stmt.where(MaterialRoll.dye_lot.ilike(f"%{dye_lot.strip()}%"))
        count_stmt = count_stmt.where(MaterialRoll.dye_lot.ilike(f"%{dye_lot.strip()}%"))
    if supplier_id is not None:
        stmt = stmt.where(MaterialRoll.supplier_id == supplier_id)
        count_stmt = count_stmt.where(MaterialRoll.supplier_id == supplier_id)
    if search:
        pattern = f"%{search.strip()}%"
        expr = or_(
            MaterialRoll.roll_number.ilike(pattern),
            MaterialRoll.barcode.ilike(pattern),
            MaterialRoll.rfid_tag.ilike(pattern),
            MaterialRoll.supplier_lot_number.ilike(pattern),
            MaterialRoll.dye_lot.ilike(pattern),
        )
        stmt = stmt.where(expr)
        count_stmt = count_stmt.where(expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(MaterialRoll.created_at.desc()).offset(skip).limit(limit),
    )
    return list(result.scalars().all()), total


async def update_roll(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollUpdate,
) -> MaterialRoll:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(roll, key, value)
    await db.flush()
    return roll


async def transfer_roll(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollTransferIn,
    *,
    user_id: int | None,
) -> MaterialRoll:
    from_wh = roll.warehouse_id
    from_loc = roll.location_id
    roll.warehouse_id = payload.to_warehouse_id
    roll.location_id = payload.to_location_id
    await _record_movement(
        db,
        roll=roll,
        movement_type=MaterialRollMovementType.TRANSFER,
        quantity_delta=Decimal("0"),
        user_id=user_id,
        remarks=payload.remarks,
        from_warehouse_id=from_wh,
        to_warehouse_id=payload.to_warehouse_id,
        from_location_id=from_loc,
        to_location_id=payload.to_location_id,
    )
    await db.flush()
    return roll


async def issue_roll_quantity(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollIssueIn,
    *,
    user_id: int | None,
    new_status: MaterialRollStatus = MaterialRollStatus.IN_PRODUCTION,
) -> MaterialRoll:
    if payload.quantity > roll.remaining_quantity:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient roll quantity: {roll.remaining_quantity} {roll.primary_uom} available",
        )
    product = await db.get(Product, roll.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    roll.remaining_quantity -= payload.quantity
    if roll.remaining_weight_kg and roll.initial_weight_kg and roll.initial_quantity > 0:
        ratio = payload.quantity / roll.initial_quantity
        roll.remaining_weight_kg = max(
            Decimal("0"),
            roll.remaining_weight_kg - (roll.initial_weight_kg * ratio),
        )

    if roll.remaining_quantity <= 0:
        roll.remaining_quantity = Decimal("0")
        roll.status = MaterialRollStatus.SHIPPED
    else:
        roll.status = new_status

    await _record_movement(
        db,
        roll=roll,
        movement_type=MaterialRollMovementType.ISSUE,
        quantity_delta=-payload.quantity,
        user_id=user_id,
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
        reference_document=payload.reference_document,
        remarks=payload.remarks,
        from_warehouse_id=roll.warehouse_id,
        from_location_id=roll.location_id,
    )

    delta_int = _rollup_integer_qty(payload.quantity, roll.conversion_factor)
    product.stock = max(0, product.stock - delta_int)
    await _inventory_txn_for_roll(
        db,
        roll=roll,
        product=product,
        delta_int=-delta_int,
        transaction_type=InventoryTransactionType.PRODUCTION_ISSUE,
        reference_document=payload.reference_document or f"ROLL-ISSUE-{roll.roll_number}",
        user_id=user_id,
        quantity_decimal=payload.quantity,
    )
    await db.flush()
    return roll


async def return_roll_quantity(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollReturnIn,
    *,
    user_id: int | None,
) -> MaterialRoll:
    product = await db.get(Product, roll.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    roll.remaining_quantity += payload.quantity
    roll.status = MaterialRollStatus.IN_STOCK

    await _record_movement(
        db,
        roll=roll,
        movement_type=MaterialRollMovementType.RETURN,
        quantity_delta=payload.quantity,
        user_id=user_id,
        remarks=payload.remarks,
        to_warehouse_id=roll.warehouse_id,
        to_location_id=roll.location_id,
    )

    delta_int = _rollup_integer_qty(payload.quantity, roll.conversion_factor)
    product.stock = max(0, product.stock + delta_int)
    await _inventory_txn_for_roll(
        db,
        roll=roll,
        product=product,
        delta_int=delta_int,
        transaction_type=InventoryTransactionType.ADJUSTMENT,
        reference_document=f"ROLL-RETURN-{roll.roll_number}",
        user_id=user_id,
        quantity_decimal=payload.quantity,
    )
    await db.flush()
    return roll


async def quarantine_roll(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollQuarantineIn,
    *,
    user_id: int | None,
) -> MaterialRoll:
    roll.status = payload.status
    roll.quality_status = payload.quality_status
    await _record_movement(
        db,
        roll=roll,
        movement_type=MaterialRollMovementType.QUARANTINE,
        quantity_delta=Decimal("0"),
        user_id=user_id,
        remarks=payload.remarks,
    )
    await db.flush()
    return roll


async def scan_roll(
    db: AsyncSession,
    payload: MaterialRollScanIn,
    *,
    user_id: int | None,
) -> MaterialRoll:
    stmt = select(MaterialRoll).options(selectinload(MaterialRoll.product))
    if payload.barcode:
        stmt = stmt.where(MaterialRoll.barcode == payload.barcode.strip())
    elif payload.rfid_tag:
        stmt = stmt.where(MaterialRoll.rfid_tag == payload.rfid_tag.strip())
    else:
        stmt = stmt.where(MaterialRoll.roll_number == payload.roll_number.strip())

    result = await db.execute(stmt)
    roll = result.scalar_one_or_none()
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")

    roll.last_scanned_at = datetime.now(timezone.utc)
    roll.last_scanned_by_id = user_id
    await db.flush()
    return roll


async def add_inspection(
    db: AsyncSession,
    roll: MaterialRoll,
    payload: MaterialRollInspectionIn,
    *,
    user_id: int | None,
) -> MaterialRollInspection:
    inspection = MaterialRollInspection(
        material_roll_id=roll.id,
        inspector_name=payload.inspector_name,
        inspected_by_id=user_id,
        passed=payload.passed,
        test_parameters=payload.test_parameters,
        notes=payload.notes,
    )
    db.add(inspection)
    roll.inspection_passed = payload.passed
    if payload.notes:
        roll.inspection_notes = payload.notes
    await db.flush()
    return inspection


async def get_traceability(db: AsyncSession, roll: MaterialRoll) -> tuple[list[TraceabilityNode], list[TraceabilityNode]]:
    backward: list[TraceabilityNode] = []
    forward: list[TraceabilityNode] = []

    if roll.supplier_id:
        backward.append(
            TraceabilityNode(
                node_type="supplier",
                reference_id=roll.supplier_id,
                label="Supplier",
                detail=roll.supplier_lot_number,
            ),
        )
    if roll.purchase_id:
        backward.append(
            TraceabilityNode(
                node_type="purchase",
                reference_id=roll.purchase_id,
                label=f"PO / Purchase #{roll.purchase_id}",
                detail=roll.po_number or roll.grn_reference,
            ),
        )
    backward.append(
        TraceabilityNode(
            node_type="receipt",
            reference_id=roll.id,
            label=f"Roll receipt {roll.roll_number}",
            detail=str(roll.receipt_date),
        ),
    )

    movements = (
        await db.execute(
            select(MaterialRollMovement)
            .where(MaterialRollMovement.material_roll_id == roll.id)
            .where(MaterialRollMovement.movement_type == MaterialRollMovementType.ISSUE)
            .order_by(MaterialRollMovement.transaction_at),
        )
    ).scalars().all()

    for mv in movements:
        forward.append(
            TraceabilityNode(
                node_type=mv.reference_type or "issue",
                reference_id=mv.reference_id,
                label=mv.reference_document or mv.movement_type.value,
                detail=f"{abs(mv.quantity_delta)} {mv.uom}",
            ),
        )

    return backward, forward


def build_label_html(roll: MaterialRoll, product: Product) -> str:
    from app.core.html_escape import escape_html
    from app.core.html_sanitize import sanitize_html

    # Security: escape all DB-backed fields — labels are HTML and may be printed in the browser.
    roll_no = escape_html(roll.roll_number)
    barcode = escape_html(roll.barcode or roll.roll_number)
    sku = escape_html(product.sku)
    material = escape_html(product.name)
    color = escape_html(roll.color) if roll.color else "—"
    dye_lot = escape_html(roll.dye_lot) if roll.dye_lot else "—"
    qty = escape_html(roll.remaining_quantity)
    uom = escape_html(roll.primary_uom)
    raw_html = f"""<!DOCTYPE html>
<html><head><title>Roll {roll_no}</title>
<style>
body {{ font-family: sans-serif; padding: 12px; width: 280px; }}
h1 {{ font-size: 14px; margin: 0 0 8px; }}
.row {{ font-size: 11px; margin: 2px 0; }}
.barcode {{ font-family: monospace; font-size: 16px; letter-spacing: 2px; margin-top: 8px; }}
</style></head><body>
<h1>{roll_no}</h1>
<div class="row"><b>SKU:</b> {sku}</div>
<div class="row"><b>Material:</b> {material}</div>
<div class="row"><b>Color:</b> {color}</div>
<div class="row"><b>Dye lot:</b> {dye_lot}</div>
<div class="row"><b>Qty:</b> {qty} {uom}</div>
<div class="barcode">*{barcode}*</div>
</body></html>"""
    return sanitize_html(raw_html)
