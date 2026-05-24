"""Sales order full ERP field coverage

Revision ID: r2s4t6v820
Revises: q1r3s5t7w819, o9p1r3t5v717
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "r2s4t6v820"
down_revision: Union[str, tuple[str, ...], None] = ("q1r3s5t7w819", "o9p1r3t5v717")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DELIVERY_STATUSES = ("NOT_STARTED", "PENDING", "PARTIAL", "COMPLETE", "BLOCKED")
BILLING_STATUSES = ("NOT_INVOICED", "PARTIAL", "INVOICED", "COMPLETE")
SALE_PARTNER_ROLES = (
    "SOLD_TO",
    "SHIP_TO",
    "BILL_TO",
    "PAYER",
    "FORWARDING_AGENT",
    "SALES_EMPLOYEE",
)


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in (
        ("deliverystatus", DELIVERY_STATUSES),
        ("billingstatus", BILLING_STATUSES),
        ("salepartnerrole", SALE_PARTNER_ROLES),
    ):
        postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())
    sales_columns = {c["name"] for c in inspector.get_columns("sales")}
    sale_item_columns = {c["name"] for c in inspector.get_columns("sale_items")}

    def _add_col(table: str, column: sa.Column, known: set[str]) -> None:
        if column.name not in known:
            op.add_column(table, column)
            known.add(column.name)

    delivery_status = _enum("deliverystatus", DELIVERY_STATUSES)
    billing_status = _enum("billingstatus", BILLING_STATUSES)
    partner_role = _enum("salepartnerrole", SALE_PARTNER_ROLES)

    # --- sales header ---
    _add_col("sales", sa.Column("sales_organization", sa.String(32), nullable=True), sales_columns)
    for col in (
        sa.Column("distribution_channel", sa.String(32), nullable=True),
        sa.Column("division", sa.String(32), nullable=True),
        sa.Column("sales_office", sa.String(64), nullable=True),
        sa.Column("sales_group", sa.String(64), nullable=True),
        sa.Column("pricing_procedure", sa.String(64), nullable=True),
        sa.Column("incoterms_location", sa.String(120), nullable=True),
        sa.Column(
            "shipping_point_id",
            sa.Integer(),
            sa.ForeignKey("warehouses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("requested_delivery_date", sa.Date(), nullable=True),
        sa.Column("customer_po_number", sa.String(64), nullable=True),
        sa.Column("customer_po_date", sa.Date(), nullable=True),
        sa.Column("complete_delivery_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "opportunity_id",
            sa.Integer(),
            sa.ForeignKey("crm_opportunities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("campaign_id", sa.String(64), nullable=True),
        sa.Column("price_group", sa.String(64), nullable=True),
        sa.Column("shipping_conditions", sa.String(64), nullable=True),
        sa.Column("transportation_group", sa.String(64), nullable=True),
        sa.Column("loading_group", sa.String(64), nullable=True),
        sa.Column("header_text", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    ):
        _add_col("sales", col, sales_columns)

    if "delivery_status_enum" not in sales_columns and "delivery_status" in sales_columns:
        op.execute(
            """
            UPDATE sales SET delivery_status = 'PENDING'
            WHERE delivery_status IS NOT NULL AND delivery_status NOT IN (
                'NOT_STARTED', 'PENDING', 'PARTIAL', 'COMPLETE', 'BLOCKED'
            )
            """
        )
        op.execute(
            """
            UPDATE sales SET invoice_status = 'NOT_INVOICED'
            WHERE invoice_status IS NOT NULL AND invoice_status NOT IN (
                'NOT_INVOICED', 'PARTIAL', 'INVOICED', 'COMPLETE'
            )
            """
        )
        _add_col("sales", sa.Column("delivery_status_enum", delivery_status, nullable=True), sales_columns)
        _add_col("sales", sa.Column("invoice_status_enum", billing_status, nullable=True), sales_columns)
        op.execute(
            """
            UPDATE sales SET delivery_status_enum = CASE
                WHEN delivery_status IN ('NOT_STARTED','PENDING','PARTIAL','COMPLETE','BLOCKED')
                    THEN delivery_status::deliverystatus
                WHEN delivery_status IS NOT NULL THEN 'PENDING'::deliverystatus
                ELSE NULL
            END
            """
        )
        op.execute(
            """
            UPDATE sales SET invoice_status_enum = CASE
                WHEN invoice_status IN ('NOT_INVOICED','PARTIAL','INVOICED','COMPLETE')
                    THEN invoice_status::billingstatus
                WHEN invoice_status IS NOT NULL THEN 'NOT_INVOICED'::billingstatus
                ELSE NULL
            END
            """
        )
        op.drop_column("sales", "delivery_status")
        op.drop_column("sales", "invoice_status")
        op.alter_column("sales", "delivery_status_enum", new_column_name="delivery_status")
        op.alter_column("sales", "invoice_status_enum", new_column_name="invoice_status")

    # --- sale_items ---
    for col in (
        sa.Column("item_category", sa.String(32), nullable=True),
        sa.Column("confirmed_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delivered_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gross_price", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "warehouse_id",
            sa.Integer(),
            sa.ForeignKey("warehouses.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "storage_location_id",
            sa.Integer(),
            sa.ForeignKey("storage_locations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("batch_number", sa.String(64), nullable=True),
        sa.Column("serial_number", sa.String(64), nullable=True),
        sa.Column("delivery_block", sa.String(64), nullable=True),
        sa.Column("billing_block", sa.String(64), nullable=True),
        sa.Column("rejection_reason", sa.String(120), nullable=True),
        sa.Column("net_weight", sa.Numeric(12, 4), nullable=True),
        sa.Column("gross_weight", sa.Numeric(12, 4), nullable=True),
        sa.Column("volume", sa.Numeric(12, 4), nullable=True),
        sa.Column(
            "substitute_product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("line_text", sa.Text(), nullable=True),
    ):
        _add_col("sale_items", col, sale_item_columns)

    # --- sale_partners ---
    if "sale_partners" not in table_names:
        op.create_table(
            "sale_partners",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False),
            sa.Column("role", partner_role, nullable=False),
            sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True),
            sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("name_override", sa.String(255), nullable=True),
            sa.Column("address", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("sale_id", "role", name="uq_sale_partners_sale_role"),
            if_not_exists=True,
        )
        op.create_index(
            "ix_sale_partners_sale_id",
            "sale_partners",
            ["sale_id"],
            if_not_exists=True,
        )


def downgrade() -> None:
    op.drop_index("ix_sale_partners_sale_id", table_name="sale_partners")
    op.drop_table("sale_partners")

    for col in (
        "line_text",
        "substitute_product_id",
        "volume",
        "gross_weight",
        "net_weight",
        "rejection_reason",
        "billing_block",
        "delivery_block",
        "serial_number",
        "batch_number",
        "storage_location_id",
        "warehouse_id",
        "gross_price",
        "delivered_quantity",
        "confirmed_quantity",
        "item_category",
    ):
        op.drop_column("sale_items", col)

    op.add_column("sales", sa.Column("delivery_status_str", sa.String(32), nullable=True))
    op.add_column("sales", sa.Column("invoice_status_str", sa.String(32), nullable=True))
    op.execute("UPDATE sales SET delivery_status_str = delivery_status::text")
    op.execute("UPDATE sales SET invoice_status_str = invoice_status::text")
    op.drop_column("sales", "delivery_status")
    op.drop_column("sales", "invoice_status")
    op.alter_column("sales", "delivery_status_str", new_column_name="delivery_status")
    op.alter_column("sales", "invoice_status_str", new_column_name="invoice_status")

    for col in (
        "updated_by_id",
        "updated_at",
        "header_text",
        "loading_group",
        "transportation_group",
        "shipping_conditions",
        "price_group",
        "campaign_id",
        "opportunity_id",
        "complete_delivery_required",
        "customer_po_date",
        "customer_po_number",
        "requested_delivery_date",
        "shipping_point_id",
        "incoterms_location",
        "pricing_procedure",
        "sales_group",
        "sales_office",
        "division",
        "distribution_channel",
        "sales_organization",
    ):
        op.drop_column("sales", col)

    bind = op.get_bind()
    for name in ("salepartnerrole", "billingstatus", "deliverystatus"):
        postgresql.ENUM(name=name).drop(bind, checkfirst=True)
