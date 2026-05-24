from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart_of_account import ChartOfAccount


async def list_chart_of_accounts(db: AsyncSession) -> list[ChartOfAccount]:
    result = await db.execute(
        select(ChartOfAccount).where(ChartOfAccount.is_active.is_(True)).order_by(ChartOfAccount.code),
    )
    return list(result.scalars().all())


async def get_account_by_code(db: AsyncSession, code: str) -> ChartOfAccount | None:
    result = await db.execute(
        select(ChartOfAccount).where(ChartOfAccount.code == code, ChartOfAccount.is_active.is_(True)),
    )
    return result.scalar_one_or_none()


async def get_account(db: AsyncSession, account_id: int) -> ChartOfAccount | None:
    result = await db.execute(select(ChartOfAccount).where(ChartOfAccount.id == account_id))
    return result.scalar_one_or_none()
