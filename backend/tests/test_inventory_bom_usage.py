"""Tests for inventory ↔ BOM usage discovery and stock shortage flags."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.manufacturing.bom.bootstrap import seed_bom_demo_if_empty
from app.models.manufacturing import ManufacturingItem
from app.models.product import Product
from app.services.inventory_bom_usage import (
    _is_short,
    _required_qty_for_component,
    _tree_contains_component,
    get_bom_usages_for_product,
)
from tests.fixtures.bom_garment_sample import build_garment_bom_service


@pytest.mark.asyncio
async def test_bom_usage_logic_in_memory() -> None:
    svc = await build_garment_bom_service()
    lookup = await svc._build_lookup()
    fab = await svc._repo.get_item_by_sku("FAB-RAW")
    style = await svc._repo.get_item_by_sku("STYLE-001")
    assert fab is not None and style is not None

    assert _tree_contains_component(style.id, fab.id, lookup) is True
    required = _required_qty_for_component(style, fab.id, order_quantity=1, lookup=lookup)
    assert required is not None
    assert required > Decimal("0")
    assert _is_short(0, required) is True
    assert _is_short(1000, required) is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_bom_usages_linked_product_postgres(db_session: AsyncSession) -> None:
    await seed_bom_demo_if_empty(db_session)
    await db_session.commit()

    product = Product(
        sku=f"INV-FAB-{uuid.uuid4().hex[:8]}",
        name="Cotton Shirting Inventory",
        stock=10,
        low_stock_threshold=5,
        price=Decimal("0"),
        cost_price=Decimal("3.50"),
    )
    db_session.add(product)
    await db_session.flush()

    result = await db_session.execute(
        select(ManufacturingItem).where(ManufacturingItem.sku == "FAB-RAW"),
    )
    mfg = result.scalar_one()
    mfg.product_id = product.id
    await db_session.commit()

    usages = await get_bom_usages_for_product(db_session, product)
    parent_skus = {u.parent_sku for u in usages}
    assert "STYLE-001" in parent_skus

    style = next(u for u in usages if u.parent_sku == "STYLE-001")
    assert style.required_qty > 0
    assert style.on_hand_stock == 10
    assert style.is_short is (_is_short(10, style.required_qty))

    product.stock = 0
    usages_low = await get_bom_usages_for_product(db_session, product)
    style_low = next(u for u in usages_low if u.parent_sku == "STYLE-001")
    assert style_low.is_short is True

    product.stock = 1000
    usages_ok = await get_bom_usages_for_product(db_session, product)
    style_ok = next(u for u in usages_ok if u.parent_sku == "STYLE-001")
    assert style_ok.is_short is False

    mfg.product_id = None
    await db_session.commit()
    assert await get_bom_usages_for_product(db_session, product) == []
