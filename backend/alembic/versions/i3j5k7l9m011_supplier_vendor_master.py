"""supplier vendor master fields

Revision ID: i3j5k7l9m011
Revises: h2i4j6k8l010
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "i3j5k7l9m011"
down_revision: Union[str, None] = "h2i4j6k8l010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("vendor_code", sa.String(length=32), nullable=True))
    op.add_column("suppliers", sa.Column("legal_name", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("dba", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("address_line1", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("address_line2", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("suppliers", sa.Column("state", sa.String(length=120), nullable=True))
    op.add_column("suppliers", sa.Column("postal_code", sa.String(length=32), nullable=True))
    op.add_column("suppliers", sa.Column("country", sa.String(length=64), nullable=True))
    op.add_column("suppliers", sa.Column("website", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("tax_id", sa.String(length=64), nullable=True))
    op.add_column("suppliers", sa.Column("payment_terms", sa.String(length=120), nullable=True))
    op.add_column("suppliers", sa.Column("incoterms", sa.String(length=32), nullable=True))
    op.add_column(
        "suppliers",
        sa.Column("bank_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("suppliers", sa.Column("vendor_category", sa.String(length=64), nullable=True))
    op.add_column("suppliers", sa.Column("vendor_type", sa.String(length=64), nullable=True))
    op.add_column("suppliers", sa.Column("approval_status", sa.String(length=32), nullable=True))
    op.add_column(
        "suppliers",
        sa.Column("performance_rating", sa.Numeric(6, 2), nullable=True),
    )
    op.add_column("suppliers", sa.Column("lead_time_days", sa.Integer(), nullable=True))
    op.add_column("suppliers", sa.Column("moq", sa.Numeric(14, 4), nullable=True))
    op.add_column(
        "suppliers",
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
    )
    op.add_column("suppliers", sa.Column("pricing_currency", sa.String(length=3), nullable=True))
    op.add_column(
        "suppliers",
        sa.Column("documents", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.execute(
        """
        UPDATE suppliers
        SET vendor_code = 'VND-' || LPAD(id::text, 5, '0')
        WHERE vendor_code IS NULL
        """
    )

    op.alter_column("suppliers", "vendor_code", nullable=False)
    op.create_unique_constraint("uq_suppliers_vendor_code", "suppliers", ["vendor_code"])


def downgrade() -> None:
    op.drop_constraint("uq_suppliers_vendor_code", "suppliers", type_="unique")
    for col in (
        "documents",
        "pricing_currency",
        "currency_code",
        "moq",
        "lead_time_days",
        "performance_rating",
        "approval_status",
        "vendor_type",
        "vendor_category",
        "bank_details",
        "incoterms",
        "payment_terms",
        "tax_id",
        "website",
        "country",
        "postal_code",
        "state",
        "city",
        "address_line2",
        "address_line1",
        "dba",
        "legal_name",
        "vendor_code",
    ):
        op.drop_column("suppliers", col)
