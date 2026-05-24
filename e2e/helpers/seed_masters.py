"""Session master-data seeding for ERPFlow Selenium tests."""

from __future__ import annotations

import asyncio
import sys
import uuid
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@dataclass
class FlowSeedMasters:
    run_id: str
    customer_id: int
    supplier_id: int
    sellable_product_id: int
    sellable_sku: str
    raw_sku: str
    bom_parent_skus: list[str]
    bom_component_sku: str


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def seed_flow_masters(api_client: httpx.Client, *, bom_parent_count: int = 20) -> FlowSeedMasters:
    run_id = uuid.uuid4().hex[:8].upper()

    customer_res = api_client.post(
        "/api/v1/customers",
        json={
            "name": f"E2E Flow Customer {run_id}",
            "customer_code": f"E2E-C-{run_id}",
            "currency_code": "USD",
        },
    )
    customer_res.raise_for_status()
    customer_id = customer_res.json()["id"]

    supplier_code = f"E2E-V-{run_id}"
    supplier_res = api_client.post(
        "/api/v1/suppliers",
        json={
            "vendor_code": supplier_code,
            "name": f"E2E Flow Supplier {run_id}",
            "currency_code": "USD",
        },
    )
    supplier_res.raise_for_status()
    supplier_id = supplier_res.json()["id"]

    sellable_sku = _unique("E2E-SELL")
    sellable_res = api_client.post(
        "/api/v1/inventory",
        json={
            "sku": sellable_sku,
            "name": f"E2E Sellable {run_id}",
            "lifecycle_status": "ACTIVE",
            "item_type": "TRADING",
            "initial_stock": 100,
            "price": "15.00",
            "cost_price": "7.50",
            "low_stock_threshold": 5,
            "default_supplier_id": supplier_id,
        },
    )
    sellable_res.raise_for_status()
    sellable_product_id = sellable_res.json()["id"]

    raw_sku = _unique("E2E-RAW")
    raw_res = api_client.post(
        "/api/v1/inventory",
        json={
            "sku": raw_sku,
            "name": f"E2E Raw Material {run_id}",
            "lifecycle_status": "ACTIVE",
            "item_type": "RAW",
            "initial_stock": 500,
            "price": "0",
            "cost_price": "3.00",
            "low_stock_threshold": 10,
        },
    )
    raw_res.raise_for_status()

    bom_component_sku = f"E2E-COMP-{run_id}"
    bom_parent_skus = asyncio.run(
        _seed_manufacturing_items(run_id, bom_component_sku, bom_parent_count),
    )

    return FlowSeedMasters(
        run_id=run_id,
        customer_id=customer_id,
        supplier_id=supplier_id,
        sellable_product_id=sellable_product_id,
        sellable_sku=sellable_sku,
        raw_sku=raw_sku,
        bom_parent_skus=bom_parent_skus,
        bom_component_sku=bom_component_sku,
    )


async def _seed_manufacturing_items(
    run_id: str,
    component_sku: str,
    parent_count: int,
) -> list[str]:
    from app.core.database import AsyncSessionLocal
    from app.crud.bom import get_item_by_sku, insert_item
    from app.manufacturing.bom.enums import ItemCategory, UnitOfMeasure

    parent_skus: list[str] = []
    async with AsyncSessionLocal() as session:
        if await get_item_by_sku(session, component_sku) is None:
            await insert_item(
                session,
                sku=component_sku,
                name=f"E2E BOM Component {run_id}",
                category=ItemCategory.FABRIC,
                unit=UnitOfMeasure.METER,
                cost_per_unit=Decimal("2.50"),
            )

        for index in range(parent_count):
            sku = f"E2E-FG-{run_id}-{index:03d}"
            if await get_item_by_sku(session, sku) is None:
                await insert_item(
                    session,
                    sku=sku,
                    name=f"E2E Finished Style {run_id}-{index:03d}",
                    category=ItemCategory.FINISHED_GOOD,
                    unit=UnitOfMeasure.PIECE,
                    cost_per_unit=Decimal("0"),
                )
            parent_skus.append(sku)

        await session.commit()

    return parent_skus
