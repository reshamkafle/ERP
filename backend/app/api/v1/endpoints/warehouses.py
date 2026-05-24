from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import warehouse as warehouse_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.warehouse import (
    StorageLocationCreate,
    StorageLocationListResponse,
    StorageLocationRead,
    StorageLocationUpdate,
    WarehouseCreate,
    WarehouseListResponse,
    WarehouseRead,
    WarehouseUpdate,
)

router = APIRouter(prefix="/warehouses")

WarehouseReadPerm = require_permission("warehouse.ops.read")
WarehouseWritePerm = require_permission("warehouse.inventory.write")


@router.get("", response_model=WarehouseListResponse)
async def list_warehouses(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseReadPerm)],
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> WarehouseListResponse:
    items, total = await warehouse_crud.list_warehouses(db, search=search, skip=skip, limit=limit)
    return WarehouseListResponse(
        items=[WarehouseRead.model_validate(w) for w in items],
        total=total,
    )


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    body: WarehouseCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> WarehouseRead:
    existing = await warehouse_crud.get_warehouse_by_code(db, body.code)
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Warehouse code already exists")
    wh = await warehouse_crud.create_warehouse(db, body)
    return WarehouseRead.model_validate(wh)


@router.get("/{warehouse_id}", response_model=WarehouseRead)
async def get_warehouse(
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseReadPerm)],
) -> WarehouseRead:
    wh = await warehouse_crud.get_warehouse(db, warehouse_id)
    if wh is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return WarehouseRead.model_validate(wh)


@router.patch("/{warehouse_id}", response_model=WarehouseRead)
async def update_warehouse(
    warehouse_id: int,
    body: WarehouseUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> WarehouseRead:
    wh = await warehouse_crud.get_warehouse(db, warehouse_id)
    if wh is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    if body.code is not None:
        existing = await warehouse_crud.get_warehouse_by_code(db, body.code, exclude_id=warehouse_id)
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Warehouse code already exists")
    updated = await warehouse_crud.update_warehouse(db, wh, body)
    return WarehouseRead.model_validate(updated)


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> None:
    wh = await warehouse_crud.get_warehouse(db, warehouse_id)
    if wh is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    await warehouse_crud.delete_warehouse(db, wh)


locations_router = APIRouter(prefix="/storage-locations")


@locations_router.get("", response_model=StorageLocationListResponse)
async def list_locations(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseReadPerm)],
    warehouse_id: int | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> StorageLocationListResponse:
    items, total = await warehouse_crud.list_storage_locations(
        db,
        warehouse_id=warehouse_id,
        search=search,
        skip=skip,
        limit=limit,
    )
    return StorageLocationListResponse(
        items=[StorageLocationRead.model_validate(loc) for loc in items],
        total=total,
    )


@locations_router.post("", response_model=StorageLocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    body: StorageLocationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> StorageLocationRead:
    wh = await warehouse_crud.get_warehouse(db, body.warehouse_id)
    if wh is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Warehouse not found")
    existing = await warehouse_crud.get_location_by_code(db, body.warehouse_id, body.code)
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Location code already exists in warehouse")
    loc = await warehouse_crud.create_storage_location(db, body)
    return StorageLocationRead.model_validate(loc)


@locations_router.get("/{location_id}", response_model=StorageLocationRead)
async def get_location(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseReadPerm)],
) -> StorageLocationRead:
    loc = await warehouse_crud.get_storage_location(db, location_id)
    if loc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Location not found")
    return StorageLocationRead.model_validate(loc)


@locations_router.patch("/{location_id}", response_model=StorageLocationRead)
async def update_location(
    location_id: int,
    body: StorageLocationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> StorageLocationRead:
    loc = await warehouse_crud.get_storage_location(db, location_id)
    if loc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Location not found")
    wh_id = body.warehouse_id if body.warehouse_id is not None else loc.warehouse_id
    code = body.code if body.code is not None else loc.code
    if body.code is not None or body.warehouse_id is not None:
        existing = await warehouse_crud.get_location_by_code(
            db, wh_id, code, exclude_id=location_id,
        )
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Location code already exists in warehouse")
    updated = await warehouse_crud.update_storage_location(db, loc, body)
    return StorageLocationRead.model_validate(updated)


@locations_router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(WarehouseWritePerm)],
) -> None:
    loc = await warehouse_crud.get_storage_location(db, location_id)
    if loc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Location not found")
    await warehouse_crud.delete_storage_location(db, loc)
