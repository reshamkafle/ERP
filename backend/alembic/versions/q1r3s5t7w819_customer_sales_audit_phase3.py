"""Customer sales areas and audit log

Revision ID: q1r3s5t7w819
Revises: p0q2s4t6v718
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "q1r3s5t7w819"
down_revision: Union[str, None] = "p0q2s4t6v718"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "customer_sales_areas" in inspector.get_table_names():
        if "customer_audit_log" not in inspector.get_table_names():
            op.create_table(
                "customer_audit_log",
                sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
                sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
                sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
                sa.Column("field_name", sa.String(128), nullable=False),
                sa.Column("old_value", postgresql.JSONB(), nullable=True),
                sa.Column("new_value", postgresql.JSONB(), nullable=True),
                sa.Column("change_summary", sa.Text(), nullable=True),
                sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            )
            op.create_index("ix_customer_audit_log_customer_id", "customer_audit_log", ["customer_id"])
        return

    op.create_table(
        "customer_sales_areas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sales_org", sa.String(64), nullable=False),
        sa.Column("distribution_channel", sa.String(64), nullable=True),
        sa.Column("division", sa.String(64), nullable=True),
        sa.Column("credit_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("payment_terms", sa.String(120), nullable=True),
        sa.Column("pricing_procedure", sa.String(120), nullable=True),
        sa.Column("partner_functions", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint(
            "customer_id",
            "sales_org",
            "distribution_channel",
            "division",
            name="uq_customer_sales_area",
        ),
    )
    op.create_index("ix_customer_sales_areas_customer_id", "customer_sales_areas", ["customer_id"])

    op.create_table(
        "customer_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("field_name", sa.String(128), nullable=False),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_customer_audit_log_customer_id", "customer_audit_log", ["customer_id"])


def downgrade() -> None:
    op.drop_index("ix_customer_audit_log_customer_id", table_name="customer_audit_log")
    op.drop_table("customer_audit_log")
    op.drop_index("ix_customer_sales_areas_customer_id", table_name="customer_sales_areas")
    op.drop_table("customer_sales_areas")
