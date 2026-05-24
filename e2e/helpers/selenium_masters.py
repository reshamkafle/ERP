"""Session master data created through the ERP UI (Selenium WebDriver)."""

from __future__ import annotations

import uuid

from selenium.webdriver.chrome.webdriver import WebDriver

from helpers.seed_masters import FlowSeedMasters, _seed_manufacturing_items
from pages.customers import CustomersPage
from pages.suppliers import SuppliersPage
from pages.warehouses import WarehousesPage
import httpx


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def seed_system_masters_selenium(
    driver: WebDriver,
    *,
    base_url: str,
    wait_timeout: float,
    api_client: httpx.Client,
    bom_parent_count: int = 20,
) -> FlowSeedMasters:
    """Create customer, supplier, and warehouse via UI; stock SKUs via API; BOM SKUs via DB helper."""
    run_id = uuid.uuid4().hex[:8].upper()
    customers = CustomersPage(driver, base_url, wait_timeout)
    suppliers = SuppliersPage(driver, base_url, wait_timeout)
    warehouses = WarehousesPage(driver, base_url, wait_timeout)

    customer_name = f"E2E Seed Customer {run_id}"
    customer_code = f"E2E-C-{run_id}"
    customer_id = customers.create_customer(name=customer_name, code=customer_code)

    vendor_code = f"E2E-V-{run_id}"
    supplier_name = f"E2E Seed Supplier {run_id}"
    supplier_id = suppliers.create_supplier(vendor_code=vendor_code, name=supplier_name)

    warehouses.create_warehouse(code=f"WH-{run_id}", name=f"E2E Warehouse {run_id}")

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
    import asyncio

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
