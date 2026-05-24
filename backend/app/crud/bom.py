from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.manufacturing.bom.enums import BOMStatus, BOMType, ConsumptionType, ItemCategory, UnitOfMeasure
from app.manufacturing.bom.models import BOM, BOMItem, Item
from app.models.manufacturing import BOMHeader, BOMLine, BOMAlternate, BOMSubstitute, ManufacturingItem
from app.models.product import Product


def _product_load_options():
    return selectinload(ManufacturingItem.product).selectinload(Product.default_supplier)


def item_to_domain(row: ManufacturingItem) -> Item:
    secondary = None
    if row.secondary_uom:
        secondary = UnitOfMeasure(row.secondary_uom)
    return Item(
        id=row.id,
        sku=row.sku,
        name=row.name,
        category=row.category,
        unit=row.unit,
        cost_per_unit=row.cost_per_unit,
        secondary_uom=secondary,
        conversion_factor=row.conversion_factor,
    )


def bom_to_domain(header: BOMHeader, parent_sku: str) -> BOM:
    sorted_lines = sorted(header.lines, key=lambda ln: ln.line_sequence)
    lines = [
        BOMItem(
            parent_item_id=line.parent_item_id,
            component_item_id=line.component_item_id,
            line_sequence=line.line_sequence,
            quantity_per_unit=line.quantity_per_unit,
            consumption_type=line.consumption_type,
            wastage_percentage=line.wastage_percentage,
            yield_percentage=line.yield_percentage,
            is_phantom=line.is_phantom,
            lead_time_offset_days=line.lead_time_offset_days,
            notes=line.notes,
        )
        for line in sorted_lines
    ]
    return BOM(
        parent_item_id=header.parent_item_id,
        parent_sku=parent_sku,
        lines=lines,
        bom_number=header.bom_number,
        version=header.version,
        status=header.status,
        bom_type=header.bom_type,
        effective_start_date=header.effective_start_date,
        effective_end_date=header.effective_end_date,
        eco_number=header.eco_number,
        approved_at=header.approved_at,
        approved_by_id=header.approved_by_id,
        created_by_id=header.created_by_id,
        created_at=header.created_at,
        updated_by_id=header.updated_by_id,
        updated_at=header.updated_at,
    )


def default_bom_number(parent_sku: str, version: int) -> str:
    return f"{parent_sku}-V{version}"


async def get_mfg_item_with_product(session: AsyncSession, item_id: int) -> ManufacturingItem | None:
    result = await session.execute(
        select(ManufacturingItem)
        .where(ManufacturingItem.id == item_id)
        .options(_product_load_options()),
    )
    return result.scalar_one_or_none()


async def get_item_by_sku(session: AsyncSession, sku: str) -> Item | None:
    result = await session.execute(
        select(ManufacturingItem).where(ManufacturingItem.sku == sku),
    )
    row = result.scalar_one_or_none()
    return item_to_domain(row) if row else None


async def get_item_by_id(session: AsyncSession, item_id: int) -> Item | None:
    result = await session.execute(
        select(ManufacturingItem).where(ManufacturingItem.id == item_id),
    )
    row = result.scalar_one_or_none()
    return item_to_domain(row) if row else None


async def list_items(session: AsyncSession) -> list[Item]:
    result = await session.execute(select(ManufacturingItem).order_by(ManufacturingItem.sku))
    return [item_to_domain(row) for row in result.scalars().all()]


