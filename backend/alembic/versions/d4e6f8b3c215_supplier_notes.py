"""supplier notes

Revision ID: d4e6f8b3c215
Revises: c3d5f7a2b104
Create Date: 2026-05-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e6f8b3c215"
down_revision: Union[str, None] = "c3d5f7a2b104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("suppliers", "notes")
