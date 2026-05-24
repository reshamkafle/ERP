"""BOM phase 1 header/line fields and status workflow

Revision ID: k5m7n9p1q213
Revises: j4k6l8m0n012
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "k5m7n9p1q213"
down_revision: Union[str, None] = "j4k6l8m0n012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

bomstatus = ENUM(
    "DRAFT",
    "ACTIVE",
    "OBSOLETE",
    "SUPERSEDED",
    name="bomstatus",
    create_type=False,
)
bomtype = ENUM(
    "MANUFACTURING",
    "ENGINEERING",
    "SALES",
    "SERVICE",
    "PHANTOM",
    name="bomtype",
    create_type=False,
)


def _ensure_enums() -> None:
    bind = op.get_bind()
    sa.Enum("DRAFT", "ACTIVE", "OBSOLETE", "SUPERSEDED", name="bomstatus").create(bind, checkfirst=True)
    sa.Enum(
        "MANUFACTURING",
        "ENGINEERING",
        "SALES",
        "SERVICE",
        "PHANTOM",
        name="bomtype",
    ).create(bind, checkfirst=True)


def upgrade() -> None:
    _ensure_enums()

    op.add_column("bom_headers", sa.Column("bom_number", sa.String(length=64), nullable=True))
    op.add_column("bom_headers", sa.Column("status", bomstatus, nullable=True))
    op.add_column("bom_headers", sa.Column("bom_type", bomtype, nullable=True))
    op.add_column("bom_headers", sa.Column("effective_start_date", sa.Date(), nullable=True))
    op.add_column("bom_headers", sa.Column("effective_end_date", sa.Date(), nullable=True))
    op.add_column("bom_headers", sa.Column("eco_number", sa.String(length=64), nullable=True))
    op.add_column("bom_headers", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("bom_headers", sa.Column("approved_by_id", sa.Integer(), nullable=True))
    op.add_column("bom_headers", sa.Column("created_by_id", sa.Integer(), nullable=True))
    op.add_column(
        "bom_headers",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.add_column("bom_headers", sa.Column("updated_by_id", sa.Integer(), nullable=True))
    op.add_column(
        "bom_headers",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )

    op.execute(
        sa.text(
            "UPDATE bom_headers SET status = CASE WHEN is_active THEN 'ACTIVE'::bomstatus "
            "ELSE 'OBSOLETE'::bomstatus END",
        ),
    )
    op.execute(
        sa.text(
            "UPDATE bom_headers h SET bom_number = mi.sku || '-V' || h.version::text "
            "FROM manufacturing_items mi WHERE mi.id = h.parent_item_id",
        ),
    )
    op.execute(sa.text("UPDATE bom_headers SET bom_type = 'MANUFACTURING'::bomtype"))
    op.execute(sa.text("UPDATE bom_headers SET status = 'ACTIVE'::bomstatus WHERE status IS NULL"))
    op.execute(sa.text("UPDATE bom_headers SET bom_type = 'MANUFACTURING'::bomtype WHERE bom_type IS NULL"))

    op.alter_column("bom_headers", "status", nullable=False, server_default="DRAFT")
    op.alter_column("bom_headers", "bom_type", nullable=False, server_default="MANUFACTURING")
    op.alter_column("bom_headers", "bom_number", nullable=False)

    op.create_unique_constraint("uq_bom_headers_bom_number", "bom_headers", ["bom_number"])
    op.create_foreign_key(
        "fk_bom_headers_approved_by_id",
        "bom_headers",
        "users",
        ["approved_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_bom_headers_created_by_id",
        "bom_headers",
        "users",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_bom_headers_updated_by_id",
        "bom_headers",
        "users",
        ["updated_by_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_column("bom_headers", "is_active")

    op.add_column("bom_lines", sa.Column("line_sequence", sa.Integer(), nullable=True))
    op.add_column(
        "bom_lines",
        sa.Column("yield_percentage", sa.Numeric(8, 4), nullable=False, server_default="0"),
    )
    op.add_column(
        "bom_lines",
        sa.Column("is_phantom", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("bom_lines", sa.Column("lead_time_offset_days", sa.Integer(), nullable=True))

    op.execute(
        sa.text(
            "UPDATE bom_lines bl SET line_sequence = sub.rn FROM ("
            "SELECT id, ROW_NUMBER() OVER (PARTITION BY parent_item_id ORDER BY id) AS rn "
            "FROM bom_lines) sub WHERE bl.id = sub.id",
        ),
    )
    op.alter_column("bom_lines", "line_sequence", nullable=False)
    op.create_unique_constraint(
        "uq_bom_lines_parent_sequence",
        "bom_lines",
        ["parent_item_id", "line_sequence"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_bom_lines_parent_sequence", "bom_lines", type_="unique")
    op.drop_column("bom_lines", "lead_time_offset_days")
    op.drop_column("bom_lines", "is_phantom")
    op.drop_column("bom_lines", "yield_percentage")
    op.drop_column("bom_lines", "line_sequence")

    op.add_column(
        "bom_headers",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.execute(
        sa.text(
            "UPDATE bom_headers SET is_active = (status = 'ACTIVE'::bomstatus)",
        ),
    )

    op.drop_constraint("fk_bom_headers_updated_by_id", "bom_headers", type_="foreignkey")
    op.drop_constraint("fk_bom_headers_created_by_id", "bom_headers", type_="foreignkey")
    op.drop_constraint("fk_bom_headers_approved_by_id", "bom_headers", type_="foreignkey")
    op.drop_constraint("uq_bom_headers_bom_number", "bom_headers", type_="unique")
    op.drop_column("bom_headers", "updated_at")
    op.drop_column("bom_headers", "updated_by_id")
    op.drop_column("bom_headers", "created_at")
    op.drop_column("bom_headers", "created_by_id")
    op.drop_column("bom_headers", "approved_by_id")
    op.drop_column("bom_headers", "approved_at")
    op.drop_column("bom_headers", "eco_number")
    op.drop_column("bom_headers", "effective_end_date")
    op.drop_column("bom_headers", "effective_start_date")
    op.drop_column("bom_headers", "bom_type")
    op.drop_column("bom_headers", "status")
    op.drop_column("bom_headers", "bom_number")

    bind = op.get_bind()
    sa.Enum("DRAFT", "ACTIVE", "OBSOLETE", "SUPERSEDED", name="bomstatus").drop(bind, checkfirst=True)
    sa.Enum(
        "MANUFACTURING",
        "ENGINEERING",
        "SALES",
        "SERVICE",
        "PHANTOM",
        name="bomtype",
    ).drop(bind, checkfirst=True)
