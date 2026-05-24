from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bom as bom_crud
from app.dependencies.auth import require_permission
from app.dependencies.bom import get_bom_service
from app.core.database import get_db
from app.manufacturing.bom.exceptions import BOMError, BOMNotFoundError, ItemNotFoundError
from app.manufacturing.bom.models import BOM
from app.manufacturing.bom.product_snapshot import product_snapshot_from_row
from app.manufacturing.bom.service import BOMService
from app.models.user import User
from app.schemas.bom_api import (
    AddBOMResponse,
    BOMAlternateCreate,
    BOMAlternateRead,
    BOMLineRead,
    BOMListResponse,
    BOMRead,
    BOMSubstituteCreate,
    BOMSubstituteRead,
    BOMSummaryRead,
    BOMTreeResponse,
    ExplosionResponse,
    FabricSummaryResponse,
    ItemListResponse,
    ItemRead,
    SaveBOMRequest,
    TrimSummaryResponse,
    UpdateBOMStatusRequest,
)

router = APIRouter(prefix="/bom")

BOMReadRoles = require_permission("warehouse.bom.read")
BOMWriteRoles = require_permission("warehouse.bom.write")


async def _bom_to_read_async(
    bom: BOM,
    svc: BOMService,
    db: AsyncSession,
) -> BOMRead:
    parent_row = await bom_crud.get_mfg_item_with_product(db, bom.parent_item_id)
    parent_item = await svc._repo.get_item_by_id(bom.parent_item_id)
    parent_snapshot = product_snapshot_from_row(parent_row)
    parent_description = parent_snapshot.description if parent_snapshot else None

    db_lines = await bom_crud.list_bom_lines_with_substitutes(db, bom.parent_item_id)
    db_line_by_sequence = {ln.line_sequence: ln for ln in db_lines}

    lines: list[BOMLineRead] = []
    for line in sorted(bom.lines, key=lambda ln: ln.line_sequence):
        comp = await svc._repo.get_item_by_id(line.component_item_id)
        if comp is None:
            continue
        comp_row = await bom_crud.get_mfg_item_with_product(db, line.component_item_id)
        db_line = db_line_by_sequence.get(line.line_sequence)
        substitutes: list[BOMSubstituteRead] = []
        if db_line is not None:
            for sub in sorted(db_line.substitutes, key=lambda s: s.priority):
                sub_item = sub.substitute_item
                substitutes.append(
                    BOMSubstituteRead(
                        id=sub.id,
                        substitute_item_id=sub.substitute_item_id,
                        substitute_sku=sub_item.sku if sub_item else "",
                        substitute_name=sub_item.name if sub_item else "",
                        substitute_quantity=sub.substitute_quantity,
                        priority=sub.priority,
                        notes=sub.notes,
                    ),
                )
        lines.append(
            BOMLineRead(
                line_id=db_line.id if db_line is not None else None,
                line_sequence=line.line_sequence,
                component_sku=comp.sku,
                component_name=comp.name,
                component_category=comp.category,
                quantity_per_unit=line.quantity_per_unit,
                consumption_type=line.consumption_type,
                wastage_percentage=line.wastage_percentage,
                yield_percentage=line.yield_percentage,
                is_phantom=line.is_phantom,
                lead_time_offset_days=line.lead_time_offset_days,
                notes=line.notes,
                product_snapshot=product_snapshot_from_row(comp_row),
                substitutes=substitutes,
            ),
        )

    alternates: list[BOMAlternateRead] = []
    for alt in await bom_crud.list_bom_alternates(db, bom.parent_item_id):
        alt_item = alt.alternate_parent_item
        alternates.append(
            BOMAlternateRead(
                id=alt.id,
                alternate_parent_item_id=alt.alternate_parent_item_id,
                alternate_parent_sku=alt_item.sku if alt_item else "",
                alternate_parent_name=alt_item.name if alt_item else "",
                alternate_group=alt.alternate_group,
                priority=alt.priority,
                notes=alt.notes,
            ),
        )

    return BOMRead(
        parent_item_id=bom.parent_item_id,
        parent_sku=bom.parent_sku,
        parent_name=parent_item.name if parent_item else bom.parent_sku,
        parent_description=parent_description,
        bom_number=bom.bom_number,
        version=bom.version,
        status=bom.status,
        bom_type=bom.bom_type,
        effective_start_date=bom.effective_start_date,
        effective_end_date=bom.effective_end_date,
        eco_number=bom.eco_number,
        approved_at=bom.approved_at,
        approved_by_id=bom.approved_by_id,
        created_by_id=bom.created_by_id,
        created_at=bom.created_at,
        updated_by_id=bom.updated_by_id,
        updated_at=bom.updated_at,
        parent_product_snapshot=parent_snapshot,
        lines=lines,
        alternates=alternates,
    )


@router.get("", response_model=BOMListResponse)
async def list_boms(
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
) -> BOMListResponse:
    boms = await svc._repo.list_all_boms()
    summaries: list[BOMSummaryRead] = []
    for bom in sorted(boms, key=lambda b: b.parent_sku):
        parent = await svc._repo.get_item_by_id(bom.parent_item_id)
        summaries.append(
            BOMSummaryRead(
                parent_sku=bom.parent_sku,
                parent_name=parent.name if parent else bom.parent_sku,
                bom_number=bom.bom_number,
                version=bom.version,
                status=bom.status,
                bom_type=bom.bom_type,
                line_count=len(bom.lines),
                effective_start_date=bom.effective_start_date,
                updated_at=bom.updated_at,
            ),
        )
    return BOMListResponse(boms=summaries)


