"""link manufacturing items to inventory products

Revision ID: b1d3e5f7a908
Revises: a9c1e2f4b706
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b1d3e5f7a908"
down_revision: Union[str, None] = "a9c1e2f4b706"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "manufacturing_items",
        sa.Column("product_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_manufacturing_items_product_id",
        "manufacturing_items",
        "products",
        ["product_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_manufacturing_items_product_id",
        "manufacturing_items",
        ["product_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_manufacturing_items_product_id", table_name="manufacturing_items")
    op.drop_constraint(
        "fk_manufacturing_items_product_id",
        "manufacturing_items",
        type_="foreignkey",
    )
    op.drop_column("manufacturing_items", "product_id")
