"""Material roll / lot tracking for fabric and raw materials

Revision ID: v9x1y3z5a724
Revises: u8w0y2a4b623
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "v9x1y3z5a724"
down_revision: Union[str, None] = "u8w0y2a4b623"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "material_rolls" in inspector.get_table_names():
        return

    for name, values in [
        ("materialrollstatus", ["IN_STOCK", "ALLOCATED", "IN_PRODUCTION", "ON_HOLD", "QUARANTINED", "REJECTED", "SHIPPED"]),
        ("materialfinishtype", ["GREIGE", "DYED", "PRINTED", "FINISHED", "OTHER"]),
        ("materialrollmovementtype", ["RECEIPT", "TRANSFER", "ISSUE", "RETURN", "ADJUSTMENT", "ALLOCATE", "DEALLOCATE", "SHIP", "QUARANTINE", "CYCLE_COUNT"]),
        ("materialrollallocationstatus", ["ACTIVE", "CONSUMED", "RELEASED"]),
    ]:
        sa.Enum(*values, name=name).create(bind, checkfirst=True)

    op.add_column(
        "products",
        sa.Column("roll_tracking_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "material_rolls",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("roll_number", sa.String(length=64), nullable=False),
        sa.Column("barcode", sa.String(length=64), nullable=True),
        sa.Column("rfid_tag", sa.String(length=128), nullable=True),
        sa.Column("serial_number", sa.String(length=128), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("material_type", sa.String(length=120), nullable=True),
        sa.Column("composition", sa.String(length=255), nullable=True),
        sa.Column("color", sa.String(length=64), nullable=True),
        sa.Column("dye_lot", sa.String(length=64), nullable=True),
        sa.Column("pattern", sa.String(length=120), nullable=True),
        sa.Column("gsm", sa.Numeric(10, 2), nullable=True),
        sa.Column("width", sa.Numeric(12, 4), nullable=True),
        sa.Column("thickness", sa.Numeric(12, 4), nullable=True),
        sa.Column("grade", sa.String(length=32), nullable=True),
        sa.Column(
            "finish_type",
            sa.Enum("GREIGE", "DYED", "PRINTED", "FINISHED", "OTHER", name="materialfinishtype", create_type=False),
            nullable=True,
        ),
        sa.Column("initial_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("remaining_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("initial_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("remaining_weight_kg", sa.Numeric(14, 4), nullable=True),
        sa.Column("primary_uom", sa.String(length=32), nullable=False),
        sa.Column("secondary_uom", sa.String(length=32), nullable=True),
        sa.Column("conversion_factor", sa.Numeric(12, 4), nullable=True),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("supplier_lot_number", sa.String(length=64), nullable=True),
        sa.Column("purchase_id", sa.Integer(), nullable=True),
        sa.Column("purchase_item_id", sa.Integer(), nullable=True),
        sa.Column("po_number", sa.String(length=64), nullable=True),
        sa.Column("grn_reference", sa.String(length=64), nullable=True),
        sa.Column("invoice_number", sa.String(length=64), nullable=True),
        sa.Column("receipt_date", sa.Date(), nullable=True),
        sa.Column("unit_cost", sa.Numeric(12, 4), nullable=True),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("manufacture_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "IN_STOCK",
                "ALLOCATED",
                "IN_PRODUCTION",
                "ON_HOLD",
                "QUARANTINED",
                "REJECTED",
                "SHIPPED",
                name="materialrollstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("warehouse_id", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=True),
        sa.Column(
            "quality_status",
            sa.Enum("QUARANTINE", "APPROVED", "REJECTED", name="stockqualitystatus", create_type=False),
            nullable=False,
        ),
        sa.Column("inspection_passed", sa.Boolean(), nullable=True),
        sa.Column("inspection_notes", sa.Text(), nullable=True),
        sa.Column("certifications", postgresql.JSONB(), nullable=True),
        sa.Column("defect_log", postgresql.JSONB(), nullable=True),
        sa.Column("shrinkage_test_data", postgresql.JSONB(), nullable=True),
        sa.Column("reserved_for_type", sa.String(length=32), nullable=True),
        sa.Column("reserved_for_id", sa.Integer(), nullable=True),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("custom_attributes", postgresql.JSONB(), nullable=True),
        sa.Column("attachments", postgresql.JSONB(), nullable=True),
        sa.Column("last_scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scanned_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["purchase_item_id"], ["purchase_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["location_id"], ["storage_locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["last_scanned_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("roll_number"),
    )
    op.create_index("ix_material_rolls_barcode", "material_rolls", ["barcode"])
    op.create_index("ix_material_rolls_rfid_tag", "material_rolls", ["rfid_tag"])
    op.create_index("ix_material_rolls_product_status", "material_rolls", ["product_id", "status"])

    op.create_table(
        "material_roll_movements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("material_roll_id", sa.Integer(), nullable=False),
        sa.Column(
            "movement_type",
            sa.Enum(
                "RECEIPT",
                "TRANSFER",
                "ISSUE",
                "RETURN",
                "ADJUSTMENT",
                "ALLOCATE",
                "DEALLOCATE",
                "SHIP",
                "QUARANTINE",
                "CYCLE_COUNT",
                name="materialrollmovementtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("quantity_delta", sa.Numeric(14, 4), nullable=False),
        sa.Column("uom", sa.String(length=32), nullable=False),
        sa.Column("from_warehouse_id", sa.Integer(), nullable=True),
        sa.Column("to_warehouse_id", sa.Integer(), nullable=True),
        sa.Column("from_location_id", sa.Integer(), nullable=True),
        sa.Column("to_location_id", sa.Integer(), nullable=True),
        sa.Column("reference_type", sa.String(length=32), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("reference_document", sa.String(length=128), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("transaction_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["material_roll_id"], ["material_rolls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["from_location_id"], ["storage_locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_location_id"], ["storage_locations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "material_roll_inspections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("material_roll_id", sa.Integer(), nullable=False),
        sa.Column("inspector_name", sa.String(length=120), nullable=True),
        sa.Column("inspected_by_id", sa.Integer(), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("test_parameters", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["material_roll_id"], ["material_rolls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inspected_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "material_roll_allocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("material_roll_id", sa.Integer(), nullable=False),
        sa.Column("reference_type", sa.String(length=32), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=False),
        sa.Column("allocated_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("consumed_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "CONSUMED", "RELEASED", name="materialrollallocationstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["material_roll_id"], ["material_rolls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "inventory_transactions",
        sa.Column("quantity_decimal", sa.Numeric(14, 4), nullable=True),
    )
    op.add_column(
        "inventory_transactions",
        sa.Column("material_roll_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_inventory_transactions_material_roll",
        "inventory_transactions",
        "material_rolls",
        ["material_roll_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "production_material_issues",
        sa.Column("material_roll_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_production_material_issues_material_roll",
        "production_material_issues",
        "material_rolls",
        ["material_roll_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("purchase_items", sa.Column("rolls_expected", sa.Integer(), nullable=True))
    op.add_column("purchase_items", sa.Column("receipt_metadata", postgresql.JSONB(), nullable=True))

    op.add_column("cut_order_fabric_allocations", sa.Column("material_roll_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_cut_order_fabric_alloc_material_roll",
        "cut_order_fabric_allocations",
        "material_rolls",
        ["material_roll_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_constraint("uq_stock_balances_product_wh_loc", "stock_balances", type_="unique")
    op.create_unique_constraint(
        "uq_stock_balances_product_wh_loc_lot",
        "stock_balances",
        ["product_id", "warehouse_id", "location_id", "lot_number"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "material_rolls" not in inspector.get_table_names():
        return

    op.drop_constraint("uq_stock_balances_product_wh_loc_lot", "stock_balances", type_="unique")
    op.create_unique_constraint(
        "uq_stock_balances_product_wh_loc",
        "stock_balances",
        ["product_id", "warehouse_id", "location_id"],
    )

    op.drop_constraint("fk_cut_order_fabric_alloc_material_roll", "cut_order_fabric_allocations", type_="foreignkey")
    op.drop_column("cut_order_fabric_allocations", "material_roll_id")

    op.drop_column("purchase_items", "receipt_metadata")
    op.drop_column("purchase_items", "rolls_expected")

    op.drop_constraint("fk_production_material_issues_material_roll", "production_material_issues", type_="foreignkey")
    op.drop_column("production_material_issues", "material_roll_id")

    op.drop_constraint("fk_inventory_transactions_material_roll", "inventory_transactions", type_="foreignkey")
    op.drop_column("inventory_transactions", "material_roll_id")
    op.drop_column("inventory_transactions", "quantity_decimal")

    op.drop_table("material_roll_allocations")
    op.drop_table("material_roll_inspections")
    op.drop_table("material_roll_movements")
    op.drop_table("material_rolls")

    op.drop_column("products", "roll_tracking_enabled")

    for name in (
        "materialrollallocationstatus",
        "materialrollmovementtype",
        "materialfinishtype",
        "materialrollstatus",
    ):
        sa.Enum(name=name).drop(bind, checkfirst=True)
