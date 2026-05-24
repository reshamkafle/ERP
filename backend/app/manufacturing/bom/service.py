from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.manufacturing.bom.calculators import (
    build_bom_tree_root,
    explode_bom,
    explosion_to_fabric_summary,
    explosion_to_trim_summary,
    material_requirements_dict,
)
from app.manufacturing.bom.enums import BOMStatus
from app.manufacturing.bom.exceptions import BOMNotFoundError, ItemNotFoundError
from app.manufacturing.bom.lookup import PreloadedLookup
from app.manufacturing.bom.models import (
    BOM,
    BOMItem,
    BOMTree,
    ExplosionResult,
    FabricSummary,
    Item,
    TrimSummary,
    ValidationResult,
)
from app.manufacturing.bom.repository import BOMRepository
from app.manufacturing.bom.schemas import BOMHeaderInput, BOMItemInput, SaveBOMRequest
from app.manufacturing.bom.validators import validate_bom, validate_status_transition


def default_bom_number(parent_sku: str, version: int) -> str:
    return f"{parent_sku}-V{version}"


class BOMService:
    def __init__(self, repo: BOMRepository) -> None:
        self._repo = repo

    async def _build_lookup(self) -> PreloadedLookup:
        items = await self._repo.list_items()
        boms = await self._repo.list_all_boms()
        return PreloadedLookup(items, boms)

    async def register_item(self, item: Item) -> Item:
        existing = await self._repo.get_item_by_sku(item.sku)
        if existing is not None:
            return await self._repo.save_item(item.model_copy(update={"id": existing.id}))
        return await self._repo.save_item(item)

    async def create_item(
        self,
        sku: str,
        name: str,
        category,
        unit,
        cost_per_unit: Decimal = Decimal("0"),
        **kwargs: Any,
    ) -> Item:
        existing = await self._repo.get_item_by_sku(sku)
        if existing is not None:
            return existing
        try:
            item_id = await self._repo.next_item_id()
        except NotImplementedError:
            item_id = 0
        item = Item(
            id=item_id,
            sku=sku,
            name=name,
            category=category,
            unit=unit,
            cost_per_unit=cost_per_unit,
            **kwargs,
        )
        return await self.register_item(item)

    async def add_bom(self, parent_sku: str, bom_items: list[BOMItemInput]) -> BOM:
        """Backward-compatible save; keeps BOM active for existing callers/tests."""
        from app.manufacturing.bom.schemas import BOMHeaderInput

        request = SaveBOMRequest(
            header=BOMHeaderInput(status=BOMStatus.ACTIVE),
            lines=bom_items,
        )
        return await self.save_bom(parent_sku, request)

    async def save_bom(
        self,
        parent_sku: str,
        request: SaveBOMRequest,
        *,
        user_id: int | None = None,
    ) -> BOM:
        parent = await self._require_item(parent_sku)
        header_in = request.header or BOMHeaderInput()
        lines = await self._lines_from_inputs(parent.id, request.lines)

        existing = await self._repo.get_bom_by_parent_id(parent.id)
        version = (existing.version + 1) if existing else 1
        bom_number = default_bom_number(parent.sku, version)

        status = header_in.status
        if existing and existing.status == BOMStatus.ACTIVE and status == BOMStatus.DRAFT:
            status = existing.status

        bom = BOM(
            parent_item_id=parent.id,
            parent_sku=parent.sku,
            lines=lines,
            bom_number=bom_number,
            version=version,
            status=status,
            bom_type=header_in.bom_type,
            effective_start_date=header_in.effective_start_date,
            effective_end_date=header_in.effective_end_date,
            eco_number=header_in.eco_number,
            created_by_id=existing.created_by_id if existing else user_id,
            updated_by_id=user_id,
        )

        lookup = await self._build_lookup()
        result = validate_bom(bom, lookup)
        if not result.is_valid:
            from app.manufacturing.bom.exceptions import BOMError

            raise BOMError("; ".join(result.errors))

        return await self._repo.save_bom(bom, user_id=user_id)

    async def update_bom_status(
        self,
        parent_sku: str,
        status: BOMStatus,
        *,
        user_id: int | None = None,
    ) -> BOM:
        parent = await self._require_item(parent_sku)
        existing = await self._repo.get_bom_by_parent_id(parent.id)
        if existing is None:
            raise BOMNotFoundError(parent_sku)

        transition = validate_status_transition(existing.status, status)
        if not transition.is_valid:
            from app.manufacturing.bom.exceptions import BOMError

            raise BOMError("; ".join(transition.errors))

        updated = await self._repo.update_bom_status(
            parent.id,
            status,
            user_id=user_id,
            approved_by_id=user_id if status == BOMStatus.ACTIVE else None,
        )
        if updated is None:
            raise BOMNotFoundError(parent_sku)
        return updated

    async def _lines_from_inputs(self, parent_id: int, inputs: list[BOMItemInput]) -> list[BOMItem]:
        lines: list[BOMItem] = []
        for idx, inp in enumerate(inputs, start=1):
            component = await self._require_item(inp.component_sku)
            lines.append(
                BOMItem(
                    parent_item_id=parent_id,
                    component_item_id=component.id,
                    line_sequence=inp.line_sequence if inp.line_sequence is not None else idx,
                    quantity_per_unit=inp.quantity_per_unit,
                    consumption_type=inp.consumption_type,
                    wastage_percentage=inp.wastage_percentage,
                    yield_percentage=inp.yield_percentage,
                    is_phantom=inp.is_phantom,
                    lead_time_offset_days=inp.lead_time_offset_days,
                    notes=inp.notes,
                ),
            )
        return lines

    async def get_full_bom(self, sku: str, depth: int | None = None) -> BOMTree:
        parent = await self._require_item(sku)
        bom = await self._repo.get_bom_by_parent_id(parent.id)
        if bom is None:
            raise BOMNotFoundError(sku)
        lookup = await self._build_lookup()
        return build_bom_tree_root(parent, lookup, depth=depth)

    async def explode_bom(self, sku: str, order_quantity: int = 1) -> ExplosionResult:
        parent = await self._require_item(sku)
        lookup = await self._build_lookup()
        return explode_bom(parent, order_quantity, lookup)

    async def calculate_material_requirements(self, sku: str, order_qty: int) -> dict[str, Any]:
        result = await self.explode_bom(sku, order_quantity=order_qty)
        return material_requirements_dict(result)

    async def get_fabric_consumption_summary(self, sku: str, order_qty: int) -> FabricSummary:
        result = await self.explode_bom(sku, order_quantity=order_qty)
        return explosion_to_fabric_summary(result)

    async def get_trim_requirements(self, sku: str, order_qty: int) -> TrimSummary:
        result = await self.explode_bom(sku, order_quantity=order_qty)
        return explosion_to_trim_summary(result)

    async def validate_bom(self, bom: BOM) -> ValidationResult:
        return validate_bom(bom, await self._build_lookup())

    async def _require_item(self, sku: str) -> Item:
        item = await self._repo.get_item_by_sku(sku)
        if item is None:
            raise ItemNotFoundError(sku)
        return item
