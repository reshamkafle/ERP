"""Customer CRM master fields

Revision ID: m7o9q1s3t415
Revises: l6n8p0q2r314
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "m7o9q1s3t415"
down_revision: Union[str, None] = "l6n8p0q2r314"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CUSTOMER_SEGMENTS = ("VIP", "REGULAR", "NEW", "PROSPECT", "INACTIVE")


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*CUSTOMER_SEGMENTS, name="customersegment").create(bind, checkfirst=True)
    segment = postgresql.ENUM(*CUSTOMER_SEGMENTS, name="customersegment", create_type=False)

    op.add_column("customers", sa.Column("industry", sa.String(120), nullable=True))
    op.add_column("customers", sa.Column("company_size", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("annual_revenue", sa.Numeric(16, 2), nullable=True))
    op.add_column("customers", sa.Column("website", sa.String(255), nullable=True))
    op.add_column("customers", sa.Column("segment", segment, nullable=True))
    op.add_column("customers", sa.Column("tax_registration_type", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("gst_number", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("vat_number", sa.String(64), nullable=True))
    op.add_column("customers", sa.Column("billing_preference", sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column("customers", "billing_preference")
    op.drop_column("customers", "vat_number")
    op.drop_column("customers", "gst_number")
    op.drop_column("customers", "tax_registration_type")
    op.drop_column("customers", "segment")
    op.drop_column("customers", "website")
    op.drop_column("customers", "annual_revenue")
    op.drop_column("customers", "company_size")
    op.drop_column("customers", "industry")
    bind = op.get_bind()
    postgresql.ENUM(name="customersegment").drop(bind, checkfirst=True)
