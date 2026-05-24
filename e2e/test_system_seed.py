"""Selenium whole-system data seed — drives the ERP UI via WebDriver."""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest

from helpers.inventory_api import create_inventory_item
from helpers.reporting import SeedReport, utc_now_iso, write_report
from helpers.seed_masters import FlowSeedMasters
from helpers.seed_runner import run_seed_type
from helpers.selenium_masters import seed_system_masters_selenium
from pages.bom import BomPage
from pages.crm import CrmPage
from pages.customers import CustomersPage
from pages.inventory import InventoryPage
from pages.layout import AppLayout
from pages.manufacturing import ManufacturingPage
from pages.module_hub import ModuleHubPage
from pages.module_record import ModuleRecordPage
from pages.pos import PosPage
from pages.procurement import ProcurementPage
from pages.purchases import PurchasesPage
from pages.sales import SalesPage
from pages.suppliers import SuppliersPage
from pages.tms import TmsPage
from pages.warehouses import LocationsPage, WarehousesPage

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

SEED_COUNT = int(os.getenv("E2E_SEED_COUNT", os.getenv("E2E_DOC_COUNT", "10")))

MODULE_HUB_ROUTES: tuple[tuple[str, str], ...] = (
    ("warehouse_module", "/warehouse"),
    ("sales_distribution", "/sales-distribution"),
    ("projects", "/projects"),
    ("platform", "/platform"),
)

MODULE_RECORD_ROUTES: tuple[tuple[str, str, str], ...] = (
    ("finance", "/finance", "Title / Header Text"),
    ("hcm", "/hcm", "Title / Display name"),
    ("scm", "/scm", "Title / summary"),
)


def _suffix(run_id: str, index: int) -> str:
    return f"{run_id}-{index:03d}"


def _pos_checkout(pos: PosPage, sku: str) -> None:
    pos.open().wait_loaded()
    pos.search_and_add_first(sku)
    pos.checkout()
    pos.wait_receipt_dialog()


