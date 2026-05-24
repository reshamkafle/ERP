"""Discover parent BOMs that consume a linked inventory item and flag stock shortages."""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import bom as bom_crud
from app.manufacturing.bom.calculators import apply_quantity_to_primary_uom, apply_wastage, explode_bom
from app.manufacturing.bom.effective import bom_is_effective
from app.manufacturing.bom.enums import BOMStatus
from app.manufacturing.bom.lookup import PreloadedLookup
from app.manufacturing.bom.models import Item
from app.models.manufacturing import BOMHeader, ManufacturingItem
from app.models.product import Product


@dataclass(frozen=True)
class BomUsageRow:
    parent_sku: str
    parent_name: str
    parent_category: str
    required_qty: Decimal
    on_hand_stock: int
    is_short: bool


@dataclass(frozen=True)
class BomUsageSummary:
    bom_parent_count: int
    has_bom_shortage: bool


def _tree_contains_component(
    parent_id: int,
    target_id: int,
    lookup: PreloadedLookup,
) -> bool:
    bom = lookup.get_bom_by_parent_id(parent_id)
    if bom is None or not bom_is_effective(bom):
        return parent_id == target_id
    for line in bom.lines:
        if line.component_item_id == target_id:
            return True
        if _tree_contains_component(line.component_item_id, target_id, lookup):
            return True
    return False


def _required_qty_for_component(
    parent_item: Item,
    target_id: int,
    order_quantity: int,
    lookup: PreloadedLookup,
) -> Decimal | None:
    explosion = explode_bom(parent_item, order_quantity, lookup)
    for line in explosion.lines:
        if line.item_id == target_id:
            return line.total_qty

    need = Decimal(order_quantity)

    def dfs(parent_id: int, qty_needed: Decimal) -> Decimal | None:
        if parent_id == target_id:
            return qty_needed
        bom = lookup.get_bom_by_parent_id(parent_id)
        if bom is None or not bom_is_effective(bom):
            return None
        total = Decimal("0")
        found = False
        for line in bom.lines:
            component = lookup.get_item_by_id(line.component_item_id)
            if component is None:
                continue
            extended = apply_quantity_to_primary_uom(qty_needed * line.quantity_per_unit, component)
            if line.component_item_id == target_id:
                _, _, with_wastage = apply_wastage(extended, line.wastage_percentage)
                total += with_wastage
                found = True
            else:
                sub = dfs(line.component_item_id, extended)
                if sub is not None:
                    total += sub
                    found = True
        return total if found else None

    return dfs(parent_item.id, need)


def _is_short(on_hand: int, required: Decimal) -> bool:
    if required <= 0:
        return False
    return on_hand < math.ceil(float(required))


async def _build_lookup(session: AsyncSession) -> PreloadedLookup:
    items = await bom_crud.list_items(session)
    boms = await bom_crud.list_all_boms(session)
    return PreloadedLookup(items, boms)


async def _get_linked_mfg_item(
    session: AsyncSession,
    product_id: int,
) -> ManufacturingItem | None:
    result = await session.execute(
        select(ManufacturingItem).where(ManufacturingItem.product_id == product_id),
    )
    return result.scalar_one_or_none()


async def get_bom_usages_for_product(
    session: AsyncSession,
    product: Product,
) -> list[BomUsageRow]:
    mfg = await _get_linked_mfg_item(session, product.id)
    if mfg is None:
        return []

    lookup = await _build_lookup(session)
    parent_item = lookup.get_item_by_id(mfg.id)
    if parent_item is None:
        return []

    headers = (
        await session.execute(
            select(BOMHeader)
            .where(BOMHeader.status == BOMStatus.ACTIVE)
            .order_by(BOMHeader.parent_item_id),
        )
    ).scalars().all()

    usages: list[BomUsageRow] = []
    for header in headers:
        parent = lookup.get_item_by_id(header.parent_item_id)
        if parent is None:
            continue
        if not _tree_contains_component(parent.id, mfg.id, lookup):
            continue
        required = _required_qty_for_component(parent, mfg.id, order_quantity=1, lookup=lookup)
        if required is None:
            continue
        usages.append(
            BomUsageRow(
                parent_sku=parent.sku,
                parent_name=parent.name,
                parent_category=parent.category.value,
                required_qty=required,
                on_hand_stock=product.stock,
                is_short=_is_short(product.stock, required),
            ),
        )

    usages.sort(key=lambda u: u.parent_sku)
    return usages


async def get_bom_usage_summary(
    session: AsyncSession,
    product: Product,
) -> BomUsageSummary:
    usages = await get_bom_usages_for_product(session, product)
    return BomUsageSummary(
        bom_parent_count=len(usages),
        has_bom_shortage=any(u.is_short for u in usages),
    )


async def batch_bom_usage_summaries(
    session: AsyncSession,
    products: list[Product],
) -> dict[int, BomUsageSummary]:
    if not products:
        return {}
    product_ids = [p.id for p in products]
    linked = (
        await session.execute(
            select(ManufacturingItem).where(ManufacturingItem.product_id.in_(product_ids)),
        )
    ).scalars().all()
    linked_by_product = {m.product_id: m for m in linked if m.product_id is not None}
    if not linked_by_product:
        return {pid: BomUsageSummary(0, False) for pid in product_ids}

    lookup = await _build_lookup(session)
    headers = (
        await session.execute(
            select(BOMHeader).where(BOMHeader.status == BOMStatus.ACTIVE),
        )
    ).scalars().all()

    summaries: dict[int, BomUsageSummary] = {}
    for product in products:
        mfg = linked_by_product.get(product.id)
        if mfg is None:
            summaries[product.id] = BomUsageSummary(0, False)
            continue
        count = 0
        any_short = False
        for header in headers:
            parent = lookup.get_item_by_id(header.parent_item_id)
            if parent is None:
                continue
            if not _tree_contains_component(parent.id, mfg.id, lookup):
                continue
            required = _required_qty_for_component(parent, mfg.id, order_quantity=1, lookup=lookup)
            if required is None:
                continue
            count += 1
            if _is_short(product.stock, required):
                any_short = True
        summaries[product.id] = BomUsageSummary(count, any_short)

    return summaries
