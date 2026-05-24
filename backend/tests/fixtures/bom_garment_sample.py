"""Shared garment BOM fixture: Style -> Panel -> Fabric cut -> Raw fabric + trim."""

from __future__ import annotations

from app.manufacturing.bom import BOMService, InMemoryBOMRepository
from app.manufacturing.bom.demo_data import seed_garment_demo


async def build_garment_bom_service() -> BOMService:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await seed_garment_demo(svc)
    return svc
