from __future__ import annotations

from typing import Protocol

from app.manufacturing.bom.enums import BOMStatus, ConsumptionType, ItemCategory
from app.manufacturing.bom.models import BOM, ValidationResult

_ALLOWED_STATUS_TRANSITIONS: dict[BOMStatus, set[BOMStatus]] = {
    BOMStatus.DRAFT: {BOMStatus.ACTIVE, BOMStatus.OBSOLETE},
    BOMStatus.ACTIVE: {BOMStatus.OBSOLETE, BOMStatus.SUPERSEDED},
    BOMStatus.OBSOLETE: {BOMStatus.ACTIVE, BOMStatus.SUPERSEDED},
    BOMStatus.SUPERSEDED: set(),
}


class ItemRegistry(Protocol):
    def get_item_by_id(self, item_id: int): ...
    def get_item_by_sku(self, sku: str): ...
    def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None: ...
    def list_all_boms(self) -> list[BOM]: ...


def validate_status_transition(current: BOMStatus, new: BOMStatus) -> ValidationResult:
    if current == new:
        return ValidationResult(is_valid=True)
    allowed = _ALLOWED_STATUS_TRANSITIONS.get(current, set())
    if new not in allowed:
        return ValidationResult(
            is_valid=False,
            errors=[f"Cannot change BOM status from {current.value} to {new.value}"],
        )
    return ValidationResult(is_valid=True)


def validate_bom(bom: BOM, registry: ItemRegistry) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    parent = registry.get_item_by_id(bom.parent_item_id)
    if parent is None:
        errors.append(f"Parent item id {bom.parent_item_id} not found in registry")

    if (
        bom.effective_start_date is not None
        and bom.effective_end_date is not None
        and bom.effective_start_date > bom.effective_end_date
    ):
        errors.append("effective_start_date must be on or before effective_end_date")

    seen_components: set[tuple[int, int]] = set()
    seen_sequences: set[int] = set()
    for line in bom.lines:
        if line.quantity_per_unit <= 0:
            errors.append(
                f"quantity_per_unit must be > 0 for component {line.component_item_id}",
            )
        if line.wastage_percentage < 0:
            errors.append(
                f"wastage_percentage must be >= 0 for component {line.component_item_id}",
            )
        if line.yield_percentage < 0 or line.yield_percentage > 100:
            errors.append(
                f"yield_percentage must be between 0 and 100 for component {line.component_item_id}",
            )

        if line.line_sequence in seen_sequences:
            errors.append(f"Duplicate line_sequence {line.line_sequence} on parent BOM")
        seen_sequences.add(line.line_sequence)

        key = (line.parent_item_id, line.component_item_id)
        if key in seen_components:
            warnings.append(
                f"Duplicate BOM line: parent {line.parent_item_id} "
                f"component {line.component_item_id}",
            )
        seen_components.add(key)

        component = registry.get_item_by_id(line.component_item_id)
        if component is None:
            errors.append(f"Component item id {line.component_item_id} not found")
            continue

        if (
            component.category == ItemCategory.FINISHED_GOOD
            and line.consumption_type == ConsumptionType.FABRIC
        ):
            warnings.append(
                f"Finished good {component.sku} used as fabric consumption on parent BOM",
            )

    cycle_path = detect_cycle(bom.parent_item_id, registry, pending_bom=bom)
    if cycle_path:
        errors.append(f"BOM cycle detected: {' -> '.join(cycle_path)}")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def _lines_for_parent(
    parent_id: int,
    registry: ItemRegistry,
    pending_bom: BOM | None,
) -> list:
    if pending_bom is not None and pending_bom.parent_item_id == parent_id:
        return pending_bom.lines
    bom = registry.get_bom_by_parent_id(parent_id)
    if bom is None:
        return []
    from app.manufacturing.bom.effective import bom_is_effective

    if not bom_is_effective(bom):
        return []
    return bom.lines


def detect_cycle(
    start_parent_id: int,
    registry: ItemRegistry,
    pending_bom: BOM | None = None,
) -> list[str] | None:
    """
    DFS from parent following component edges; return SKU path if cycle found.
    pending_bom: BOM being validated (not yet saved) takes precedence at its parent.
    """
    parent_item = registry.get_item_by_id(start_parent_id)
    if parent_item is None:
        return None

    def dfs(
        current_id: int,
        path_ids: list[int],
        path_skus: list[str],
        visiting: set[int],
    ) -> list[str] | None:
        item = registry.get_item_by_id(current_id)
        if item is None:
            return None

        if current_id in visiting:
            idx = path_ids.index(current_id)
            return path_skus[idx:] + [item.sku]

        visiting.add(current_id)
        path_ids.append(current_id)
        path_skus.append(item.sku)

        lines = _lines_for_parent(current_id, registry, pending_bom)
        for line in lines:
            result = dfs(
                line.component_item_id,
                path_ids,
                path_skus,
                visiting,
            )
            if result:
                return result

        visiting.remove(current_id)
        path_ids.pop()
        path_skus.pop()
        return None

    return dfs(start_parent_id, [], [], set())


def validate_all_boms(registry: ItemRegistry) -> ValidationResult:
    """Validate every BOM in the registry."""
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for bom in registry.list_all_boms():
        result = validate_bom(bom, registry)
        all_errors.extend(result.errors)
        all_warnings.extend(result.warnings)
    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
    )
