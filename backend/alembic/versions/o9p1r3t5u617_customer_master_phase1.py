"""Customer master phase 1 fields

Revision ID: o9p1r3t5u617
Revises: n8p0r2t4u516
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "o9p1r3t5u617"
down_revision: Union[str, None] = "n8p0r2t4u516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CUSTOMER_STATUSES = ("ACTIVE", "INACTIVE", "PROSPECT", "BLOCKED")
CUSTOMER_TYPES = ("INDIVIDUAL", "COMPANY", "GOVERNMENT", "DISTRIBUTOR", "RETAIL", "OTHER")


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if column.name not in {c["name"] for c in insp.get_columns(table)}:
        op.add_column(table, column)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*CUSTOMER_STATUSES, name="customerstatus").create(bind, checkfirst=True)
    postgresql.ENUM(*CUSTOMER_TYPES, name="customertype").create(bind, checkfirst=True)
    status_enum = postgresql.ENUM(*CUSTOMER_STATUSES, name="customerstatus", create_type=False)
    type_enum = postgresql.ENUM(*CUSTOMER_TYPES, name="customertype", create_type=False)

    cols = [
        sa.Column("trade_name", sa.String(255), nullable=True),
        sa.Column("search_terms", sa.String(255), nullable=True),
        sa.Column("status", status_enum, nullable=True),
        sa.Column("customer_type", type_enum, nullable=True),
        sa.Column("parent_customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("mobile_phone", sa.String(64), nullable=True),
        sa.Column("fax", sa.String(64), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=True),
        sa.Column("language", sa.String(64), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column(
            "reconciliation_account_id",
            sa.Integer(),
            sa.ForeignKey("chart_of_accounts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("tax_classification", sa.String(64), nullable=True),
        sa.Column("tax_exempt", sa.Boolean(), nullable=True),
        sa.Column("bank_details", postgresql.JSONB(), nullable=True),
        sa.Column("dunning_procedure", sa.String(120), nullable=True),
        sa.Column("withholding_tax", sa.String(64), nullable=True),
        sa.Column("sales_rep", sa.String(120), nullable=True),
        sa.Column("price_group", sa.String(64), nullable=True),
        sa.Column("shipping_conditions", sa.String(120), nullable=True),
        sa.Column("delivering_plant", sa.String(120), nullable=True),
        sa.Column("order_probability", sa.Numeric(5, 2), nullable=True),
        sa.Column("lead_source", sa.String(120), nullable=True),
        sa.Column("preferred_carrier", sa.String(120), nullable=True),
        sa.Column("receiving_hours", sa.String(255), nullable=True),
        sa.Column("freight_terms", sa.String(120), nullable=True),
        sa.Column("transport_zone", sa.String(64), nullable=True),
        sa.Column("extended_data", postgresql.JSONB(), nullable=True),
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
    ]
    for col in cols:
        _add_column_if_missing("customers", col)
    op.create_index(
        "ix_customers_parent_customer_id",
        "customers",
        ["parent_customer_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_customers_parent_customer_id", table_name="customers")
    for col in (
        "updated_at",
        "created_at",
        "extended_data",
        "transport_zone",
        "freight_terms",
        "receiving_hours",
        "preferred_carrier",
        "lead_source",
        "order_probability",
        "delivering_plant",
        "shipping_conditions",
        "price_group",
        "sales_rep",
        "withholding_tax",
        "dunning_procedure",
        "bank_details",
        "tax_exempt",
        "tax_classification",
        "reconciliation_account_id",
        "longitude",
        "latitude",
        "language",
        "timezone",
        "fax",
        "mobile_phone",
        "parent_customer_id",
        "customer_type",
        "status",
        "search_terms",
        "trade_name",
    ):
        op.drop_column("customers", col)
    bind = op.get_bind()
    postgresql.ENUM(name="customertype").drop(bind, checkfirst=True)
    postgresql.ENUM(name="customerstatus").drop(bind, checkfirst=True)
