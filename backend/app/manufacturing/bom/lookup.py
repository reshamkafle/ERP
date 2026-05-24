from __future__ import annotations

from app.manufacturing.bom.models import BOM, Item


class PreloadedLookup:
    """In-memory snapshot for sync calculators and validators."""

    def __init__(
        self,
        items: list[Item],
        boms: list[BOM],
    ) -> None:
        self._items_by_id = {i.id: i for i in items}
        self._items_by_sku = {i.sku: i for i in items}
        self._boms_by_parent_id = {b.parent_item_id: b for b in boms}

    def get_item_by_id(self, item_id: int) -> Item | None:
        return self._items_by_id.get(item_id)

    def get_item_by_sku(self, sku: str) -> Item | None:
        return self._items_by_sku.get(sku)

    def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None:
        return self._boms_by_parent_id.get(parent_item_id)

    def list_all_boms(self) -> list[BOM]:
        return list(self._boms_by_parent_id.values())
