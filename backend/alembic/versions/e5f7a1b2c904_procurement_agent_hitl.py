"""procurement agent human-in-the-loop

Revision ID: e5f7a1b2c904
Revises: d4e6f8b3c215
Create Date: 2026-05-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "e5f7a1b2c904"
down_revision: Union[str, None] = "d4e6f8b3c215"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    procurementrunstatus = postgresql.ENUM(
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        name="procurementrunstatus",
        create_type=False,
    )
    procurementrunstatus.create(bind, checkfirst=True)

    purchasestatus = postgresql.ENUM(
        "DRAFT",
        "RECEIVED",
        name="purchasestatus",
        create_type=False,
    )
    purchasestatus.create(bind, checkfirst=True)

    if not insp.has_table("procurement_runs"):
        op.create_table(
            "procurement_runs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("status", procurementrunstatus, nullable=False),
            sa.Column("summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    insp = inspect(bind)
    purchase_cols = {c["name"] for c in insp.get_columns("purchases")} if insp.has_table("purchases") else set()

    if "status" not in purchase_cols:
        op.add_column(
            "purchases",
            sa.Column("status", purchasestatus, server_default="RECEIVED", nullable=False),
        )
    if "procurement_run_id" not in purchase_cols:
        op.add_column(
            "purchases",
            sa.Column("procurement_run_id", sa.Integer(), nullable=True),
        )
    if "agent_metadata" not in purchase_cols:
        op.add_column(
            "purchases",
            sa.Column("agent_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        )

    insp = inspect(bind)
    fk_names = {fk["name"] for fk in insp.get_foreign_keys("purchases")} if insp.has_table("purchases") else set()
    if "fk_purchases_procurement_run_id" not in fk_names and insp.has_table("procurement_runs"):
        op.create_foreign_key(
            "fk_purchases_procurement_run_id",
            "purchases",
            "procurement_runs",
            ["procurement_run_id"],
            ["id"],
            ondelete="SET NULL",
        )

    insp = inspect(bind)
    product_cols = {c["name"] for c in insp.get_columns("products")} if insp.has_table("products") else set()
    if "default_supplier_id" not in product_cols:
        op.add_column("products", sa.Column("default_supplier_id", sa.Integer(), nullable=True))

    insp = inspect(bind)
    fk_prod = {fk["name"] for fk in insp.get_foreign_keys("products")} if insp.has_table("products") else set()
    if "fk_products_default_supplier_id" not in fk_prod:
        op.create_foreign_key(
            "fk_products_default_supplier_id",
            "products",
            "suppliers",
            ["default_supplier_id"],
            ["id"],
            ondelete="SET NULL",
        )
    if "promotion_reorder_boost" not in product_cols:
        op.add_column(
            "products",
            sa.Column(
                "promotion_reorder_boost",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()

    insp = inspect(bind)
    if insp.has_table("products"):
        if insp.has_column("products", "promotion_reorder_boost"):
            op.drop_column("products", "promotion_reorder_boost")
        fk_prod = {fk["name"] for fk in insp.get_foreign_keys("products")}
        if "fk_products_default_supplier_id" in fk_prod:
            op.drop_constraint("fk_products_default_supplier_id", "products", type_="foreignkey")
        if insp.has_column("products", "default_supplier_id"):
            op.drop_column("products", "default_supplier_id")

    insp = inspect(bind)
    if insp.has_table("purchases"):
        fk_pur = {fk["name"] for fk in insp.get_foreign_keys("purchases")}
        if "fk_purchases_procurement_run_id" in fk_pur:
            op.drop_constraint("fk_purchases_procurement_run_id", "purchases", type_="foreignkey")
        if insp.has_column("purchases", "agent_metadata"):
            op.drop_column("purchases", "agent_metadata")
        if insp.has_column("purchases", "procurement_run_id"):
            op.drop_column("purchases", "procurement_run_id")
        if insp.has_column("purchases", "status"):
            op.drop_column("purchases", "status")

    if insp.has_table("procurement_runs"):
        op.drop_table("procurement_runs")

    procurementrunstatus = postgresql.ENUM(
        "IN_PROGRESS",
        "COMPLETED",
        "FAILED",
        name="procurementrunstatus",
        create_type=False,
    )
    procurementrunstatus.drop(bind, checkfirst=True)

    purchasestatus = postgresql.ENUM(
        "DRAFT",
        "RECEIVED",
        name="purchasestatus",
        create_type=False,
    )
    purchasestatus.drop(bind, checkfirst=True)
