from __future__ import annotations

from app.manufacturing.bom.demo_data import create_demo_bom_service
from app.manufacturing.bom.service import BOMService

_bom_service: BOMService | None = None


async def get_inmemory_bom_service() -> BOMService:
    """In-memory service for unit tests only."""
    global _bom_service
    if _bom_service is None:
        _bom_service = await create_demo_bom_service()
    return _bom_service
