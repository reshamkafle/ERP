from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sale import Sale


async def generate_order_number(db: AsyncSession, *, as_of: date | None = None) -> str:
    year = (as_of or date.today()).year
    prefix = f"SO-{year}-"
    result = await db.execute(
        select(func.count())
        .select_from(Sale)
        .where(Sale.order_number.like(f"{prefix}%")),
    )
    seq = int(result.scalar_one()) + 1
    return f"{prefix}{seq:05d}"


async def resolve_order_number(
    db: AsyncSession,
    *,
    override: str | None = None,
    as_of: date | None = None,
) -> str:
    if override and override.strip():
        number = override.strip()
        existing = (
            await db.execute(select(Sale.id).where(Sale.order_number == number))
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Order number {number} already exists",
            )
        return number
    return await generate_order_number(db, as_of=as_of)
