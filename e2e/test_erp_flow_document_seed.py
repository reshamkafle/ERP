"""Selenium ERPFlow document seed — 20+ records per creatable document type."""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest

from helpers.erp_documents import create_erp_document
from helpers.reporting import SeedReport, utc_now_iso, write_report
from helpers.seed_runner import run_seed_type
from helpers.seed_masters import FlowSeedMasters
from pages.bom import BomPage
from pages.inventory import InventoryPage
from pages.layout import AppLayout
from pages.manufacturing import ManufacturingPage
from pages.procurement import ProcurementPage
from pages.purchases import PurchasesPage
from pages.sales import SalesPage

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

DOCUMENT_COUNT = int(os.getenv("E2E_DOC_COUNT", "20"))


def _suffix(run_id: str, index: int) -> str:
    return f"{run_id}-{index:03d}"


def test_seed_erp_flow_documents(
    logged_in_admin: AppLayout,
    driver,
    base_url: str,
    wait_timeout: float,
    flow_seed_masters: FlowSeedMasters,
    api_client,
) -> None:
    started_at = utc_now_iso()
    masters = flow_seed_masters
    _ = logged_in_admin

    sales = SalesPage(driver, base_url, wait_timeout)
    procurement = ProcurementPage(driver, base_url, wait_timeout)
    purchases = PurchasesPage(driver, base_url, wait_timeout)
    inventory = InventoryPage(driver, base_url, wait_timeout)
    bom = BomPage(driver, base_url, wait_timeout)
    manufacturing = ManufacturingPage(driver, base_url, wait_timeout)

    seed_specs: list[tuple[str, str, Callable[[], Callable[[int], None]]]] = [
        (
            "sales_order",
            "Sales Order",
            lambda: (
                lambda index: (
                    sales.open().create_sales_order(
                        customer_id=masters.customer_id,
                        product_sku=masters.sellable_sku,
                    )
                )
            ),
        ),
        (
            "purchase_requisition",
            "Purchase Requisition",
            lambda: (
                lambda index: procurement.open_purchase_requisitions().create_purchase_requisition(
                    title=f"E2E PR {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "purchase_order",
            "Purchase Order",
            lambda: (
                lambda index: purchases.open().create_purchase(
                    supplier_id=masters.supplier_id,
                    product_sku=masters.sellable_sku,
                )
            ),
        ),
        (
            "grn",
            "Goods Receipt Note",
            lambda: (
                lambda index: procurement.open(feature="goods_receipt").create_procurement_record(
                    title=f"E2E GRN {_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "raw_material_inventory",
            "Raw Material Inventory",
            lambda: (
                lambda index: inventory.open(item_type="RAW").create_item(
                    sku=f"E2E-RAW-{_suffix(masters.run_id, index)}",
                    name=f"E2E Raw {_suffix(masters.run_id, index)}",
                    item_type="RAW",
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
            "Work Order",
            lambda: (
                lambda index: manufacturing.open().create_production_order(
                    product_id=masters.sellable_product_id,
                )
            ),
        ),
        (
            "quality_inspection",
            "Quality Inspection",
            lambda: (
                lambda index: create_erp_document(
                    api_client,
                    document_type="INSPECTION_REPORT",
                    title=f"E2E QC {_suffix(masters.run_id, index)}",
                    reference_number=f"QC-{_suffix(masters.run_id, index)}",
                )
            ),
        ),
        (
            "finished_goods_inventory",
            "Finished Goods Inventory",
            lambda: (
                lambda index: inventory.open(item_type="FINISHED").create_item(
                    sku=f"E2E-FG-INV-{_suffix(masters.run_id, index)}",
                    name=f"E2E Finished {_suffix(masters.run_id, index)}",
                    item_type="FINISHED",
                )
            ),
        ),
        (
            "sales_invoice",
            "Sales Invoice",
            lambda: (
                lambda index: create_erp_document(
                    api_client,
                    document_type="OUTGOING_INVOICE",
                    title=f"E2E Invoice {_suffix(masters.run_id, index)}",
                    reference_number=f"INV-{_suffix(masters.run_id, index)}",
                )
            ),
        ),
    ]

    type_results = []
    for document_type, label, factory in seed_specs:
        type_results.append(
            run_seed_type(
                driver=driver,
                document_type=document_type,
                label=label,
                count=DOCUMENT_COUNT,
                create_fn=factory(),
            ),
        )

    finished_at = utc_now_iso()
    report = SeedReport(
        started_at=started_at,
        finished_at=finished_at,
        document_count_per_type=DOCUMENT_COUNT,
        type_results=type_results,
    )
    json_path, md_path = write_report(report)

    assert report.total_failed == 0, (
        f"ERPFlow seed completed with {report.total_failed} failure(s). "
        f"See {md_path} and {json_path}."
    )
