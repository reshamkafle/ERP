"""CRM contacts, activities, leads, opportunities

Revision ID: n8p0r2t4u516
Revises: m7o9q1s3t415
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "n8p0r2t4u516"
down_revision: Union[str, None] = "m7o9q1s3t415"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COMMUNICATION_CHANNELS = ("EMAIL", "PHONE", "SMS", "IN_PERSON", "PORTAL")
INFLUENCE_LEVELS = ("LOW", "MEDIUM", "HIGH", "DECISION_MAKER")
ACTIVITY_TYPES = ("CALL", "EMAIL", "MEETING", "NOTE", "VISIT")
LEAD_STATUSES = ("NEW", "CONTACTED", "QUALIFIED", "UNQUALIFIED", "CONVERTED", "LOST")
OPPORTUNITY_STAGES = (
    "PROSPECTING",
    "QUALIFICATION",
    "PROPOSAL",
    "NEGOTIATION",
    "CLOSED_WON",
    "CLOSED_LOST",
)


def _enum(name: str, values: tuple[str, ...]) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    for name, values in (
        ("communicationchannel", COMMUNICATION_CHANNELS),
        ("influencelevel", INFLUENCE_LEVELS),
        ("crmactivitytype", ACTIVITY_TYPES),
        ("leadstatus", LEAD_STATUSES),
        ("opportunitystage", OPPORTUNITY_STAGES),
    ):
        postgresql.ENUM(*values, name=name).create(bind, checkfirst=True)

    channel = _enum("communicationchannel", COMMUNICATION_CHANNELS)
    influence = _enum("influencelevel", INFLUENCE_LEVELS)
    activity_type = _enum("crmactivitytype", ACTIVITY_TYPES)
    lead_status = _enum("leadstatus", LEAD_STATUSES)
    opp_stage = _enum("opportunitystage", OPPORTUNITY_STAGES)

    op.create_table(
        "customer_contacts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("role", sa.String(120), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("preferred_channel", channel, nullable=True),
        sa.Column("influence_level", influence, nullable=True),
        sa.Column("relationship_strength", sa.String(32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "ix_customer_contacts_customer_id",
        "customer_contacts",
        ["customer_id"],
        if_not_exists=True,
    )

    op.create_table(
        "crm_activities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=True),
        sa.Column("activity_type", activity_type, nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contact_id"], ["customer_contacts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "ix_crm_activities_customer_id",
        "crm_activities",
        ["customer_id"],
        if_not_exists=True,
    )

    op.create_table(
        "crm_leads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("source", sa.String(120), nullable=True),
        sa.Column("status", lead_status, nullable=False, server_default="NEW"),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )

    op.create_table(
        "crm_opportunities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("stage", opp_stage, nullable=False, server_default="PROSPECTING"),
        sa.Column("probability", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("expected_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("close_date", sa.Date(), nullable=True),
        sa.Column("win_loss_reason", sa.String(255), nullable=True),
        sa.Column("sale_id", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["crm_leads.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_index(
        "ix_crm_opportunities_customer_id",
        "crm_opportunities",
        ["customer_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("crm_opportunities")
    op.drop_table("crm_leads")
    op.drop_table("crm_activities")
    op.drop_table("customer_contacts")
    bind = op.get_bind()
    for name in (
        "opportunitystage",
        "leadstatus",
        "crmactivitytype",
        "influencelevel",
        "communicationchannel",
    ):
        postgresql.ENUM(name=name).drop(bind, checkfirst=True)
