"""promotion agent runs (HITL proposals)

Revision ID: f8a9b0c1d2e3
Revises: e5f7a1b2c904
Create Date: 2026-05-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, None] = "e5f7a1b2c904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    promotionrunstatus = postgresql.ENUM(
        "IN_PROGRESS",
        "DRAFT_REVIEW",
        "APPROVED",
        "REJECTED",
        "FAILED",
        name="promotionrunstatus",
        create_type=False,
    )
    promotionrunstatus.create(bind, checkfirst=True)

    insp = inspect(bind)
    if not insp.has_table("promotion_runs"):
        op.create_table(
            "promotion_runs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("status", promotionrunstatus, nullable=False),
            sa.Column("proposals_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("approved_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if insp.has_table("promotion_runs"):
        op.drop_table("promotion_runs")
    promotionrunstatus = postgresql.ENUM(name="promotionrunstatus")
    promotionrunstatus.drop(bind, checkfirst=True)