@router.get("/items", response_model=ItemListResponse)
async def list_manufacturing_items(
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    category: str | None = None,
) -> ItemListResponse:
    items = await svc._repo.list_items()
    if category:
        items = [i for i in items if i.category.value == category.upper()]
    return ItemListResponse(items=[ItemRead.from_item(i) for i in items])


@router.get("/items/{sku}", response_model=ItemRead)
async def get_manufacturing_item(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
) -> ItemRead:
    item = await svc._repo.get_item_by_sku(sku)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Item not found: {sku}")
    return ItemRead.from_item(item)


@router.get("/{sku}", response_model=BOMRead)
async def get_bom(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BOMRead:
    parent = await svc._repo.get_item_by_sku(sku)
    if parent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Item not found: {sku}")
    bom = await svc._repo.get_bom_by_parent_id(parent.id)
    if bom is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"BOM not found for: {sku}")
    return await _bom_to_read_async(bom, svc, db)


@router.post("/{sku}", response_model=AddBOMResponse)
async def save_bom_endpoint(
    sku: str,
    body: SaveBOMRequest,
    user: Annotated[User, Depends(BOMWriteRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AddBOMResponse:
    try:
        bom = await svc.save_bom(sku, body, user_id=user.id)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BOMError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    validation = await svc.validate_bom(bom)
    return AddBOMResponse(bom=await _bom_to_read_async(bom, svc, db), validation=validation)


@router.patch("/{sku}/status", response_model=BOMRead)
async def patch_bom_status(
    sku: str,
    body: UpdateBOMStatusRequest,
    user: Annotated[User, Depends(BOMWriteRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BOMRead:
    try:
        bom = await svc.update_bom_status(sku, body.status, user_id=user.id)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BOMNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BOMError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return await _bom_to_read_async(bom, svc, db)


@router.get("/{sku}/tree", response_model=BOMTreeResponse)
async def get_bom_tree(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    depth: int | None = Query(default=None, ge=0, le=20),
) -> BOMTreeResponse:
    try:
        return await svc.get_full_bom(sku, depth=depth)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except BOMNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{sku}/explode", response_model=ExplosionResponse)
async def explode_bom_endpoint(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    order_quantity: int = Query(default=1, ge=1, le=1_000_000),
) -> ExplosionResponse:
    try:
        return await svc.explode_bom(sku, order_quantity=order_quantity)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{sku}/fabric-summary", response_model=FabricSummaryResponse)
async def fabric_summary(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    order_qty: int = Query(default=1, ge=1, le=1_000_000),
) -> FabricSummaryResponse:
    try:
        return await svc.get_fabric_consumption_summary(sku, order_qty=order_qty)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{sku}/trim-summary", response_model=TrimSummaryResponse)
async def trim_summary(
    sku: str,
    _: Annotated[User, Depends(BOMReadRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    order_qty: int = Query(default=1, ge=1, le=1_000_000),
) -> TrimSummaryResponse:
    try:
        return await svc.get_trim_requirements(sku, order_qty=order_qty)
    except ItemNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{sku}/alternates", status_code=status.HTTP_201_CREATED)
async def add_bom_alternate_endpoint(
    sku: str,
    body: BOMAlternateCreate,
    _: Annotated[User, Depends(BOMWriteRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BOMAlternateRead:
    parent = await svc._repo.get_item_by_sku(sku)
    if parent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Item not found: {sku}")
    alt_item = await svc._repo.get_item_by_sku(body.alternate_parent_sku)
    if alt_item is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Alternate item not found: {body.alternate_parent_sku}",
        )
    alt = await bom_crud.add_bom_alternate(
        db,
        parent.id,
        alternate_parent_item_id=alt_item.id,
        alternate_group=body.alternate_group,
        priority=body.priority,
        notes=body.notes,
    )
    await db.commit()
    return BOMAlternateRead(
        id=alt.id,
        alternate_parent_item_id=alt.alternate_parent_item_id,
        alternate_parent_sku=alt_item.sku,
        alternate_parent_name=alt_item.name,
        alternate_group=alt.alternate_group,
        priority=alt.priority,
        notes=alt.notes,
    )


@router.post("/{sku}/lines/{line_id}/substitutes", status_code=status.HTTP_201_CREATED)
async def add_bom_substitute_endpoint(
    sku: str,
    line_id: int,
    body: BOMSubstituteCreate,
    _: Annotated[User, Depends(BOMWriteRoles)],
    svc: Annotated[BOMService, Depends(get_bom_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BOMSubstituteRead:
    parent = await svc._repo.get_item_by_sku(sku)
    if parent is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Item not found: {sku}")
    db_lines = await bom_crud.list_bom_lines_with_substitutes(db, parent.id)
    db_line = next((ln for ln in db_lines if ln.id == line_id), None)
    if db_line is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"BOM line not found: {line_id}")
    sub_item = await svc._repo.get_item_by_sku(body.substitute_sku)
    if sub_item is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Substitute item not found: {body.substitute_sku}",
        )
    sub = await bom_crud.add_bom_substitute(
        db,
        line_id,
        substitute_item_id=sub_item.id,
        substitute_quantity=body.substitute_quantity,
        priority=body.priority,
        notes=body.notes,
    )
    await db.commit()
    return BOMSubstituteRead(
        id=sub.id,
        substitute_item_id=sub.substitute_item_id,
        substitute_sku=sub_item.sku,
        substitute_name=sub_item.name,
        substitute_quantity=sub.substitute_quantity,
        priority=sub.priority,
        notes=sub.notes,
    )
