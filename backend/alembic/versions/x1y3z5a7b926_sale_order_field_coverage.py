"""sale order field coverage — alternate UOM on lines

Revision ID: x1y3z5a7b926
Revises: w0x2y4a6b825
Create Date: 2026-05-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "x1y3z5a7b926"
down_revision: Union[str, None] = "w0x2y4a6b825"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE saleordersource ADD VALUE IF NOT EXISTS 'WEBSITE'")
    op.execute("ALTER TABLE sale_items ADD COLUMN IF NOT EXISTS alternate_uom VARCHAR(32)")
    op.execute(
        "ALTER TABLE sale_items ADD COLUMN IF NOT EXISTS uom_conversion_factor NUMERIC(12, 6)"
    )


def downgrade() -> None:
    op.drop_column("sale_items", "uom_conversion_factor")
    op.drop_column("sale_items", "alternate_uom")
