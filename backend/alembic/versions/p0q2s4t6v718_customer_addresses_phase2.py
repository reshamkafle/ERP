"""Customer addresses and contact extensions

Revision ID: p0q2s4t6v718
Revises: o9p1r3t5u617
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p0q2s4t6v718"
down_revision: Union[str, None] = "o9p1r3t5u617"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADDRESS_TYPES = ("PRIMARY", "BILLING", "SHIPPING", "OTHER")


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*ADDRESS_TYPES, name="customeraddresstype").create(bind, checkfirst=True)
    addr_type = postgresql.ENUM(*ADDRESS_TYPES, name="customeraddresstype", create_type=False)

    inspector = sa.inspect(bind)
    if "customer_addresses" in inspector.get_table_names():
        if "title" not in [c["name"] for c in inspector.get_columns("customer_contacts")]:
            op.add_column("customer_contacts", sa.Column("title", sa.String(120), nullable=True))
            op.add_column("customer_contacts", sa.Column("department", sa.String(120), nullable=True))
        return

    op.create_table(
        "customer_addresses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("address_type", addr_type, nullable=False),
        sa.Column("label", sa.String(64), nullable=True),
        sa.Column("line1", sa.String(255), nullable=True),
        sa.Column("line2", sa.String(255), nullable=True),
        sa.Column("house_no", sa.String(32), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("state", sa.String(120), nullable=True),
        sa.Column("postal_code", sa.String(32), nullable=True),
        sa.Column("country", sa.String(64), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_customer_addresses_customer_id", "customer_addresses", ["customer_id"])

    op.add_column("customer_contacts", sa.Column("title", sa.String(120), nullable=True))
    op.add_column("customer_contacts", sa.Column("department", sa.String(120), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT id, billing_address_line1, billing_address_line2, billing_city, billing_state,
                   billing_postal_code, billing_country,
                   shipping_address_line1, shipping_address_line2, shipping_city, shipping_state,
                   shipping_postal_code, shipping_country
            FROM customers
            """
        )
    ).fetchall()
    for row in rows:
        cid = row[0]
        if any(row[1:7]):
            conn.execute(
                sa.text(
                    """
                    INSERT INTO customer_addresses
                    (customer_id, address_type, line1, line2, city, state, postal_code, country, is_default)
                    VALUES (:cid, 'BILLING', :l1, :l2, :city, :state, :postal, :country, true)
                    """
                ),
                {
                    "cid": cid,
                    "l1": row[1],
                    "l2": row[2],
                    "city": row[3],
                    "state": row[4],
                    "postal": row[5],
                    "country": row[6],
                },
            )
        if any(row[7:13]):
            conn.execute(
                sa.text(
                    """
                    INSERT INTO customer_addresses
                    (customer_id, address_type, line1, line2, city, state, postal_code, country, is_default)
                    VALUES (:cid, 'SHIPPING', :l1, :l2, :city, :state, :postal, :country, true)
                    """
                ),
                {
                    "cid": cid,
                    "l1": row[7],
                    "l2": row[8],
                    "city": row[9],
                    "state": row[10],
                    "postal": row[11],
                    "country": row[12],
                },
            )


def downgrade() -> None:
    op.drop_column("customer_contacts", "department")
    op.drop_column("customer_contacts", "title")
    op.drop_index("ix_customer_addresses_customer_id", table_name="customer_addresses")
    op.drop_table("customer_addresses")
    bind = op.get_bind()
    postgresql.ENUM(name="customeraddresstype").drop(bind, checkfirst=True)
