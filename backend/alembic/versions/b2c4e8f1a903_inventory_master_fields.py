"""inventory master fields

Revision ID: b2c4e8f1a903
Revises: 7a9ef19a56dc
Create Date: 2026-05-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c4e8f1a903"
down_revision: Union[str, None] = "7a9ef19a56dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

itemtype = sa.Enum("RAW", "FINISHED", "TRADING", "SERVICE", "ASSET", name="itemtype")
itemlifecyclestatus = sa.Enum(
    "ACTIVE", "INACTIVE", "DISCONTINUED", "OBSOLETE", name="itemlifecyclestatus"
)
approvalstatus = sa.Enum("DRAFT", "PENDING", "APPROVED", "REJECTED", name="approvalstatus")


def upgrade() -> None:
    itemtype.create(op.get_bind(), checkfirst=True)
    itemlifecyclestatus.create(op.get_bind(), checkfirst=True)
    approvalstatus.create(op.get_bind(), checkfirst=True)

    op.alter_column("products", "category_id", existing_type=sa.Integer(), nullable=True)

    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("alternate_codes", sa.Text(), nullable=True))
    op.add_column("products", sa.Column("sub_category", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("product_line", sa.String(length=120), nullable=True))
    op.add_column(
        "products",
        sa.Column(
            "item_type",
            itemtype,
            nullable=False,
            server_default="TRADING",
        ),
    )
    op.add_column("products", sa.Column("size", sa.String(length=64), nullable=True))
    op.add_column("products", sa.Column("color", sa.String(length=64), nullable=True))
    op.add_column("products", sa.Column("model", sa.String(length=120), nullable=True))
    op.add_column("products", sa.Column("variant", sa.String(length=120), nullable=True))
    op.add_column(
        "products",
        sa.Column("serial_number_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "products",
        sa.Column("batch_lot_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "products",
        sa.Column("expiry_date_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "products",
        sa.Column("primary_uom", sa.String(length=32), nullable=False, server_default="EA"),
    )
    op.add_column("products", sa.Column("secondary_uom", sa.String(length=32), nullable=True))
    op.add_column("products", sa.Column("conversion_factor", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("length", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("width", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("height", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("volume", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("gross_weight", sa.Numeric(12, 4), nullable=True))
    op.add_column("products", sa.Column("net_weight", sa.Numeric(12, 4), nullable=True))
    op.add_column(
        "products",
        sa.Column(
            "lifecycle_status",
            itemlifecyclestatus,
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "approval_status",
            approvalstatus,
            nullable=False,
            server_default="DRAFT",
        ),
    )
    op.add_column("products", sa.Column("tax_code", sa.String(length=64), nullable=True))
    op.add_column("products", sa.Column("hs_code", sa.String(length=32), nullable=True))
    op.add_column("products", sa.Column("country_of_origin", sa.String(length=64), nullable=True))
    op.add_column(
        "products",
        sa.Column("hazardous_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "products",
        sa.Column("perishable_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("products", "perishable_flag")
    op.drop_column("products", "hazardous_flag")
    op.drop_column("products", "country_of_origin")
    op.drop_column("products", "hs_code")
    op.drop_column("products", "tax_code")
    op.drop_column("products", "approval_status")
    op.drop_column("products", "lifecycle_status")
    op.drop_column("products", "net_weight")
    op.drop_column("products", "gross_weight")
    op.drop_column("products", "volume")
    op.drop_column("products", "height")
    op.drop_column("products", "width")
    op.drop_column("products", "length")
    op.drop_column("products", "conversion_factor")
    op.drop_column("products", "secondary_uom")
    op.drop_column("products", "primary_uom")
    op.drop_column("products", "expiry_date_flag")
    op.drop_column("products", "batch_lot_flag")
    op.drop_column("products", "serial_number_flag")
    op.drop_column("products", "variant")
    op.drop_column("products", "model")
    op.drop_column("products", "color")
    op.drop_column("products", "size")
    op.drop_column("products", "item_type")
    op.drop_column("products", "product_line")
    op.drop_column("products", "sub_category")
    op.drop_column("products", "alternate_codes")
    op.drop_column("products", "description")

    op.alter_column("products", "category_id", existing_type=sa.Integer(), nullable=False)

    approvalstatus.drop(op.get_bind(), checkfirst=True)
    itemlifecyclestatus.drop(op.get_bind(), checkfirst=True)
    itemtype.drop(op.get_bind(), checkfirst=True)
