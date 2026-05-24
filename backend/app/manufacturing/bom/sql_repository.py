from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bom as bom_crud
from app.manufacturing.bom.models import BOM, Item


class SqlBOMRepository:
    """PostgreSQL-backed BOM repository (async)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_item_by_sku(self, sku: str) -> Item | None:
        return await bom_crud.get_item_by_sku(self._session, sku)

    async def get_item_by_id(self, item_id: int) -> Item | None:
        return await bom_crud.get_item_by_id(self._session, item_id)

    async def save_item(self, item: Item) -> Item:
        if item.id:
            existing = await bom_crud.get_item_by_id(self._session, item.id)
            if existing:
                return existing
        return await bom_crud.insert_item(
            self._session,
            sku=item.sku,
            name=item.name,
            category=item.category,
            unit=item.unit,
            cost_per_unit=item.cost_per_unit,
            secondary_uom=item.secondary_uom,
            conversion_factor=item.conversion_factor,
        )

    async def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None:
        return await bom_crud.get_bom_by_parent_id(self._session, parent_item_id)

    async def save_bom(self, bom: BOM, *, user_id: int | None = None) -> BOM:
        return await bom_crud.save_bom(self._session, bom, user_id=user_id)

    async def update_bom_status(
        self,
        parent_item_id: int,
        status,
        *,
        user_id: int | None = None,
        approved_by_id: int | None = None,
    ) -> BOM | None:
        return await bom_crud.update_bom_status(
            self._session,
            parent_item_id,
            status,
            user_id=user_id,
            approved_by_id=approved_by_id,
        )

    async def delete_bom_lines(self, parent_item_id: int) -> None:
        await bom_crud.delete_bom_lines(self._session, parent_item_id)

    async def list_all_boms(self) -> list[BOM]:
        return await bom_crud.list_all_boms(self._session)

    async def list_items(self) -> list[Item]:
        return await bom_crud.list_items(self._session)

    async def next_item_id(self) -> int:
        raise NotImplementedError("SQL repository assigns IDs on insert")