async def insert_item(
    session: AsyncSession,
    *,
    sku: str,
    name: str,
    category: ItemCategory,
    unit: UnitOfMeasure,
    cost_per_unit: Decimal = Decimal("0"),
    secondary_uom: UnitOfMeasure | None = None,
    conversion_factor: Decimal | None = None,
) -> Item:
    row = ManufacturingItem(
        sku=sku,
        name=name,
        category=category,
        unit=unit,
        cost_per_unit=cost_per_unit,
        secondary_uom=secondary_uom.value if secondary_uom else None,
        conversion_factor=conversion_factor,
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return item_to_domain(row)


async def get_bom_by_parent_id(session: AsyncSession, parent_item_id: int) -> BOM | None:
    result = await session.execute(
        select(BOMHeader)
        .where(BOMHeader.parent_item_id == parent_item_id)
        .options(
            selectinload(BOMHeader.lines),
            selectinload(BOMHeader.parent_item),
        ),
    )
    header = result.scalar_one_or_none()
    if header is None:
        return None
    return bom_to_domain(header, header.parent_item.sku)


async def list_all_boms(session: AsyncSession) -> list[BOM]:
    result = await session.execute(
        select(BOMHeader).options(
            selectinload(BOMHeader.lines),
            selectinload(BOMHeader.parent_item),
        ),
    )
    return [bom_to_domain(h, h.parent_item.sku) for h in result.scalars().all()]


async def save_bom(
    session: AsyncSession,
    bom: BOM,
    *,
    user_id: int | None = None,
) -> BOM:
    result = await session.execute(
        select(BOMHeader).where(BOMHeader.parent_item_id == bom.parent_item_id),
    )
    header = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    bom_number = bom.bom_number or default_bom_number(bom.parent_sku, bom.version)

    if header is None:
        header = BOMHeader(
            parent_item_id=bom.parent_item_id,
            bom_number=bom_number,
            version=bom.version,
            status=bom.status,
            bom_type=bom.bom_type,
            effective_start_date=bom.effective_start_date,
            effective_end_date=bom.effective_end_date,
            eco_number=bom.eco_number,
            approved_at=bom.approved_at,
            approved_by_id=bom.approved_by_id,
            created_by_id=user_id or bom.created_by_id,
            updated_by_id=user_id,
            created_at=now,
            updated_at=now,
        )
        session.add(header)
    else:
        header.bom_number = bom_number
        header.version = bom.version
        header.status = bom.status
        header.bom_type = bom.bom_type
        header.effective_start_date = bom.effective_start_date
        header.effective_end_date = bom.effective_end_date
        header.eco_number = bom.eco_number
        header.approved_at = bom.approved_at
        header.approved_by_id = bom.approved_by_id
        header.updated_by_id = user_id or bom.updated_by_id
        header.updated_at = now

    await session.execute(
        delete(BOMLine).where(BOMLine.parent_item_id == bom.parent_item_id),
    )

    for line in sorted(bom.lines, key=lambda ln: ln.line_sequence):
        session.add(
            BOMLine(
                parent_item_id=line.parent_item_id,
                component_item_id=line.component_item_id,
                line_sequence=line.line_sequence,
                quantity_per_unit=line.quantity_per_unit,
                consumption_type=line.consumption_type,
                wastage_percentage=line.wastage_percentage,
                yield_percentage=line.yield_percentage,
                is_phantom=line.is_phantom,
                lead_time_offset_days=line.lead_time_offset_days,
                notes=line.notes,
            ),
        )

    await session.flush()
    await session.commit()
    refreshed = await get_bom_by_parent_id(session, bom.parent_item_id)
    assert refreshed is not None
    return refreshed


async def update_bom_status(
    session: AsyncSession,
    parent_item_id: int,
    status: BOMStatus,
    *,
    user_id: int | None = None,
    approved_by_id: int | None = None,
) -> BOM | None:
    result = await session.execute(
        select(BOMHeader).where(BOMHeader.parent_item_id == parent_item_id),
    )
    header = result.scalar_one_or_none()
    if header is None:
        return None
    now = datetime.now(timezone.utc)
    header.status = status
    header.updated_by_id = user_id
    header.updated_at = now
    if status == BOMStatus.ACTIVE and approved_by_id is not None:
        header.approved_by_id = approved_by_id
        header.approved_at = now
    await session.flush()
    await session.commit()
    return await get_bom_by_parent_id(session, parent_item_id)


async def delete_bom_lines(session: AsyncSession, parent_item_id: int) -> None:
    await session.execute(delete(BOMLine).where(BOMLine.parent_item_id == parent_item_id))
    result = await session.execute(
        select(BOMHeader).where(BOMHeader.parent_item_id == parent_item_id),
    )
    header = result.scalar_one_or_none()
    if header:
        await session.delete(header)


async def list_bom_alternates(session: AsyncSession, parent_item_id: int) -> list[BOMAlternate]:
    result = await session.execute(
        select(BOMAlternate)
        .where(BOMAlternate.parent_item_id == parent_item_id)
        .options(selectinload(BOMAlternate.alternate_parent_item))
        .order_by(BOMAlternate.alternate_group, BOMAlternate.priority),
    )
    return list(result.scalars().all())


async def list_bom_lines_with_substitutes(
    session: AsyncSession,
    parent_item_id: int,
) -> list[BOMLine]:
    result = await session.execute(
        select(BOMLine)
        .where(BOMLine.parent_item_id == parent_item_id)
        .options(
            selectinload(BOMLine.substitutes).selectinload(BOMSubstitute.substitute_item),
            selectinload(BOMLine.component_item),
        )
        .order_by(BOMLine.line_sequence),
    )
    return list(result.scalars().all())


async def add_bom_alternate(
    session: AsyncSession,
    parent_item_id: int,
    *,
    alternate_parent_item_id: int,
    alternate_group: str = "DEFAULT",
    priority: int = 1,
    notes: str | None = None,
) -> BOMAlternate:
    alt = BOMAlternate(
        parent_item_id=parent_item_id,
        alternate_parent_item_id=alternate_parent_item_id,
        alternate_group=alternate_group,
        priority=priority,
        notes=notes,
    )
    session.add(alt)
    await session.flush()
    await session.refresh(alt, attribute_names=["alternate_parent_item"])
    return alt


async def add_bom_substitute(
    session: AsyncSession,
    bom_line_id: int,
    *,
    substitute_item_id: int,
    substitute_quantity: Decimal,
    priority: int = 1,
    notes: str | None = None,
) -> BOMSubstitute:
    sub = BOMSubstitute(
        bom_line_id=bom_line_id,
        substitute_item_id=substitute_item_id,
        substitute_quantity=substitute_quantity,
        priority=priority,
        notes=notes,
    )
    session.add(sub)
    await session.flush()
    await session.refresh(sub, attribute_names=["substitute_item"])
    return sub
