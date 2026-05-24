"""inventory warehouse expansion (phases 1-4)

Revision ID: j4k6l8m0n012
Revises: i3j5k7l9m011
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "j4k6l8m0n012"
down_revision: Union[str, None] = "i3j5k7l9m011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _enum(name: str, *values: str) -> postgresql.ENUM:
    """ENUM type created once in upgrade(); columns use create_type=False."""
    return postgresql.ENUM(*values, name=name, create_type=False)


abcclass = _enum("abcclass", "A", "B", "C")
xyzclass = _enum("xyzclass", "FAST", "SLOW", "NON_MOVING")
costvaluationmethod = _enum(
    "costvaluationmethod", "STANDARD", "AVERAGE", "LAST_PURCHASE", "FIFO", "LIFO"
)
warehousetype = _enum(
    "warehousetype", "MAIN", "DISTRIBUTION", "PRODUCTION", "COLD_STORAGE", "THIRD_PARTY", "OTHER"
)
warehousestatus = _enum("warehousestatus", "ACTIVE", "INACTIVE")
storagelocationtype = _enum(
    "storagelocationtype", "BULK", "PICKING", "RECEIVING", "SHIPPING", "QUARANTINE", "STAGING", "OTHER"
)
storagelocationstatus = _enum("storagelocationstatus", "AVAILABLE", "BLOCKED", "DAMAGED")
stockqualitystatus = _enum("stockqualitystatus", "QUARANTINE", "APPROVED", "REJECTED")
inventorytransactiontype = _enum(
    "inventorytransactiontype",
    "RECEIPT",
    "ISSUE",
    "TRANSFER",
    "ADJUSTMENT",
    "WRITE_OFF",
    "CYCLE_COUNT",
)

_ALL_ENUMS = (
    abcclass,
    xyzclass,
    costvaluationmethod,
    warehousetype,
    warehousestatus,
    storagelocationtype,
    storagelocationstatus,
    stockqualitystatus,
    inventorytransactiontype,
)


def _create_enums(bind) -> None:
    for enum_type in _ALL_ENUMS:
        postgresql.ENUM(*enum_type.enums, name=enum_type.name, create_type=True).create(
            bind, checkfirst=True
        )


def _has_table(bind, name: str) -> bool:
    return inspect(bind).has_table(name)


def _has_column(bind, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(bind).get_columns(table)}


def _has_fk(bind, table: str, fk_name: str) -> bool:
    return fk_name in {fk["name"] for fk in inspect(bind).get_foreign_keys(table)}


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'SEMI_FINISHED'")
    op.execute("ALTER TYPE itemtype ADD VALUE IF NOT EXISTS 'CONSUMABLE'")

    _create_enums(bind)

    if not _has_table(bind, "warehouses"):
        op.create_table(
            "warehouses",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(length=32), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("warehouse_type", warehousetype, nullable=False),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("capacity_weight", sa.Numeric(14, 4), nullable=True),
            sa.Column("capacity_volume", sa.Numeric(14, 4), nullable=True),
            sa.Column("capacity_pallets", sa.Integer(), nullable=True),
            sa.Column("status", warehousestatus, nullable=False),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("wave_picking_enabled", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("cross_docking_enabled", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("cycle_count_frequency", sa.String(length=64), nullable=True),
            sa.Column("cycle_count_class", sa.String(length=32), nullable=True),
            sa.Column("packing_rules", postgresql.JSONB(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code"),
        )
        op.create_index("ix_warehouses_code", "warehouses", ["code"], unique=True)

    if not _has_table(bind, "storage_locations"):
        op.create_table(
            "storage_locations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(length=64), nullable=False),
            sa.Column("warehouse_id", sa.Integer(), nullable=False),
            sa.Column("aisle", sa.String(length=32), nullable=True),
            sa.Column("row", sa.String(length=32), nullable=True),
            sa.Column("column", sa.String(length=32), nullable=True),
            sa.Column("level", sa.String(length=32), nullable=True),
            sa.Column("location_type", storagelocationtype, nullable=False),
            sa.Column("capacity", sa.Numeric(14, 4), nullable=True),
            sa.Column("putaway_strategy", sa.String(length=64), nullable=True),
            sa.Column("picking_strategy", sa.String(length=64), nullable=True),
            sa.Column("status", storagelocationstatus, nullable=False),
            sa.Column("zone", sa.String(length=64), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("warehouse_id", "code", name="uq_storage_locations_warehouse_code"),
        )
        op.create_index("ix_storage_locations_warehouse_id", "storage_locations", ["warehouse_id"])

    product_columns: list[tuple[str, sa.Column]] = [
        ("qr_code", sa.Column("qr_code", sa.String(length=128), nullable=True)),
        ("rfid_tag", sa.Column("rfid_tag", sa.String(length=128), nullable=True)),
        ("purchase_uom", sa.Column("purchase_uom", sa.String(length=32), nullable=True)),
        ("sales_uom", sa.Column("sales_uom", sa.String(length=32), nullable=True)),
        ("shelf_life_days", sa.Column("shelf_life_days", sa.Integer(), nullable=True)),
        (
            "batch_management_enabled",
            sa.Column(
                "batch_management_enabled",
                sa.Boolean(),
                nullable=False,
                server_default="false",
            ),
        ),
        ("abc_class", sa.Column("abc_class", abcclass, nullable=True)),
        ("xyz_class", sa.Column("xyz_class", xyzclass, nullable=True)),
        ("standard_cost", sa.Column("standard_cost", sa.Numeric(12, 2), nullable=True)),
        ("cost_valuation_method", sa.Column("cost_valuation_method", costvaluationmethod, nullable=True)),
        (
            "reorder_level",
            sa.Column("reorder_level", sa.Integer(), nullable=False, server_default="0"),
        ),
        ("max_stock_level", sa.Column("max_stock_level", sa.Integer(), nullable=True)),
        ("economic_order_qty", sa.Column("economic_order_qty", sa.Integer(), nullable=True)),
        ("lead_time_days", sa.Column("lead_time_days", sa.Integer(), nullable=True)),
        (
            "reorder_point",
            sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="0"),
        ),
        (
            "safety_stock_level",
            sa.Column("safety_stock_level", sa.Integer(), nullable=False, server_default="0"),
        ),
        ("min_order_qty", sa.Column("min_order_qty", sa.Integer(), nullable=True)),
        ("max_order_qty", sa.Column("max_order_qty", sa.Integer(), nullable=True)),
        ("procurement_lead_time_days", sa.Column("procurement_lead_time_days", sa.Integer(), nullable=True)),
        ("demand_forecast_notes", sa.Column("demand_forecast_notes", sa.Text(), nullable=True)),
        (
            "quality_inspection_required",
            sa.Column(
                "quality_inspection_required",
                sa.Boolean(),
                nullable=False,
                server_default="false",
            ),
        ),
        ("inspection_checklist", sa.Column("inspection_checklist", postgresql.JSONB(), nullable=True)),
        ("expiry_alert_threshold_days", sa.Column("expiry_alert_threshold_days", sa.Integer(), nullable=True)),
        ("hazardous_material_class", sa.Column("hazardous_material_class", sa.String(length=64), nullable=True)),
        ("regulatory_compliance_codes", sa.Column("regulatory_compliance_codes", sa.Text(), nullable=True)),
        ("image_url", sa.Column("image_url", sa.String(length=512), nullable=True)),
        ("attachments", sa.Column("attachments", postgresql.JSONB(), nullable=True)),
        (
            "created_at",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        ),
        (
            "updated_at",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        ),
        ("created_by_id", sa.Column("created_by_id", sa.Integer(), nullable=True)),
        ("updated_by_id", sa.Column("updated_by_id", sa.Integer(), nullable=True)),
        ("tax_rate_id", sa.Column("tax_rate_id", sa.Integer(), nullable=True)),
        ("default_warehouse_id", sa.Column("default_warehouse_id", sa.Integer(), nullable=True)),
        ("default_location_id", sa.Column("default_location_id", sa.Integer(), nullable=True)),
    ]
    for col_name, column in product_columns:
        if not _has_column(bind, "products", col_name):
            op.add_column("products", column)

    if not _has_fk(bind, "products", "fk_products_tax_rate_id"):
        op.create_foreign_key(
            "fk_products_tax_rate_id",
            "products",
            "tax_rates",
            ["tax_rate_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_fk(bind, "products", "fk_products_created_by_id"):
        op.create_foreign_key(
            "fk_products_created_by_id",
            "products",
            "users",
            ["created_by_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_fk(bind, "products", "fk_products_updated_by_id"):
        op.create_foreign_key(
            "fk_products_updated_by_id",
            "products",
            "users",
            ["updated_by_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_fk(bind, "products", "fk_products_default_warehouse_id"):
        op.create_foreign_key(
            "fk_products_default_warehouse_id",
            "products",
            "warehouses",
            ["default_warehouse_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if not _has_fk(bind, "products", "fk_products_default_location_id"):
        op.create_foreign_key(
            "fk_products_default_location_id",
            "products",
            "storage_locations",
            ["default_location_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if not _has_table(bind, "product_suppliers"):
        op.create_table(
            "product_suppliers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("supplier_id", sa.Integer(), nullable=False),
            sa.Column("vendor_code", sa.String(length=64), nullable=True),
            sa.Column("is_preferred", sa.Boolean(), nullable=False, server_default="false"),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "product_id", "supplier_id", name="uq_product_suppliers_product_supplier"
            ),
        )
        op.create_index("ix_product_suppliers_product_id", "product_suppliers", ["product_id"])

    if not _has_table(bind, "stock_balances"):
        op.create_table(
            "stock_balances",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("warehouse_id", sa.Integer(), nullable=False),
            sa.Column("location_id", sa.Integer(), nullable=True),
            sa.Column("on_hand", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("available", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("reserved", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("in_transit", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("quality_status", stockqualitystatus, nullable=False),
            sa.Column("valuation_method", costvaluationmethod, nullable=True),
            sa.Column("last_transaction_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("expiry_date", sa.Date(), nullable=True),
            sa.Column("lot_number", sa.String(length=64), nullable=True),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["location_id"], ["storage_locations.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "product_id", "warehouse_id", "location_id", name="uq_stock_balances_product_wh_loc"
            ),
        )

    if not _has_table(bind, "inventory_transactions"):
        op.create_table(
            "inventory_transactions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("transaction_type", inventorytransactiontype, nullable=False),
            sa.Column(
                "transaction_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("reference_document", sa.String(length=128), nullable=True),
            sa.Column("from_warehouse_id", sa.Integer(), nullable=True),
            sa.Column("from_location_id", sa.Integer(), nullable=True),
            sa.Column("to_warehouse_id", sa.Integer(), nullable=True),
            sa.Column("to_location_id", sa.Integer(), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("lot_number", sa.String(length=64), nullable=True),
            sa.Column("serial_number", sa.String(length=128), nullable=True),
            sa.Column("unit_cost", sa.Numeric(12, 4), nullable=True),
            sa.Column("reason_code", sa.String(length=64), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("remarks", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["from_warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["from_location_id"], ["storage_locations.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["to_warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["to_location_id"], ["storage_locations.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_inventory_transactions_product_id", "inventory_transactions", ["product_id"]
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _has_table(bind, "inventory_transactions"):
        op.drop_table("inventory_transactions")
    if _has_table(bind, "stock_balances"):
        op.drop_table("stock_balances")
    if _has_table(bind, "product_suppliers"):
        op.drop_table("product_suppliers")
    for fk in (
        "fk_products_default_location_id",
        "fk_products_default_warehouse_id",
        "fk_products_updated_by_id",
        "fk_products_created_by_id",
        "fk_products_tax_rate_id",
    ):
        if _has_fk(bind, "products", fk):
            op.drop_constraint(fk, "products", type_="foreignkey")
    for col in (
        "default_location_id",
        "default_warehouse_id",
        "tax_rate_id",
        "updated_by_id",
        "created_by_id",
        "updated_at",
        "created_at",
        "attachments",
        "image_url",
        "regulatory_compliance_codes",
        "hazardous_material_class",
        "expiry_alert_threshold_days",
        "inspection_checklist",
        "quality_inspection_required",
        "demand_forecast_notes",
        "procurement_lead_time_days",
        "max_order_qty",
        "min_order_qty",
        "safety_stock_level",
        "reorder_point",
        "lead_time_days",
        "economic_order_qty",
        "max_stock_level",
        "reorder_level",
        "cost_valuation_method",
        "standard_cost",
        "xyz_class",
        "abc_class",
        "batch_management_enabled",
        "shelf_life_days",
        "sales_uom",
        "purchase_uom",
        "rfid_tag",
        "qr_code",
    ):
        if _has_column(bind, "products", col):
            op.drop_column("products", col)
    if _has_table(bind, "storage_locations"):
        op.drop_table("storage_locations")
    if _has_table(bind, "warehouses"):
        op.drop_table("warehouses")
    for enum_type in reversed(_ALL_ENUMS):
        postgresql.ENUM(*enum_type.enums, name=enum_type.name, create_type=True).drop(
            bind, checkfirst=True
        )
