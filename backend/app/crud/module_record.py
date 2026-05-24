from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module_record import ModuleRecord
from app.schemas.module_record import ModuleRecordCreate, ModuleRecordUpdate


async def list_module_records(
    db: AsyncSession,
    *,
    module_code: str,
    feature_code: str | None = None,
    search: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[ModuleRecord], int]:
    stmt = select(ModuleRecord).where(ModuleRecord.module_code == module_code)
    count_stmt = (
        select(func.count())
        .select_from(ModuleRecord)
        .where(ModuleRecord.module_code == module_code)
    )

    if feature_code:
        stmt = stmt.where(ModuleRecord.feature_code == feature_code)
        count_stmt = count_stmt.where(ModuleRecord.feature_code == feature_code)
    if status:
        stmt = stmt.where(ModuleRecord.status == status)
        count_stmt = count_stmt.where(ModuleRecord.status == status)
    if search:
        pattern = f"%{search.strip()}%"
        expr = or_(
            ModuleRecord.title.ilike(pattern),
            ModuleRecord.reference.ilike(pattern),
            ModuleRecord.party_name.ilike(pattern),
            ModuleRecord.description.ilike(pattern),
        )
        stmt = stmt.where(expr)
        count_stmt = count_stmt.where(expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(ModuleRecord.updated_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all()), total


async def count_records_by_feature(
    db: AsyncSession,
    module_code: str,
) -> dict[str, int]:
    result = await db.execute(
        select(ModuleRecord.feature_code, func.count())
        .where(ModuleRecord.module_code == module_code)
        .group_by(ModuleRecord.feature_code)
    )
    return {row[0]: row[1] for row in result.all()}


async def get_module_record(db: AsyncSession, record_id: int) -> ModuleRecord | None:
    result = await db.execute(select(ModuleRecord).where(ModuleRecord.id == record_id))
    return result.scalar_one_or_none()


async def create_module_record(
    db: AsyncSession,
    module_code: str,
    body: ModuleRecordCreate,
) -> ModuleRecord:
    record = ModuleRecord(
        module_code=module_code,
        feature_code=body.feature_code,
        reference=body.reference.strip(),
        title=body.title.strip(),
        status=body.status,
        description=body.description,
        party_name=body.party_name,
        amount=body.amount,
        quantity=body.quantity,
        start_date=body.start_date,
        end_date=body.end_date,
        extra_data=body.extra_data,
    )
    db.add(record)
    await db.flush()
    return record


async def update_module_record(
    db: AsyncSession,
    record: ModuleRecord,
    body: ModuleRecordUpdate,
) -> ModuleRecord:
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key == "title" and value is not None:
            value = value.strip()
        setattr(record, key, value)
    await db.flush()
    return record


async def delete_module_record(db: AsyncSession, record: ModuleRecord) -> None:
    await db.delete(record)
    await db.flush()
