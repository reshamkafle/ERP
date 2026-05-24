"""Build read-only product snapshots for BOM lines via manufacturing_items.product_id."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.models.manufacturing import ManufacturingItem
from app.models.product import Product


class ProductSnapshot(BaseModel):
    product_id: int
    sku: str
    name: str
    description: str | None = None
    primary_uom: str
    standard_cost: Decimal | None = None
    cost_price: Decimal
    item_type: str
    default_supplier_id: int | None = None
    default_supplier_name: str | None = None
    country_of_origin: str | None = None
    hs_code: str | None = None
    gross_weight: Decimal | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    volume: Decimal | None = None
    batch_lot_flag: bool = False
    serial_number_flag: bool = False
    shelf_life_days: int | None = None
    lead_time_days: int | None = None


def product_snapshot_from_row(row: ManufacturingItem | None) -> ProductSnapshot | None:
    if row is None or row.product_id is None:
        return None
    product: Product | None = row.product
    if product is None:
        return None
    supplier_name = None
    if product.default_supplier is not None:
        supplier_name = product.default_supplier.name
    return ProductSnapshot(
        product_id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        primary_uom=product.primary_uom,
        standard_cost=product.standard_cost,
        cost_price=product.cost_price,
        item_type=product.item_type.value if hasattr(product.item_type, "value") else str(product.item_type),
        default_supplier_id=product.default_supplier_id,
        default_supplier_name=supplier_name,
        country_of_origin=product.country_of_origin,
        hs_code=product.hs_code,
        gross_weight=product.gross_weight,
        length=product.length,
        width=product.width,
        height=product.height,
        volume=product.volume,
        batch_lot_flag=product.batch_lot_flag,
        serial_number_flag=product.serial_number_flag,
        shelf_life_days=product.shelf_life_days,
        lead_time_days=product.lead_time_days,
    )
