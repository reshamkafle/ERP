from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.enums import MaterialRollStatus
from app.models.user import User
from app.schemas.material_roll import (
    MaterialRollAllocationRead,
    MaterialRollBulkReceiveIn,
    MaterialRollCreate,
    MaterialRollDetailRead,
    MaterialRollInspectionIn,
    MaterialRollInspectionRead,
    MaterialRollIssueIn,
    MaterialRollLabelRead,
    MaterialRollListResponse,
    MaterialRollMovementRead,
    MaterialRollQuarantineIn,
    MaterialRollRead,
    MaterialRollReceiveIn,
    MaterialRollReturnIn,
    MaterialRollScanIn,
    MaterialRollScanRead,
    MaterialRollTraceabilityRead,
    MaterialRollTransferIn,
    MaterialRollUpdate,
    PurchaseReceiveRollsIn,
)
from app.services import material_roll_service as roll_svc

router = APIRouter(prefix="/material-rolls")

RollReadPerm = require_permission("warehouse.material_rolls.read")
RollWritePerm = require_permission("warehouse.material_rolls.write")


def _roll_read(roll) -> MaterialRollRead:
    data = MaterialRollRead.model_validate(roll)
    if roll.product:
        return data.model_copy(
            update={
                "product_sku": roll.product.sku,
                "product_name": roll.product.name,
            },
        )
    return data


@router.get("", response_model=MaterialRollListResponse)
async def list_material_rolls(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollReadPerm)],
    product_id: int | None = None,
    status: MaterialRollStatus | None = None,
    warehouse_id: int | None = None,
    dye_lot: str | None = None,
    supplier_id: int | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> MaterialRollListResponse:
    rolls, total = await roll_svc.list_rolls(
        db,
        product_id=product_id,
        status=status,
        warehouse_id=warehouse_id,
        dye_lot=dye_lot,
        supplier_id=supplier_id,
        search=search,
        skip=skip,
        limit=limit,
    )
    return MaterialRollListResponse(
        items=[_roll_read(r) for r in rolls],
        total=total,
    )


@router.post("", response_model=MaterialRollRead, status_code=status.HTTP_201_CREATED)
async def create_material_roll(
    body: MaterialRollCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.receive_roll(db, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll.id)
    return _roll_read(roll)


@router.post("/receive", response_model=MaterialRollRead, status_code=status.HTTP_201_CREATED)
async def receive_material_roll(
    body: MaterialRollReceiveIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.receive_roll(db, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll.id)
    return _roll_read(roll)


@router.post("/bulk-receive", response_model=MaterialRollListResponse)
async def bulk_receive_material_rolls(
    body: MaterialRollBulkReceiveIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollListResponse:
    rolls = await roll_svc.bulk_receive_rolls(db, body, user_id=user.id)
    await db.commit()
    items = []
    for r in rolls:
        loaded = await roll_svc.get_roll(db, r.id)
        items.append(_roll_read(loaded))
    return MaterialRollListResponse(items=items, total=len(items))


@router.post("/purchase-receive", response_model=MaterialRollListResponse)
async def receive_rolls_from_purchase(
    body: PurchaseReceiveRollsIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollListResponse:
    from app.models.purchase import Purchase

    purchase = await db.get(Purchase, body.purchase_id)
    if purchase is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Purchase not found")

    bulk = MaterialRollBulkReceiveIn(
        lines=body.lines,
        purchase_id=body.purchase_id,
        supplier_id=purchase.supplier_id,
        grn_reference=body.grn_reference,
    )
    rolls = await roll_svc.bulk_receive_rolls(db, bulk, user_id=user.id)
    await db.commit()
    items = []
    for r in rolls:
        loaded = await roll_svc.get_roll(db, r.id)
        items.append(_roll_read(loaded))
    return MaterialRollListResponse(items=items, total=len(items))


@router.post("/scan", response_model=MaterialRollScanRead)
async def scan_material_roll(
    body: MaterialRollScanIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollReadPerm)],
) -> MaterialRollScanRead:
    roll = await roll_svc.scan_roll(db, body, user_id=user.id)
    await db.commit()
    if roll.product is None:
        roll = await roll_svc.get_roll(db, roll.id)
    return MaterialRollScanRead(
        roll=_roll_read(roll),
        product_sku=roll.product.sku,
        product_name=roll.product.name,
    )


@router.get("/{roll_id}", response_model=MaterialRollDetailRead)
async def get_material_roll(
    roll_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollReadPerm)],
) -> MaterialRollDetailRead:
    roll = await roll_svc.get_roll(db, roll_id, detail=True)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    base = _roll_read(roll)
    return MaterialRollDetailRead(
        **base.model_dump(),
        movements=[MaterialRollMovementRead.model_validate(m) for m in roll.movements],
        inspections=[MaterialRollInspectionRead.model_validate(i) for i in roll.inspections],
        allocations=[MaterialRollAllocationRead.model_validate(a) for a in roll.allocations],
    )


