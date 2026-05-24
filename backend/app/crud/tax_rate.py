from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax_rate import TaxRate
from app.schemas.tax import TaxRateCreate, TaxRateUpdate


async def list_tax_rates(
    db: AsyncSession,
    *,
    country_code: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[TaxRate], int]:
    stmt = select(TaxRate).order_by(TaxRate.code, TaxRate.effective_from.desc())
    count_stmt = select(func.count()).select_from(TaxRate)
    if country_code:
        stmt = stmt.where(TaxRate.country_code == country_code.upper())
        count_stmt = count_stmt.where(TaxRate.country_code == country_code.upper())
    if is_active is not None:
        stmt = stmt.where(TaxRate.is_active == is_active)
        count_stmt = count_stmt.where(TaxRate.is_active == is_active)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_tax_rate(db: AsyncSession, tax_rate_id: int) -> TaxRate | None:
    result = await db.execute(select(TaxRate).where(TaxRate.id == tax_rate_id))
    return result.scalar_one_or_none()


async def _has_overlap(
    db: AsyncSession,
    *,
    code: str,
    country_code: str,
    effective_from: date,
    effective_to: date | None,
    exclude_id: int | None = None,
) -> bool:
    stmt = select(TaxRate.id).where(
        TaxRate.code == code,
        TaxRate.country_code == country_code,
        TaxRate.is_active.is_(True),
    )
    if exclude_id is not None:
        stmt = stmt.where(TaxRate.id != exclude_id)
    end_bound = effective_to or date(9999, 12, 31)
    stmt = stmt.where(
        TaxRate.effective_from <= end_bound,
        or_(TaxRate.effective_to.is_(None), TaxRate.effective_to >= effective_from),
    )
    result = await db.execute(stmt.limit(1))
    return result.scalar_one_or_none() is not None


async def create_tax_rate(db: AsyncSession, payload: TaxRateCreate) -> TaxRate:
    if await _has_overlap(
        db,
        code=payload.code,
        country_code=payload.country_code.upper(),
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Overlapping active tax rate for this code and country",
        )
    row = TaxRate(
        code=payload.code,
        name=payload.name,
        rate_percent=payload.rate_percent,
        tax_type=payload.tax_type,
        country_code=payload.country_code.upper(),
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        is_active=payload.is_active,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_tax_rate(
    db: AsyncSession,
    row: TaxRate,
    payload: TaxRateUpdate,
) -> TaxRate:
    data = payload.model_dump(exclude_unset=True)
    effective_from = data.get("effective_from", row.effective_from)
    effective_to = data.get("effective_to", row.effective_to)
    code = row.code
    country = row.country_code
    if await _has_overlap(
        db,
        code=code,
        country_code=country,
        effective_from=effective_from,
        effective_to=effective_to,
        exclude_id=row.id,
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Overlapping active tax rate for this code and country",
        )
    for key, value in data.items():
        setattr(row, key, value)
    await db.commit()
    await db.refresh(row)
    return row


async def delete_tax_rate(db: AsyncSession, row: TaxRate) -> None:
    await db.delete(row)
    await db.commit()


async def get_active_tax_rate(
    db: AsyncSession,
    *,
    code: str,
    country_code: str,
    as_of: date,
) -> TaxRate | None:
    stmt = (
        select(TaxRate)
        .where(
            TaxRate.code == code,
            TaxRate.country_code == country_code.upper(),
            TaxRate.is_active.is_(True),
            TaxRate.effective_from <= as_of,
            or_(TaxRate.effective_to.is_(None), TaxRate.effective_to >= as_of),
        )
        .order_by(TaxRate.effective_from.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
