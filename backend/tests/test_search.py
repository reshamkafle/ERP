"""Permission-scoped global search."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.enums import (
    StorageLocationStatus,
    StorageLocationType,
    WarehouseStatus,
    WarehouseType,
)
from app.models.module_record import ModuleRecord
from app.models.user import User
from app.models.warehouse import StorageLocation, Warehouse
from app.services.search_service import allowed_entity_types, unified_search


@pytest.mark.asyncio
async def test_allowed_types_respects_permissions() -> None:
    full = allowed_entity_types(
        {
            "sales.customers.read",
            "sales.orders.read",
            "warehouse.documents.read",
            "warehouse.purchases.read",
            "warehouse.suppliers.read",
            "manufacturing.ops.read",
            "warehouse.inventory.read",
            "warehouse.ops.read",
            "procurement.records.read",
            "crm.leads.read",
        },
        None,
    )
    assert "customer" in full
    assert "sale" in full
    assert "module_record" in full
    assert "warehouse" in full
    assert "storage_location" in full

    limited = allowed_entity_types({"sales.customers.read"}, None)
    assert limited == {"customer"}


@pytest.mark.asyncio
async def test_search_sales_only_with_order_permission(seeded_db: AsyncSession) -> None:
    perms = {"sales.orders.read"}
    allowed = allowed_entity_types(perms, None)
    assert "sale" in allowed
    assert "customer" not in allowed

    results = await unified_search(seeded_db, query="SO", permissions=perms, limit=10)
    assert all(r.entity_type == "sale" for r in results)


@pytest.mark.asyncio
async def test_erp_document_hidden_without_navigable_parent(
    seeded_db: AsyncSession,
    admin_user: User,
) -> None:
    """Documents without a route the user can open are omitted."""
    perms = {"warehouse.documents.read"}
    allowed = allowed_entity_types(perms, None)
    assert "erp_document" in allowed
    results = await unified_search(seeded_db, query="PL", permissions=perms, limit=10)
    for hit in results:
        if hit.entity_type == "erp_document":
            assert hit.route.startswith("/")


@pytest.mark.asyncio
async def test_sale_id_context_requires_sale_permission(seeded_db: AsyncSession) -> None:
    perms = {"warehouse.documents.read"}
    results = await unified_search(
        seeded_db,
        query="test",
        permissions=perms,
        sale_id=1,
        limit=10,
    )
    assert results == []


@pytest.mark.asyncio
async def test_search_storage_location_by_code(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    wh = Warehouse(
        code=f"WH-GS-{suffix}",
        name=f"Global Search Warehouse {suffix}",
        warehouse_type=WarehouseType.MAIN,
        status=WarehouseStatus.ACTIVE,
    )
    seeded_db.add(wh)
    await seeded_db.flush()
    loc_code = f"LOC-GS-{suffix}"
    loc = StorageLocation(
        code=loc_code,
        warehouse_id=wh.id,
        location_type=StorageLocationType.BULK,
        status=StorageLocationStatus.AVAILABLE,
    )
    seeded_db.add(loc)
    await seeded_db.commit()

    perms = {"warehouse.ops.read"}
    results = await unified_search(seeded_db, query=loc_code, permissions=perms, limit=10)
    location_hits = [r for r in results if r.entity_type == "storage_location" and r.entity_id == loc.id]
    assert len(location_hits) == 1
    assert location_hits[0].title == loc_code
    assert location_hits[0].route.startswith(f"/locations?search={loc_code}")
    assert f"warehouse_id={wh.id}" in location_hits[0].route


@pytest.mark.asyncio
async def test_storage_location_hidden_without_permission(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    wh = Warehouse(
        code=f"WH-NP-{suffix}",
        name=f"No Permission Warehouse {suffix}",
        warehouse_type=WarehouseType.MAIN,
        status=WarehouseStatus.ACTIVE,
    )
    seeded_db.add(wh)
    await seeded_db.flush()
    loc_code = f"LOC-HIDDEN-{suffix}"
    seeded_db.add(
        StorageLocation(
            code=loc_code,
            warehouse_id=wh.id,
            location_type=StorageLocationType.BULK,
            status=StorageLocationStatus.AVAILABLE,
        ),
    )
    await seeded_db.commit()

    results = await unified_search(
        seeded_db,
        query=loc_code,
        permissions={"sales.customers.read"},
        limit=10,
    )
    assert all(r.entity_type != "storage_location" for r in results)
    assert all(r.entity_type != "warehouse" for r in results)


@pytest.mark.asyncio
async def test_search_customer_by_email(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"customer-a-{suffix}@example.com"
    customer = Customer(
        name=f"Customer A {suffix}",
        email=email,
    )
    seeded_db.add(customer)
    await seeded_db.commit()

    results = await unified_search(
        seeded_db,
        query=email,
        permissions={"sales.customers.read"},
        limit=10,
    )
    customer_hits = [r for r in results if r.entity_type == "customer" and r.entity_id == customer.id]
    assert len(customer_hits) == 1
    assert customer_hits[0].title == f"Customer A {suffix}"
    assert customer_hits[0].route == f"/customers/{customer.id}"


@pytest.mark.asyncio
async def test_search_module_record_by_description(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    token = f"UNIQUE-DESC-{suffix}"
    record = ModuleRecord(
        module_code="finance",
        feature_code="general_ledger",
        reference=f"SRCH-DESC-{suffix}",
        title="Ledger entry title",
        description=f"Internal note {token}",
        status="DRAFT",
    )
    seeded_db.add(record)
    await seeded_db.commit()

    results = await unified_search(
        seeded_db,
        query=token,
        permissions={"finance.records.read"},
        limit=10,
    )
    module_hits = [r for r in results if r.entity_type == "module_record" and r.entity_id == record.id]
    assert len(module_hits) == 1


@pytest.mark.asyncio
async def test_search_module_record_by_extra_data(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    token = f"UNIQUE-ITEM-{suffix}"
    record = ModuleRecord(
        module_code="procurement",
        feature_code="purchase_orders",
        reference=f"SRCH-JSON-{suffix}",
        title="PO seed record",
        status="DRAFT",
        extra_data={"line_items": [{"item_code": token}]},
    )
    seeded_db.add(record)
    await seeded_db.commit()

    results = await unified_search(
        seeded_db,
        query=token,
        permissions={"procurement.records.read"},
        limit=10,
    )
    module_hits = [r for r in results if r.entity_type == "module_record" and r.entity_id == record.id]
    assert len(module_hits) == 1
