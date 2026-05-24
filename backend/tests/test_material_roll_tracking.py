"""Tests for fabric roll / lot tracking."""

from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.enums import ItemType, MaterialRollStatus
from app.models.material_roll import MaterialRoll
from app.models.product import Product
from app.schemas.inventory import InventoryItemCreate
from app.schemas.material_roll import (
    MaterialRollIssueIn,
    MaterialRollReceiveIn,
    MaterialRollScanIn,
)
from app.crud import inventory as inventory_crud
from app.services import material_roll_service as roll_svc


@pytest.mark.asyncio
async def test_receive_and_scan_roll(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-001",
            name="Cotton Jersey Roll",
            item_type=ItemType.RAW,
            roll_tracking_enabled=True,
            primary_uom="meter",
        ),
        user_id=1,
    )
    await seeded_db.commit()

    roll = await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(
            product_id=item.id,
            initial_quantity=Decimal("120.5"),
            primary_uom="meter",
            dye_lot="DL-2026-A",
            color="Navy",
        ),
        user_id=1,
    )
    await seeded_db.commit()

    assert roll.roll_number.startswith("ROLL-")
    assert roll.barcode == roll.roll_number
    assert roll.remaining_quantity == Decimal("120.5")
    assert roll.status == MaterialRollStatus.IN_STOCK

    scanned = await roll_svc.scan_roll(
        seeded_db,
        MaterialRollScanIn(barcode=roll.barcode),
        user_id=1,
    )
    assert scanned.id == roll.id
    assert scanned.last_scanned_by_id == 1


@pytest.mark.asyncio
async def test_partial_issue_roll(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-002",
            name="Poly Roll",
            item_type=ItemType.RAW,
            roll_tracking_enabled=True,
            initial_stock=0,
        ),
        user_id=1,
    )
    roll = await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(product_id=item.id, initial_quantity=Decimal("100")),
        user_id=1,
    )
    await seeded_db.commit()

    await roll_svc.issue_roll_quantity(
        seeded_db,
        roll,
        MaterialRollIssueIn(quantity=Decimal("35.25"), reference_document="CUT-001"),
        user_id=1,
    )
    await seeded_db.commit()

    refreshed = await roll_svc.get_roll(seeded_db, roll.id)
    assert refreshed is not None
    assert refreshed.remaining_quantity == Decimal("64.75")
    assert refreshed.status == MaterialRollStatus.IN_PRODUCTION


@pytest.mark.asyncio
async def test_insufficient_roll_issue_raises(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-003",
            name="Silk Roll",
            item_type=ItemType.RAW,
            roll_tracking_enabled=True,
        ),
        user_id=1,
    )
    roll = await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(product_id=item.id, initial_quantity=Decimal("10")),
        user_id=1,
    )
    await seeded_db.commit()

    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        await roll_svc.issue_roll_quantity(
            seeded_db,
            roll,
            MaterialRollIssueIn(quantity=Decimal("50")),
            user_id=1,
        )


@pytest.mark.asyncio
async def test_list_rolls_filter_by_dye_lot(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-004",
            name="Denim Roll",
            item_type=ItemType.RAW,
        ),
        user_id=1,
    )
    await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(
            product_id=item.id,
            initial_quantity=Decimal("50"),
            dye_lot="SHADE-42",
        ),
        user_id=1,
    )
    await seeded_db.commit()

    rolls, total = await roll_svc.list_rolls(seeded_db, dye_lot="SHADE-42")
    assert total >= 1
    assert any(r.dye_lot == "SHADE-42" for r in rolls)


@pytest.mark.asyncio
async def test_traceability_backward_forward(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-005",
            name="Trace Roll",
            item_type=ItemType.RAW,
        ),
        user_id=1,
    )
    roll = await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(
            product_id=item.id,
            initial_quantity=Decimal("80"),
            grn_reference="GRN-100",
        ),
        user_id=1,
    )
    await roll_svc.issue_roll_quantity(
        seeded_db,
        roll,
        MaterialRollIssueIn(quantity=Decimal("20"), reference_document="WO-1"),
        user_id=1,
    )
    await seeded_db.commit()

    roll = await roll_svc.get_roll(seeded_db, roll.id)
    backward, forward = await roll_svc.get_traceability(seeded_db, roll)
    assert any(n.node_type == "receipt" for n in backward)
    assert len(forward) >= 1


@pytest.mark.asyncio
async def test_product_stock_updated_on_receive(seeded_db):
    item = await inventory_crud.create_inventory_item(
        seeded_db,
        InventoryItemCreate(
            sku="FAB-ROLL-TEST-006",
            name="Stock Rollup",
            item_type=ItemType.RAW,
            initial_stock=0,
        ),
        user_id=1,
    )
    await roll_svc.receive_roll(
        seeded_db,
        MaterialRollReceiveIn(product_id=item.id, initial_quantity=Decimal("45")),
        user_id=1,
    )
    await seeded_db.commit()

    product = await seeded_db.get(Product, item.id)
    assert product is not None
    assert product.stock >= 45
