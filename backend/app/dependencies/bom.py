from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.manufacturing.bom.service import BOMService
from app.manufacturing.bom.sql_repository import SqlBOMRepository


async def get_bom_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BOMService:
    return BOMService(SqlBOMRepository(db))
