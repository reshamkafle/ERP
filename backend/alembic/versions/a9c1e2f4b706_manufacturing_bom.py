"""manufacturing BOM tables

Revision ID: a9c1e2f4b706
Revises: f8a9b0c1d2e3
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "a9c1e2f4b706"
down_revision: Union[str, None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

manufacturingitemcategory = ENUM(
    "FABRIC",
    "TRIM",
    "ACCESSORY",
    "SUB_ASSEMBLY",
    "FINISHED_GOOD",
    name="manufacturingitemcategory",
    create_type=False,
)
manufacturingunitofmeasure = ENUM(
    "meter",
    "kg",
    "piece",
    "yard",
    "gram",
    "set",
    "ea",
    name="manufacturingunitofmeasure",
    create_type=False,
)
consumptiontype = ENUM("FABRIC", "TRIM", "OTHER", name="consumptiontype", create_type=False)


def _ensure_enums() -> None:
    bind = op.get_bind()
    sa.Enum(
        "FABRIC",
        "TRIM",
        "ACCESSORY",
        "SUB_ASSEMBLY",
        "FINISHED_GOOD",
        name="manufacturingitemcategory",
    ).create(bind, checkfirst=True)
    sa.Enum(
        "meter",
        "kg",
        "piece",
        "yard",
        "gram",
        "set",
        "ea",
        name="manufacturingunitofmeasure",
    ).create(bind, checkfirst=True)
    sa.Enum("FABRIC", "TRIM", "OTHER", name="consumptiontype").create(bind, checkfirst=True)


def upgrade() -> None:
    _ensure_enums()

    op.create_table(
        "manufacturing_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", manufacturingitemcategory, nullable=False),
        sa.Column("unit", manufacturingunitofmeasure, nullable=False),
        sa.Column("cost_per_unit", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("secondary_uom", sa.String(length=32), nullable=True),
        sa.Column("conversion_factor", sa.Numeric(12, 4), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )
    op.create_index("ix_manufacturing_items_sku", "manufacturing_items", ["sku"], unique=True)

    op.create_table(
        "bom_headers",
        sa.Column("parent_item_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("parent_item_id"),
    )

    op.create_table(
        "bom_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_item_id", sa.Integer(), nullable=False),
        sa.Column("component_item_id", sa.Integer(), nullable=False),
        sa.Column("quantity_per_unit", sa.Numeric(12, 4), nullable=False),
        sa.Column("consumption_type", consumptiontype, nullable=False, server_default="OTHER"),
        sa.Column("wastage_percentage", sa.Numeric(8, 4), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["component_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("parent_item_id", "component_item_id", name="uq_bom_parent_component"),
    )
    op.create_index("ix_bom_lines_parent_item_id", "bom_lines", ["parent_item_id"], unique=False)
    op.create_index("ix_bom_lines_component_item_id", "bom_lines", ["component_item_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bom_lines_component_item_id", table_name="bom_lines")
    op.drop_index("ix_bom_lines_parent_item_id", table_name="bom_lines")
    op.drop_table("bom_lines")
    op.drop_table("bom_headers")
    op.drop_index("ix_manufacturing_items_sku", table_name="manufacturing_items")
    op.drop_table("manufacturing_items")

    bind = op.get_bind()
    sa.Enum("FABRIC", "TRIM", "OTHER", name="consumptiontype").drop(bind, checkfirst=True)
    sa.Enum(
        "meter",
        "kg",
        "piece",
        "yard",
        "gram",
        "set",
        "ea",
        name="manufacturingunitofmeasure",
    ).drop(bind, checkfirst=True)
    sa.Enum(
        "FABRIC",
        "TRIM",
        "ACCESSORY",
        "SUB_ASSEMBLY",
        "FINISHED_GOOD",
        name="manufacturingitemcategory",
    ).drop(bind, checkfirst=True)