@router.patch("/{roll_id}", response_model=MaterialRollRead)
async def update_material_roll(
    roll_id: int,
    body: MaterialRollUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    roll = await roll_svc.update_roll(db, roll, body)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll_id)
    return _roll_read(roll)


@router.post("/{roll_id}/transfer", response_model=MaterialRollRead)
async def transfer_material_roll(
    roll_id: int,
    body: MaterialRollTransferIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    roll = await roll_svc.transfer_roll(db, roll, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll_id)
    return _roll_read(roll)


@router.post("/{roll_id}/issue", response_model=MaterialRollRead)
async def issue_material_roll(
    roll_id: int,
    body: MaterialRollIssueIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    roll = await roll_svc.issue_roll_quantity(db, roll, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll_id)
    return _roll_read(roll)


@router.post("/{roll_id}/return", response_model=MaterialRollRead)
async def return_material_roll(
    roll_id: int,
    body: MaterialRollReturnIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    roll = await roll_svc.return_roll_quantity(db, roll, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll_id)
    return _roll_read(roll)


@router.post("/{roll_id}/quarantine", response_model=MaterialRollRead)
async def quarantine_material_roll(
    roll_id: int,
    body: MaterialRollQuarantineIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    roll = await roll_svc.quarantine_roll(db, roll, body, user_id=user.id)
    await db.commit()
    roll = await roll_svc.get_roll(db, roll_id)
    return _roll_read(roll)


@router.post("/{roll_id}/inspections", response_model=MaterialRollInspectionRead)
async def add_roll_inspection(
    roll_id: int,
    body: MaterialRollInspectionIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(RollWritePerm)],
) -> MaterialRollInspectionRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    inspection = await roll_svc.add_inspection(db, roll, body, user_id=user.id)
    await db.commit()
    return MaterialRollInspectionRead.model_validate(inspection)


@router.get("/{roll_id}/traceability", response_model=MaterialRollTraceabilityRead)
async def roll_traceability(
    roll_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollReadPerm)],
) -> MaterialRollTraceabilityRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    backward, forward = await roll_svc.get_traceability(db, roll)
    return MaterialRollTraceabilityRead(
        roll_id=roll.id,
        roll_number=roll.roll_number,
        backward=backward,
        forward=forward,
    )


@router.get("/{roll_id}/label", response_model=MaterialRollLabelRead)
async def roll_label(
    roll_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollReadPerm)],
) -> MaterialRollLabelRead:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    if roll.product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    html = roll_svc.build_label_html(roll, roll.product)
    return MaterialRollLabelRead(
        roll_number=roll.roll_number,
        barcode=roll.barcode or roll.roll_number,
        product_sku=roll.product.sku,
        product_name=roll.product.name,
        color=roll.color,
        dye_lot=roll.dye_lot,
        remaining_quantity=roll.remaining_quantity,
        primary_uom=roll.primary_uom,
        html=html,
    )


@router.get("/{roll_id}/label/print")
async def roll_label_print(
    roll_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(RollReadPerm)],
) -> Response:
    roll = await roll_svc.get_roll(db, roll_id)
    if roll is None or roll.product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Roll not found")
    html = roll_svc.build_label_html(roll, roll.product)
    return Response(content=html, media_type="text/html")
