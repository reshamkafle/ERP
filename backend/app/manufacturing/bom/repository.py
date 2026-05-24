from __future__ import annotations

from typing import Protocol

from app.manufacturing.bom.enums import BOMStatus
from app.manufacturing.bom.models import BOM, BOMItem, Item


class BOMRepository(Protocol):
    async def get_item_by_sku(self, sku: str) -> Item | None: ...
    async def get_item_by_id(self, item_id: int) -> Item | None: ...
    async def save_item(self, item: Item) -> Item: ...
    async def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None: ...
    async def save_bom(self, bom: BOM, *, user_id: int | None = None) -> BOM: ...
    async def update_bom_status(
        self,
        parent_item_id: int,
        status: BOMStatus,
        *,
        user_id: int | None = None,
        approved_by_id: int | None = None,
    ) -> BOM | None: ...
    async def delete_bom_lines(self, parent_item_id: int) -> None: ...
    async def list_all_boms(self) -> list[BOM]: ...
    async def list_items(self) -> list[Item]: ...
    async def next_item_id(self) -> int: ...


class InMemoryBOMRepository:
    """Dict-backed BOM repository for tests and local demos."""

    def __init__(self) -> None:
        self._items_by_id: dict[int, Item] = {}
        self._items_by_sku: dict[str, Item] = {}
        self._boms_by_parent_id: dict[int, BOM] = {}
        self._next_id = 1

    async def next_item_id(self) -> int:
        item_id = self._next_id
        self._next_id += 1
        return item_id

    async def get_item_by_sku(self, sku: str) -> Item | None:
        return self._items_by_sku.get(sku)

    async def get_item_by_id(self, item_id: int) -> Item | None:
        return self._items_by_id.get(item_id)

    async def save_item(self, item: Item) -> Item:
        if item.id == 0:
            item = item.model_copy(update={"id": await self.next_item_id()})
        self._items_by_id[item.id] = item
        self._items_by_sku[item.sku] = item
        if item.id >= self._next_id:
            self._next_id = item.id + 1
        return item

    async def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None:
        return self._boms_by_parent_id.get(parent_item_id)

    async def save_bom(self, bom: BOM, *, user_id: int | None = None) -> BOM:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stored = bom.model_copy(
            update={
                "updated_by_id": user_id or bom.updated_by_id,
                "updated_at": now,
                "created_by_id": bom.created_by_id or user_id,
                "created_at": bom.created_at or now,
            },
        )
        self._boms_by_parent_id[bom.parent_item_id] = stored
        return stored

    async def update_bom_status(
        self,
        parent_item_id: int,
        status: BOMStatus,
        *,
        user_id: int | None = None,
        approved_by_id: int | None = None,
    ) -> BOM | None:
        bom = self._boms_by_parent_id.get(parent_item_id)
        if bom is None:
            return None
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        updates: dict = {"status": status, "updated_by_id": user_id, "updated_at": now}
        if status == BOMStatus.ACTIVE and approved_by_id is not None:
            updates["approved_by_id"] = approved_by_id
            updates["approved_at"] = now
        updated = bom.model_copy(update=updates)
        self._boms_by_parent_id[parent_item_id] = updated
        return updated

    async def delete_bom_lines(self, parent_item_id: int) -> None:
        self._boms_by_parent_id.pop(parent_item_id, None)

    async def list_all_boms(self) -> list[BOM]:
        return list(self._boms_by_parent_id.values())

    async def list_items(self) -> list[Item]:
        return sorted(self._items_by_id.values(), key=lambda i: i.sku)
