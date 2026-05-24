"""Tests for extended inventory item master fields."""

from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.models.enums import AbcClass, CostValuationMethod, ItemType, XyzClass
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate, ProductSupplierInput
from app.crud import inventory as inventory_crud


@pytest.mark.asyncio
async def test_create_inventory_item_extended_fields(seeded_db):
    payload = InventoryItemCreate(
        sku="EXT-SKU-001",
        name="Extended Widget",
        item_type=ItemType.SEMI_FINISHED,
        purchase_uom="BOX",
        sales_uom="EA",
        qr_code="QR-123",
        rfid_tag="RFID-456",
        shelf_life_days=90,
        batch_management_enabled=True,
        abc_class=AbcClass.A,
        xyz_class=XyzClass.FAST,
        standard_cost=Decimal("12.50"),
        cost_valuation_method=CostValuationMethod.FIFO,
        reorder_level=10,
        max_stock_level=500,
        economic_order_qty=50,
        lead_time_days=7,
        reorder_point=8,
        safety_stock_level=5,
        min_order_qty=10,
        max_order_qty=200,
        procurement_lead_time_days=14,
        demand_forecast_notes="Seasonal peak in Q4",
        quality_inspection_required=True,
        inspection_checklist={"steps": ["visual", "weight"]},
        expiry_alert_threshold_days=14,
        hazardous_material_class="Class 3",
        regulatory_compliance_codes="FDA-123",
        image_url="https://example.com/img.png",
        attachments=[{"name": "cert.pdf", "url": "https://example.com/cert.pdf", "type": "pdf"}],
        initial_stock=25,
    )
    item = await inventory_crud.create_inventory_item(seeded_db, payload, user_id=1)
    assert item.sku == "EXT-SKU-001"
    assert item.item_type == ItemType.SEMI_FINISHED
    assert item.abc_class == AbcClass.A
    assert item.reorder_level == 10
    assert item.quality_inspection_required is True
    assert item.stock == 25
    assert item.created_by_id == 1


@pytest.mark.asyncio
async def test_update_inventory_item_suppliers(seeded_db):
    from app.models.supplier import Supplier
    from sqlalchemy import select

    result = await seeded_db.execute(select(Supplier).limit(1))
    supplier = result.scalar_one()
    create_payload = InventoryItemCreate(
        sku="EXT-SKU-002",
        name="Supplier Link Item",
        product_suppliers=[
            ProductSupplierInput(
                supplier_id=supplier.id,
                vendor_code="V-99",
                is_preferred=True,
            ),
        ],
    )
    item = await inventory_crud.create_inventory_item(seeded_db, create_payload)
    await seeded_db.refresh(item, ["product_suppliers"])
    assert len(item.product_suppliers) == 1
    assert item.product_suppliers[0].vendor_code == "V-99"

    update_payload = InventoryItemUpdate(product_suppliers=[])
    updated = await inventory_crud.update_inventory_item(
        seeded_db, item, update_payload, user_id=1,
    )
    await seeded_db.refresh(updated, ["product_suppliers"])
    assert len(updated.product_suppliers) == 0


