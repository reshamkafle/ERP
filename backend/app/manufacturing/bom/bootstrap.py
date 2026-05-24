from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bom as bom_crud
from app.manufacturing.bom.demo_data import seed_garment_demo
from app.manufacturing.bom.service import BOMService
from app.manufacturing.bom.sql_repository import SqlBOMRepository


async def seed_bom_demo_if_empty(session: AsyncSession) -> None:
    existing = await bom_crud.get_item_by_sku(session, "STYLE-001")
    if existing is not None:
        return
    svc = BOMService(SqlBOMRepository(session))
    await seed_garment_demo(svc)
