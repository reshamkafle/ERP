"""Sales order management field expansion

Revision ID: l6n8p0q2r314
Revises: k5m7n9p1q213
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "l6n8p0q2r314"
down_revision: Union[str, None] = "k5m7n9p1q213"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SALE_ORDER_STATUSES = (
    "DRAFT", "CREATED", "RELEASED", "IN_PROCESS", "DELIVERED", "INVOICED", "CLOSED", "CANCELLED",
)
SALE_ORDER_TYPES = ("STANDARD", "RUSH", "SAMPLE", "RETURN", "EXPORT")
SALE_CHANNELS = ("DIRECT", "DISTRIBUTOR", "ECOMMERCE", "RETAIL")
SALE_ORDER_SOURCES = ("PHONE", "EMAIL", "PORTAL", "EDI", "MOBILE")
ORDER_PRIORITIES = ("HIGH", "MEDIUM", "LOW")
SALE_LINE_STATUSES = ("OPEN", "ALLOCATED", "PARTIAL", "DELIVERED", "INVOICED", "CANCELLED")
CREDIT_CHECK_STATUSES = ("NOT_RUN", "PASSED", "FAILED", "OVERRIDE")
ATP_CHECK_STATUSES = ("NOT_RUN", "AVAILABLE", "PARTIAL", "UNAVAILABLE")


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in (
        ("saleorderstatus", SALE_ORDER_STATUSES),
        ("saleordertype", SALE_ORDER_TYPES),
        ("salechannel", SALE_CHANNELS),
        ("saleordersource", SALE_ORDER_SOURCES),
        ("orderpriority", ORDER_PRIORITIES),
        ("salelinestatus", SALE_LINE_STATUSES),
        ("creditcheckstatus", CREDIT_CHECK_STATUSES),
        ("atpcheckstatus", ATP_CHECK_STATUSES),
    ):
        postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    sale_status = _enum("saleorderstatus", SALE_ORDER_STATUSES)
    sale_type = _enum("saleordertype", SALE_ORDER_TYPES)
    sale_channel = _enum("salechannel", SALE_CHANNELS)
    sale_source = _enum("saleordersource", SALE_ORDER_SOURCES)
    priority = _enum("orderpriority", ORDER_PRIORITIES)
    line_status = _enum("salelinestatus", SALE_LINE_STATUSES)
    credit_status = _enum("creditcheckstatus", CREDIT_CHECK_STATUSES)
    atp_status = _enum("atpcheckstatus", ATP_CHECK_STATUSES)

    # --- customers ---
    op.add_column("customers", sa.Column("customer_code", sa.String(32), nullable=True))
    op.add_column("customers", sa.Column("legal_name", sa.String(255), nullable=True))
    op.add_column("customers", sa.Column("contact_name", sa.String(255), nullable=True))
    op.add_column("customers", sa.Column("contact_phone", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("contact_email", sa.String(255), nullable=True))
    for prefix in ("billing", "shipping"):
        op.add_column("customers", sa.Column(f"{prefix}_address_line1", sa.String(255), nullable=True))
        op.add_column("customers", sa.Column(f"{prefix}_address_line2", sa.String(255), nullable=True))
        op.add_column("customers", sa.Column(f"{prefix}_city", sa.String(120), nullable=True))
        op.add_column("customers", sa.Column(f"{prefix}_state", sa.String(120), nullable=True))
        op.add_column("customers", sa.Column(f"{prefix}_postal_code", sa.String(32), nullable=True))
        op.add_column("customers", sa.Column(f"{prefix}_country", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("customer_group", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("credit_limit", sa.Numeric(14, 2), nullable=True))
    op.add_column("customers", sa.Column("credit_status", sa.String(32), nullable=True))
    op.add_column("customers", sa.Column("payment_terms", sa.String(120), nullable=True))
    op.add_column("customers", sa.Column("tax_id", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("incoterms", sa.String(32), nullable=True))
    op.add_column(
        "customers",
        sa.Column("currency_code", sa.String(3), nullable=False, server_default="USD"),
    )
    op.add_column("customers", sa.Column("shipping_preference", sa.String(120), nullable=True))
    op.create_index("ix_customers_customer_code", "customers", ["customer_code"], unique=True)

    # --- sales header ---
    op.add_column("sales", sa.Column("order_number", sa.String(32), nullable=True))
    op.add_column(
        "sales",
        sa.Column("order_status", sale_status, nullable=False, server_default="DRAFT"),
    )
    op.add_column(
        "sales",
        sa.Column("order_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
    )
    op.add_column(
        "sales",
        sa.Column("order_type", sale_type, nullable=False, server_default="STANDARD"),
    )
    op.add_column("sales", sa.Column("sales_channel", sale_channel, nullable=True))
    op.add_column("sales", sa.Column("order_source", sale_source, nullable=True))
    op.add_column(
        "sales",
        sa.Column("priority", priority, nullable=False, server_default="MEDIUM"),
    )
    op.add_column("sales", sa.Column("salesperson_id", sa.Integer(), nullable=True))
    op.add_column(
        "sales",
        sa.Column("is_pos_checkout", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("sales", sa.Column("gross_total", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column(
        "sales",
        sa.Column("header_discount_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.add_column("sales", sa.Column("freight_amount", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("insurance_amount", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("handling_amount", sa.Numeric(14, 2), nullable=False, server_default="0"))
    op.add_column("sales", sa.Column("price_list_code", sa.String(64), nullable=True))
    op.add_column("sales", sa.Column("payment_terms", sa.String(120), nullable=True))
    op.add_column("sales", sa.Column("payment_due_date", sa.Date(), nullable=True))
    op.add_column("sales", sa.Column("payment_method_id", sa.Integer(), nullable=True))
    op.add_column("sales", sa.Column("warehouse_id", sa.Integer(), nullable=True))
    op.add_column(
        "sales",
        sa.Column("partial_delivery_allowed", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("sales", sa.Column("planned_ship_date", sa.Date(), nullable=True))
    op.add_column("sales", sa.Column("shipping_method", sa.String(64), nullable=True))
    op.add_column("sales", sa.Column("incoterms", sa.String(32), nullable=True))
    op.add_column("sales", sa.Column("delivery_block", sa.String(64), nullable=True))
    op.add_column(
        "sales",
        sa.Column("credit_check_status", credit_status, nullable=False, server_default="NOT_RUN"),
    )
    op.add_column(
        "sales",
        sa.Column("atp_check_status", atp_status, nullable=False, server_default="NOT_RUN"),
    )
    op.add_column("sales", sa.Column("invoice_status", sa.String(32), nullable=True))
    op.add_column("sales", sa.Column("delivery_status", sa.String(32), nullable=True))
    op.add_column("sales", sa.Column("approval_status", sa.String(32), nullable=True))
    for col in (
        "customer_snapshot",
        "pricing_conditions",
        "delivery_logistics",
        "billing_financial",
        "terms_compliance",
        "references",
        "attachments",
        "workflow_history",
    ):
        op.add_column("sales", sa.Column(col, postgresql.JSONB(), nullable=True))

    op.execute(sa.text("UPDATE sales SET order_number = 'SO-' || id::text WHERE order_number IS NULL"))
    op.execute(sa.text("UPDATE sales SET order_status = 'CLOSED', is_pos_checkout = true"))
    op.execute(sa.text("UPDATE sales SET gross_total = subtotal WHERE gross_total = 0"))

    op.alter_column("sales", "order_number", nullable=False)
    op.create_index("ix_sales_order_number", "sales", ["order_number"], unique=True)
    op.create_foreign_key("fk_sales_salesperson", "sales", "users", ["salesperson_id"], ["id"])
    op.create_foreign_key("fk_sales_payment_method", "sales", "payment_methods", ["payment_method_id"], ["id"])
    op.create_foreign_key("fk_sales_warehouse", "sales", "warehouses", ["warehouse_id"], ["id"])

    # --- sale_items ---
    op.add_column("sale_items", sa.Column("line_number", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("sale_items", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("sale_items", sa.Column("uom", sa.String(32), nullable=True))
    op.add_column("sale_items", sa.Column("unit_price", sa.Numeric(12, 2), nullable=True))
    op.execute(sa.text("UPDATE sale_items SET unit_price = price_at_sale WHERE unit_price IS NULL"))
    op.alter_column("sale_items", "unit_price", nullable=False)
    op.add_column(
        "sale_items",
        sa.Column("discount_percent", sa.Numeric(8, 4), nullable=False, server_default="0"),
    )
    op.add_column(
        "sale_items",
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column("sale_items", sa.Column("tax_code", sa.String(32), nullable=True))
    op.add_column("sale_items", sa.Column("tax_rate_id", sa.Integer(), nullable=True))
    op.add_column(
        "sale_items",
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "sale_items",
        sa.Column("net_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "sale_items",
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.execute(
        sa.text(
            "UPDATE sale_items SET net_amount = quantity * price_at_sale, "
            "line_total = quantity * price_at_sale",
        ),
    )
    op.add_column("sale_items", sa.Column("requested_delivery_date", sa.Date(), nullable=True))
    op.add_column("sale_items", sa.Column("confirmed_delivery_date", sa.Date(), nullable=True))
    op.add_column(
        "sale_items",
        sa.Column("line_status", line_status, nullable=False, server_default="OPEN"),
    )
    op.add_column(
        "sale_items",
        sa.Column("backorder_quantity", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("sale_items", sa.Column("product_category", sa.String(120), nullable=True))
    op.create_foreign_key("fk_sale_items_tax_rate", "sale_items", "tax_rates", ["tax_rate_id"], ["id"])

    # --- erp_documents ---
    op.add_column("erp_documents", sa.Column("sale_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_erp_documents_sale",
        "erp_documents",
        "sales",
        ["sale_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_erp_documents_sale", "erp_documents", type_="foreignkey")
    op.drop_column("erp_documents", "sale_id")

    op.drop_constraint("fk_sale_items_tax_rate", "sale_items", type_="foreignkey")
    for col in (
        "product_category", "backorder_quantity", "line_status", "confirmed_delivery_date",
        "requested_delivery_date", "line_total", "net_amount", "tax_amount", "tax_rate_id",
        "tax_code", "discount_amount", "discount_percent", "unit_price", "uom", "description",
        "line_number",
    ):
        op.drop_column("sale_items", col)

    op.drop_constraint("fk_sales_warehouse", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_payment_method", "sales", type_="foreignkey")
    op.drop_constraint("fk_sales_salesperson", "sales", type_="foreignkey")
    op.drop_index("ix_sales_order_number", table_name="sales")
    for col in (
        "workflow_history", "attachments", "references", "terms_compliance",
        "billing_financial", "delivery_logistics", "pricing_conditions", "customer_snapshot",
        "approval_status", "delivery_status", "invoice_status", "atp_check_status",
        "credit_check_status", "delivery_block", "incoterms", "shipping_method",
        "planned_ship_date", "partial_delivery_allowed", "warehouse_id", "payment_method_id",
        "payment_due_date", "payment_terms", "price_list_code", "handling_amount",
        "insurance_amount", "freight_amount", "header_discount_amount", "gross_total",
        "is_pos_checkout", "salesperson_id", "priority", "order_source", "sales_channel",
        "order_type", "order_date", "order_status", "order_number",
    ):
        op.drop_column("sales", col)

    op.drop_index("ix_customers_customer_code", table_name="customers")
    for col in (
        "shipping_preference", "currency_code", "incoterms", "tax_id", "payment_terms",
        "credit_status", "credit_limit", "customer_group",
        "shipping_country", "shipping_postal_code", "shipping_state", "shipping_city",
        "shipping_address_line2", "shipping_address_line1",
        "billing_country", "billing_postal_code", "billing_state", "billing_city",
        "billing_address_line2", "billing_address_line1",
        "contact_email", "contact_phone", "contact_name", "legal_name", "customer_code",
    ):
        op.drop_column("customers", col)

    bind = op.get_bind()
    for name in (
        "atpcheckstatus", "creditcheckstatus", "salelinestatus", "orderpriority",
        "saleordersource", "salechannel", "saleordertype", "saleorderstatus",
    ):
        postgresql.ENUM(name=name).drop(bind, checkfirst=True)