def test_seed_whole_system_selenium(
    logged_in_admin: AppLayout,
    driver,
    base_url: str,
    wait_timeout: float,
    api_client,
) -> None:
    started_at = utc_now_iso()
    _ = logged_in_admin
    masters = seed_system_masters_selenium(
        driver,
        base_url=base_url,
        wait_timeout=wait_timeout,
        api_client=api_client,
        bom_parent_count=SEED_COUNT,
    )

    sales = SalesPage(driver, base_url, wait_timeout)
    procurement = ProcurementPage(driver, base_url, wait_timeout)
    purchases = PurchasesPage(driver, base_url, wait_timeout)
    inventory = InventoryPage(driver, base_url, wait_timeout)
    bom = BomPage(driver, base_url, wait_timeout)
    manufacturing = ManufacturingPage(driver, base_url, wait_timeout)
    customers = CustomersPage(driver, base_url, wait_timeout)
    suppliers = SuppliersPage(driver, base_url, wait_timeout)
    warehouses = WarehousesPage(driver, base_url, wait_timeout)
    locations = LocationsPage(driver, base_url, wait_timeout)
    module_hub = ModuleHubPage(driver, base_url, wait_timeout)
    module_record = ModuleRecordPage(driver, base_url, wait_timeout)
    crm = CrmPage(driver, base_url, wait_timeout)
    pos = PosPage(driver, base_url, wait_timeout)
    tms = TmsPage(driver, base_url, wait_timeout)

    seed_specs: list[tuple[str, str, Callable[[], Callable[[int], None]]]] = [
        (
            "customer",
            "Customer",
            lambda: (
                lambda index: customers.create_customer(
                    name=f"E2E Customer {_suffix(masters.run_id, index)}",
                    code=f"E2E-CUST-{_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "supplier",
            "Supplier / Vendor",
            lambda: (
                lambda index: suppliers.create_supplier(
                    vendor_code=f"E2E-VND-{_suffix(masters.run_id, index)}",
                    name=f"E2E Vendor {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "warehouse",
            "Warehouse",
            lambda: (
                lambda index: warehouses.create_warehouse(
                    code=f"WH-{_suffix(masters.run_id, index)}",
                    name=f"E2E Warehouse {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "location",
            "Warehouse Location",
            lambda: (
                lambda index: locations.create_location(
                    code=f"LOC-{_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "sales_order",
            "Sales Order",
            lambda: (
                lambda index: sales.open().create_sales_order(
                    customer_id=masters.customer_id,
                    product_sku=masters.sellable_sku,
                )
            ),
        ),
        (
            "purchase_requisition",
            "Purchase Requisition",
            lambda: (
                lambda index: procurement.open(feature="purchase_requisitions").create_procurement_record(
                    title=f"E2E PR {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "purchase_order_procurement",
            "Procurement PO Record",
            lambda: (
                lambda index: procurement.open(feature="purchase_orders").create_procurement_record(
                    title=f"E2E PO {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "grn",
            "Goods Receipt (GRN)",
            lambda: (
                lambda index: procurement.open(feature="goods_receipt").create_procurement_record(
                    title=f"E2E GRN {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "invoice_matching",
            "Invoice Matching",
            lambda: (
                lambda index: procurement.open(feature="invoice_matching").create_procurement_record(
                    title=f"E2E INV-MATCH {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "purchase_order",
            "Purchase (Quick Receive)",
            lambda: (
                lambda index: purchases.open().create_purchase(
                    supplier_id=masters.supplier_id,
                    product_sku=masters.sellable_sku,
                )
            ),
        ),
        (
            "pos_sale",
            "POS Checkout",
            lambda: (
                lambda index: _pos_checkout(pos, masters.sellable_sku)
            ),
        ),
        (
            "trading_inventory",
            "Trading Inventory",
            lambda: (
                lambda index: inventory.open().create_item(
                    sku=f"E2E-TRD-{_suffix(masters.run_id, index)}",
                    name=f"E2E Trading {_suffix(masters.run_id, index)}",
                    item_type="TRADING",
                )
            ),
        ),
        (
            "raw_material_inventory",
            "Raw Material Inventory",
            lambda: (
                lambda index: create_inventory_item(
                    api_client,
                    sku=f"E2E-RAW-{_suffix(masters.run_id, index)}",
                    name=f"E2E Raw {_suffix(masters.run_id, index)}",
                    item_type="RAW",
                    initial_stock=100,
                    cost_price="3.00",
                )
            ),
        ),
        (
            "finished_goods_inventory",
            "Finished Goods Inventory",
            lambda: (
                lambda index: create_inventory_item(
                    api_client,
                    sku=f"E2E-FG-INV-{_suffix(masters.run_id, index)}",
                    name=f"E2E Finished {_suffix(masters.run_id, index)}",
                    item_type="FINISHED",
                    initial_stock=50,
                    price="25.00",
                    cost_price="12.00",
                )
            ),
        ),
        (
            "bill_of_materials",
            "Bill of Materials",
            lambda: (
                lambda index: bom.open().create_bom(
                    parent_sku=masters.bom_parent_skus[index - 1],
                    component_sku=masters.bom_component_sku,
                )
            ),
        ),
        (
            "work_order",
            "Production Order",
            lambda: (
                lambda index: manufacturing.open().create_production_order(
                    product_id=masters.sellable_product_id,
                )
            ),
        ),
        (
            "crm_lead",
            "CRM Lead",
            lambda: (
                lambda index: crm.create_lead(
                    company_name=f"E2E Lead Co {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "crm_opportunity",
            "CRM Opportunity",
            lambda: (
                lambda index: crm.create_opportunity(
                    title=f"E2E Opp {_suffix(masters.run_id, index)}",
                    customer_id=masters.customer_id,
                )
            ),
        ),
        (
            "crm_campaign",
            "CRM Marketing Campaign",
            lambda: (
                lambda index: crm.add_module_record(
                    feature_button="Marketing Campaigns",
                    title=f"E2E Campaign {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "tms_shipment",
            "TMS Shipment",
            lambda: (
                lambda index: tms.create_shipment(title=f"E2E Shipment {_suffix(masters.run_id, index)}")
            ),
        ),
    ]

    for module_type, route in MODULE_HUB_ROUTES:
        seed_specs.append(
            (
                f"module_{module_type}",
                f"Module hub ({module_type})",
                lambda mod=module_type, r=route: (
                    lambda index, m=mod, path=r: module_hub.open(path).add_record(
                        title=f"E2E {m} {_suffix(masters.run_id, index)}",
                    )
                ),
            ),
        )

    for module_type, route, title_label in MODULE_RECORD_ROUTES:
        seed_specs.append(
            (
                f"module_{module_type}",
                f"Module records ({module_type})",
                lambda mod=module_type, r=route, lbl=title_label: (
                    lambda index, m=mod, path=r, label=lbl: module_record.open(path).create_record(
                        title=f"E2E {m} {_suffix(masters.run_id, index)}",
                        title_label=label,
                    )
                ),
            ),
        )

    type_results = []
    for document_type, label, factory in seed_specs:
        type_results.append(
            run_seed_type(
                driver=driver,
                document_type=document_type,
                label=label,
                count=SEED_COUNT,
                create_fn=factory(),
            ),
        )

    finished_at = utc_now_iso()
    report = SeedReport(
        started_at=started_at,
        finished_at=finished_at,
        document_count_per_type=SEED_COUNT,
        type_results=type_results,
    )
    json_path, md_path = write_report(report, basename="system_seed_report")

    assert report.total_failed == 0, (
        f"System seed completed with {report.total_failed} failure(s). "
        f"See {md_path} and {json_path}."
    )
