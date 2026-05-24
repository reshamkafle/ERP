from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import StorageLocation, Warehouse
from app.schemas.warehouse import StorageLocationCreate, StorageLocationUpdate, WarehouseCreate, WarehouseUpdate


async def list_warehouses(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Warehouse], int]:
    stmt = select(Warehouse)
    count_stmt = select(func.count()).select_from(Warehouse)
    if search:
        pattern = f"%{search.strip()}%"
        filt = or_(Warehouse.code.ilike(pattern), Warehouse.name.ilike(pattern))
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Warehouse.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_warehouse(db: AsyncSession, warehouse_id: int) -> Warehouse | None:
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    return result.scalar_one_or_none()


async def get_warehouse_by_code(
    db: AsyncSession,
    code: str,
    *,
    exclude_id: int | None = None,
) -> Warehouse | None:
    stmt = select(Warehouse).where(Warehouse.code == code)
    if exclude_id is not None:
        stmt = stmt.where(Warehouse.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _clear_other_defaults(db: AsyncSession, exclude_id: int | None = None) -> None:
    stmt = update(Warehouse).values(is_default=False)
    if exclude_id is not None:
        stmt = stmt.where(Warehouse.id != exclude_id)
    await db.execute(stmt)


async def create_warehouse(db: AsyncSession, payload: WarehouseCreate) -> Warehouse:
    data = payload.model_dump()
    if data.get("is_default"):
        await _clear_other_defaults(db)
    wh = Warehouse(**data)
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


async def update_warehouse(
    db: AsyncSession,
    warehouse: Warehouse,
    payload: WarehouseUpdate,
) -> Warehouse:
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        await _clear_other_defaults(db, exclude_id=warehouse.id)
    for key, value in data.items():
        setattr(warehouse, key, value)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse


async def delete_warehouse(db: AsyncSession, warehouse: Warehouse) -> None:
    await db.delete(warehouse)
    await db.commit()


async def list_storage_locations(
    db: AsyncSession,
    *,
    warehouse_id: int | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[StorageLocation], int]:
    stmt = select(StorageLocation)
    count_stmt = select(func.count()).select_from(StorageLocation)
    if warehouse_id is not None:
        stmt = stmt.where(StorageLocation.warehouse_id == warehouse_id)
        count_stmt = count_stmt.where(StorageLocation.warehouse_id == warehouse_id)
    if search:
        pattern = f"%{search.strip()}%"
        filt = StorageLocation.code.ilike(pattern)
        stmt = stmt.where(filt)
        count_stmt = count_stmt.where(filt)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(StorageLocation.code).offset(skip).limit(limit),
    )
    return list(result.scalars().all()), total


async def get_storage_location(db: AsyncSession, location_id: int) -> StorageLocation | None:
    result = await db.execute(
        select(StorageLocation).where(StorageLocation.id == location_id),
    )
    return result.scalar_one_or_none()


async def get_location_by_code(
    db: AsyncSession,
    warehouse_id: int,
    code: str,
    *,
    exclude_id: int | None = None,
) -> StorageLocation | None:
    stmt = select(StorageLocation).where(
        StorageLocation.warehouse_id == warehouse_id,
        StorageLocation.code == code,
    )
    if exclude_id is not None:
        stmt = stmt.where(StorageLocation.id != exclude_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_storage_location(
    db: AsyncSession,
    payload: StorageLocationCreate,
) -> StorageLocation:
    loc = StorageLocation(**payload.model_dump())
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def update_storage_location(
    db: AsyncSession,
    location: StorageLocation,
    payload: StorageLocationUpdate,
) -> StorageLocation:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, key, value)
    await db.commit()
    await db.refresh(location)
    return location


async def delete_storage_location(db: AsyncSession, location: StorageLocation) -> None:
    await db.delete(location)
    await db.commit()
