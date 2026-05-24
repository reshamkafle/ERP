from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Protocol

from app.manufacturing.bom.effective import bom_is_effective
from app.manufacturing.bom.enums import ItemCategory
from app.manufacturing.bom.models import (
    BOM,
    BOMTree,
    BOMTreeNode,
    ExplosionLine,
    ExplosionResult,
    FabricLine,
    FabricSummary,
    Item,
    TrimLine,
    TrimSummary,
)


class BOMLookup(Protocol):
    def get_item_by_id(self, item_id: int) -> Item | None: ...
    def get_bom_by_parent_id(self, parent_item_id: int) -> BOM | None: ...


def apply_quantity_to_primary_uom(quantity: Decimal, item: Item) -> Decimal:
    """Convert quantity from secondary UOM to primary when conversion_factor is set."""
    if item.secondary_uom is None or item.conversion_factor is None:
        return quantity
    return quantity * item.conversion_factor


def apply_yield(net_qty: Decimal, yield_percentage: Decimal) -> Decimal:
    """Inflate required quantity when process yield is below 100%."""
    if yield_percentage <= 0 or yield_percentage >= 100:
        return net_qty
    return net_qty / (yield_percentage / Decimal("100"))


def apply_wastage(gross_qty: Decimal, wastage_percentage: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Return (gross_qty, wastage_qty, total_qty) where total = gross * (1 + wastage%)."""
    if wastage_percentage <= 0:
        return gross_qty, Decimal("0"), gross_qty
    wastage_qty = gross_qty * (wastage_percentage / Decimal("100"))
    total_qty = gross_qty + wastage_qty
    return gross_qty, wastage_qty, total_qty


def _gross_with_yield_and_wastage(
    net_qty: Decimal,
    yield_percentage: Decimal,
    wastage_percentage: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    """Apply yield inflation then wastage; returns (gross, wastage_qty, total)."""
    gross = apply_yield(net_qty, yield_percentage)
    return apply_wastage(gross, wastage_percentage)


def _should_explode_sub_assembly(component: Item, lookup: BOMLookup) -> bool:
    if component.category != ItemCategory.SUB_ASSEMBLY:
        return False
    bom = lookup.get_bom_by_parent_id(component.id)
    return bom is not None and bom_is_effective(bom) and len(bom.lines) > 0


def explode_bom(
    parent_item: Item,
    order_quantity: int,
    lookup: BOMLookup,
) -> ExplosionResult:
    """
    Flatten multi-level BOM to leaf raw materials with wastage and cost roll-up.
    Uses iterative queue to avoid deep recursion limits.
    """
    if order_quantity < 1:
        raise ValueError("order_quantity must be at least 1")

    # Accumulate by component item_id: gross, wastage, total, consumption_type from last line
    accum: dict[int, dict] = defaultdict(
        lambda: {
            "gross": Decimal("0"),
            "wastage": Decimal("0"),
            "total": Decimal("0"),
            "consumption_type": None,
        },
    )

    # (parent_item_id, qty_needed)
    queue: list[tuple[int, Decimal]] = [(parent_item.id, Decimal(order_quantity))]

    while queue:
        parent_id, qty_needed = queue.pop(0)
        bom = lookup.get_bom_by_parent_id(parent_id)
        if bom is None or not bom_is_effective(bom):
            continue

        for line in bom.lines:
            component = lookup.get_item_by_id(line.component_item_id)
            if component is None:
                continue

            extended = qty_needed * line.quantity_per_unit
            extended = apply_quantity_to_primary_uom(extended, component)

            if line.is_phantom:
                child_bom = lookup.get_bom_by_parent_id(component.id)
                if child_bom is not None and bom_is_effective(child_bom):
                    for child_line in child_bom.lines:
                        child_component = lookup.get_item_by_id(child_line.component_item_id)
                        if child_component is None:
                            continue
                        child_extended = extended * child_line.quantity_per_unit
                        child_extended = apply_quantity_to_primary_uom(child_extended, child_component)
                        if _should_explode_sub_assembly(child_component, lookup):
                            queue.append((child_component.id, child_extended))
                        else:
                            gross, wastage, total = _gross_with_yield_and_wastage(
                                child_extended,
                                child_line.yield_percentage,
                                child_line.wastage_percentage,
                            )
                            entry = accum[child_component.id]
                            entry["gross"] += gross
                            entry["wastage"] += wastage
                            entry["total"] += total
                            entry["consumption_type"] = child_line.consumption_type
                continue

            if _should_explode_sub_assembly(component, lookup):
                queue.append((component.id, extended))
            else:
                gross, wastage, total = _gross_with_yield_and_wastage(
                    extended,
                    line.yield_percentage,
                    line.wastage_percentage,
                )
                entry = accum[component.id]
                entry["gross"] += gross
                entry["wastage"] += wastage
                entry["total"] += total
                entry["consumption_type"] = line.consumption_type

    lines: list[ExplosionLine] = []
    total_cost = Decimal("0")

    for item_id, data in sorted(accum.items(), key=lambda x: x[0]):
        item = lookup.get_item_by_id(item_id)
        if item is None:
            continue
        extended_cost = data["total"] * item.cost_per_unit
        total_cost += extended_cost
        consumption_type = data["consumption_type"] or _default_consumption_type(item)
        lines.append(
            ExplosionLine(
                item_id=item.id,
                sku=item.sku,
                name=item.name,
                category=item.category,
                consumption_type=consumption_type,
                unit=item.unit,
                gross_qty=data["gross"],
                wastage_qty=data["wastage"],
                total_qty=data["total"],
                cost_per_unit=item.cost_per_unit,
                extended_cost=extended_cost,
            ),
        )

    return ExplosionResult(
        parent_sku=parent_item.sku,
        parent_item_id=parent_item.id,
        order_quantity=order_quantity,
        lines=lines,
        total_material_cost=total_cost,
    )


def _default_consumption_type(item: Item):
    from app.manufacturing.bom.enums import ConsumptionType

    if item.category == ItemCategory.FABRIC:
        return ConsumptionType.FABRIC
    if item.category == ItemCategory.TRIM:
        return ConsumptionType.TRIM
    return ConsumptionType.OTHER


def build_bom_tree(
    parent_item: Item,
    lookup: BOMLookup,
    depth: int | None = None,
    quantity_per_unit: Decimal = Decimal("1"),
    consumption_type=None,
    wastage_percentage: Decimal = Decimal("0"),
    yield_percentage: Decimal = Decimal("0"),
    is_phantom: bool = False,
    lead_time_offset_days: int | None = None,
    line_sequence: int = 1,
    notes: str | None = None,
) -> BOMTreeNode:
    """Build recursive BOM tree; depth=None means unlimited."""
    from app.manufacturing.bom.enums import ConsumptionType

    if consumption_type is None:
        consumption_type = ConsumptionType.OTHER

    node = BOMTreeNode(
        item=parent_item,
        line_sequence=line_sequence,
        quantity_per_unit=quantity_per_unit,
        consumption_type=consumption_type,
        wastage_percentage=wastage_percentage,
        yield_percentage=yield_percentage,
        is_phantom=is_phantom,
        lead_time_offset_days=lead_time_offset_days,
        notes=notes,
        children=[],
    )

    if depth is not None and depth <= 0:
        node.rolled_up_cost = _rollup_node_cost(parent_item, lookup)
        return node

    bom = lookup.get_bom_by_parent_id(parent_item.id)
    if bom is None or not bom_is_effective(bom):
        node.rolled_up_cost = parent_item.cost_per_unit * quantity_per_unit
        return node

    child_depth = None if depth is None else depth - 1
    for line in sorted(bom.lines, key=lambda ln: ln.line_sequence):
        component = lookup.get_item_by_id(line.component_item_id)
        if component is None:
            continue
        if line.is_phantom:
            child_bom = lookup.get_bom_by_parent_id(component.id)
            if child_bom is not None and bom_is_effective(child_bom):
                for child_line in sorted(child_bom.lines, key=lambda ln: ln.line_sequence):
                    child_component = lookup.get_item_by_id(child_line.component_item_id)
                    if child_component is None:
                        continue
                    child = build_bom_tree(
                        child_component,
                        lookup,
                        depth=child_depth,
                        quantity_per_unit=line.quantity_per_unit * child_line.quantity_per_unit,
                        consumption_type=child_line.consumption_type,
                        wastage_percentage=child_line.wastage_percentage,
                        yield_percentage=child_line.yield_percentage,
                        is_phantom=child_line.is_phantom,
                        lead_time_offset_days=child_line.lead_time_offset_days,
                        notes=child_line.notes,
                    )
                    node.children.append(child)
            continue
        child = build_bom_tree(
            component,
            lookup,
            depth=child_depth,
            line_sequence=line.line_sequence,
            quantity_per_unit=line.quantity_per_unit,
            consumption_type=line.consumption_type,
            wastage_percentage=line.wastage_percentage,
            yield_percentage=line.yield_percentage,
            is_phantom=line.is_phantom,
            lead_time_offset_days=line.lead_time_offset_days,
            notes=line.notes,
        )
        node.children.append(child)

    node.rolled_up_cost = _rollup_node_cost_from_children(node, lookup)
    return node


def _rollup_node_cost(parent_item: Item, lookup: BOMLookup) -> Decimal:
    """Roll up material cost at qty=1 for a single node."""
    result = explode_bom(parent_item, 1, lookup)
    return result.total_material_cost


def _rollup_node_cost_from_children(node: BOMTreeNode, lookup: BOMLookup) -> Decimal:
    if not node.children:
        _, _, total = _gross_with_yield_and_wastage(
            node.quantity_per_unit,
            node.yield_percentage,
            node.wastage_percentage,
        )
        return total * node.item.cost_per_unit

    total = Decimal("0")
    for child in node.children:
        child_cost = child.rolled_up_cost or Decimal("0")
        # Child rolled_up is at child's own qty=1; scale by parent line qty
        if child.children:
            total += child_cost * node.quantity_per_unit
        else:
            _, _, parent_line_total = _gross_with_yield_and_wastage(
                node.quantity_per_unit * child.quantity_per_unit,
                child.yield_percentage,
                child.wastage_percentage,
            )
            total += parent_line_total * child.item.cost_per_unit
    if total > 0:
        return total
    return _rollup_node_cost(node.item, lookup)


def build_bom_tree_root(
    parent_item: Item,
    lookup: BOMLookup,
    depth: int | None = None,
) -> BOMTree:
    root = build_bom_tree(parent_item, lookup, depth=depth)
    return BOMTree(root=root, parent_sku=parent_item.sku)


def explosion_to_fabric_summary(result: ExplosionResult) -> FabricSummary:
    from app.manufacturing.bom.enums import ConsumptionType, UnitOfMeasure

    fabrics: list[FabricLine] = []
    total_meters = Decimal("0")
    total_cost = Decimal("0")

    for line in result.lines:
        if line.consumption_type != ConsumptionType.FABRIC and line.category.value != "FABRIC":
            continue
        wastage_pct = (
            (line.wastage_qty / line.gross_qty * Decimal("100"))
            if line.gross_qty > 0
            else Decimal("0")
        )
        fabrics.append(
            FabricLine(
                sku=line.sku,
                name=line.name,
                unit=line.unit,
                gross_qty=line.gross_qty,
                wastage_qty=line.wastage_qty,
                total_qty=line.total_qty,
                wastage_percentage=wastage_pct,
                extended_cost=line.extended_cost,
            ),
        )
        if line.unit == UnitOfMeasure.METER:
            total_meters += line.total_qty
        total_cost += line.extended_cost

    return FabricSummary(
        parent_sku=result.parent_sku,
        order_quantity=result.order_quantity,
        fabrics=fabrics,
        total_meters=total_meters,
        total_fabric_cost=total_cost,
    )


def explosion_to_trim_summary(result: ExplosionResult) -> TrimSummary:
    from app.manufacturing.bom.enums import ConsumptionType

    trims: list[TrimLine] = []
    total_cost = Decimal("0")

    for line in result.lines:
        if line.consumption_type != ConsumptionType.TRIM and line.category.value != "TRIM":
            continue
        trims.append(
            TrimLine(
                sku=line.sku,
                name=line.name,
                unit=line.unit,
                gross_qty=line.gross_qty,
                wastage_qty=line.wastage_qty,
                total_qty=line.total_qty,
                extended_cost=line.extended_cost,
            ),
        )
        total_cost += line.extended_cost

    return TrimSummary(
        parent_sku=result.parent_sku,
        order_quantity=result.order_quantity,
        trims=trims,
        total_trim_cost=total_cost,
    )


def material_requirements_dict(result: ExplosionResult) -> dict:
    """Stable dict shape for calculate_material_requirements."""
    return {
        "parent_sku": result.parent_sku,
        "order_qty": result.order_quantity,
        "materials": [
            {
                "sku": line.sku,
                "name": line.name,
                "category": line.category.value,
                "consumption_type": line.consumption_type.value,
                "unit": line.unit.value,
                "gross_qty": line.gross_qty,
                "wastage_qty": line.wastage_qty,
                "total_qty": line.total_qty,
                "cost_per_unit": line.cost_per_unit,
                "extended_cost": line.extended_cost,
            }
            for line in result.lines
        ],
        "total_cost": result.total_material_cost,
    }
