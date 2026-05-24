"""erp operational documents (journey)

Revision ID: c2d4e6f8b019
Revises: b1d3e5f7a908
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "c2d4e6f8b019"
down_revision: Union[str, None] = "b1d3e5f7a908"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ERP_DOCUMENT_TYPES = (
    "TECH_PACK",
    "BOM",
    "PURCHASE_ORDER",
    "GRN",
    "INSPECTION_REPORT",
    "LAB_TEST_REPORT",
    "PRODUCTION_ORDER",
    "STOCK_TRANSFER",
    "INVENTORY_ADJUSTMENT",
    "PICK_LIST",
    "PACKING_LIST",
    "SHIPPING_MARKS",
    "ASN",
    "COMMERCIAL_INVOICE",
    "OUTGOING_INVOICE",
    "BILL_OF_LADING",
    "CERTIFICATE_OF_ORIGIN",
    "EXPORT_DECLARATION",
    "LETTER_OF_CREDIT",
    "BILL_OF_EXCHANGE",
    "PROOF_OF_DELIVERY",
    "PAYMENT_RECORD",
    "LANDED_COST",
)

ERP_DOCUMENT_STATUSES = ("DRAFT", "ISSUED", "CONFIRMED", "CANCELLED")


def upgrade() -> None:
    bind = op.get_bind()
    doc_type_enum = postgresql.ENUM(*ERP_DOCUMENT_TYPES, name="erpdocumenttype", create_type=False)
    doc_status_enum = postgresql.ENUM(
        *ERP_DOCUMENT_STATUSES,
        name="erpdocumentstatus",
        create_type=False,
    )
    doc_type_enum.create(bind, checkfirst=True)
    doc_status_enum.create(bind, checkfirst=True)

    insp = inspect(bind)
    if not insp.has_table("erp_documents"):
        op.create_table(
            "erp_documents",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("document_number", sa.String(length=64), nullable=False),
            sa.Column("document_type", doc_type_enum, nullable=False),
            sa.Column("journey_step", sa.Integer(), nullable=False),
            sa.Column("phase", sa.String(length=128), nullable=False),
            sa.Column("status", doc_status_enum, nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("reference_number", sa.String(length=128), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "content",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column("supplier_id", sa.Integer(), nullable=True),
            sa.Column("customer_id", sa.Integer(), nullable=True),
            sa.Column("purchase_id", sa.Integer(), nullable=True),
            sa.Column("related_document_id", sa.Integer(), nullable=True),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
            sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"]),
            sa.ForeignKeyConstraint(["related_document_id"], ["erp_documents.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("document_number"),
        )
        op.create_index("ix_erp_documents_document_number", "erp_documents", ["document_number"])
        op.create_index("ix_erp_documents_document_type", "erp_documents", ["document_type"])
        op.create_index("ix_erp_documents_journey_step", "erp_documents", ["journey_step"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if insp.has_table("erp_documents"):
        op.drop_index("ix_erp_documents_journey_step", table_name="erp_documents")
        op.drop_index("ix_erp_documents_document_type", table_name="erp_documents")
        op.drop_index("ix_erp_documents_document_number", table_name="erp_documents")
        op.drop_table("erp_documents")
    postgresql.ENUM(name="erpdocumentstatus").drop(bind, checkfirst=True)
    postgresql.ENUM(name="erpdocumenttype").drop(bind, checkfirst=True)
