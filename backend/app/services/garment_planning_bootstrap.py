"""Bootstrap garment planning demo data on startup."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.testing.seed_garment_planning import seed_garment_planning_demo


async def seed_garment_planning_if_empty(session: AsyncSession) -> None:
    await seed_garment_planning_demo(session)
