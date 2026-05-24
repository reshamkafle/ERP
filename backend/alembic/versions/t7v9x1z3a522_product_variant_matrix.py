"""Product template and Style-Color-Size variant matrix

Revision ID: t7v9x1z3a522
Revises: s3t5u7v9w021
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "t7v9x1z3a522"
down_revision: Union[str, None] = "s3t5u7v9w021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_attributes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_product_attributes_code", "product_attributes", ["code"], unique=True)

    op.create_table(
        "attribute_values",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("attribute_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["attribute_id"], ["product_attributes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attribute_id", "code", name="uq_attribute_value_code"),
    )
    op.create_index("ix_attribute_values_attribute_id", "attribute_values", ["attribute_id"])

    op.create_table(
        "product_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("style_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sku_prefix", sa.String(length=48), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "item_type",
            sa.Enum(
                "RAW",
                "FINISHED",
                "SEMI_FINISHED",
                "CONSUMABLE",
                "TRADING",
                "SERVICE",
                "ASSET",
                name="itemtype",
                create_type=False,
            ),
            nullable=False,
            server_default="FINISHED",
        ),
        sa.Column("product_line", sa.String(length=120), nullable=True),
        sa.Column("primary_uom", sa.String(length=32), nullable=False, server_default="EA"),
        sa.Column("default_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("default_cost_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("manufacturing_item_sku", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("style_code"),
    )
    op.create_index("ix_product_templates_style_code", "product_templates", ["style_code"], unique=True)

    op.add_column("products", sa.Column("template_id", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("style_code", sa.String(length=64), nullable=True))
    op.add_column("products", sa.Column("color_value_id", sa.Integer(), nullable=True))
    op.add_column("products", sa.Column("size_value_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_products_template_id",
        "products",
        "product_templates",
        ["template_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_products_color_value_id",
        "products",
        "attribute_values",
        ["color_value_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_products_size_value_id",
        "products",
        "attribute_values",
        ["size_value_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_products_template_id", "products", ["template_id"])
    op.create_index("ix_products_style_code", "products", ["style_code"])

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "INSERT INTO product_attributes (code, name, sort_order) VALUES "
            "('COLOR', 'Color', 1), ('SIZE', 'Size', 2)"
        ),
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO attribute_values (attribute_id, code, label, sort_order)
            SELECT id, v.code, v.label, v.sort_order FROM product_attributes pa
            CROSS JOIN (VALUES
                ('RED', 'Red', 1), ('BLU', 'Blue', 2), ('BLK', 'Black', 3), ('WHT', 'White', 4)
            ) AS v(code, label, sort_order)
            WHERE pa.code = 'COLOR'
            """
        ),
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO attribute_values (attribute_id, code, label, sort_order)
            SELECT id, v.code, v.label, v.sort_order FROM product_attributes pa
            CROSS JOIN (VALUES
                ('XS', 'XS', 1), ('S', 'S', 2), ('M', 'M', 3), ('L', 'L', 4), ('XL', 'XL', 5)
            ) AS v(code, label, sort_order)
            WHERE pa.code = 'SIZE'
            """
        ),
    )


def downgrade() -> None:
    op.drop_constraint("fk_products_size_value_id", "products", type_="foreignkey")
    op.drop_constraint("fk_products_color_value_id", "products", type_="foreignkey")
    op.drop_constraint("fk_products_template_id", "products", type_="foreignkey")
    op.drop_index("ix_products_style_code", table_name="products")
    op.drop_index("ix_products_template_id", table_name="products")
    op.drop_column("products", "size_value_id")
    op.drop_column("products", "color_value_id")
    op.drop_column("products", "style_code")
    op.drop_column("products", "template_id")
    op.drop_table("product_templates")
    op.drop_index("ix_attribute_values_attribute_id", table_name="attribute_values")
    op.drop_table("attribute_values")
    op.drop_index("ix_product_attributes_code", table_name="product_attributes")
    op.drop_table("product_attributes")
