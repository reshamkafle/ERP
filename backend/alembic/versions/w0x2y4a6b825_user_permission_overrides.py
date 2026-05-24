"""user permission overrides

Revision ID: w0x2y4a6b825
Revises: v9x1y3z5a724
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "w0x2y4a6b825"
down_revision: Union[str, None] = "v9x1y3z5a724"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "user_permission_overrides" not in inspector.get_table_names():
        op.create_table(
            "user_permission_overrides",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("permission_id", sa.Integer(), nullable=False),
            sa.Column("granted", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "permission_id", name="uq_user_permission_override"),
        )
        op.create_index(
            "ix_user_permission_overrides_user_id",
            "user_permission_overrides",
            ["user_id"],
        )
        op.create_index(
            "ix_user_permission_overrides_permission_id",
            "user_permission_overrides",
            ["permission_id"],
        )


def downgrade() -> None:
    op.drop_index("ix_user_permission_overrides_permission_id", table_name="user_permission_overrides")
    op.drop_index("ix_user_permission_overrides_user_id", table_name="user_permission_overrides")
    op.drop_table("user_permission_overrides")
