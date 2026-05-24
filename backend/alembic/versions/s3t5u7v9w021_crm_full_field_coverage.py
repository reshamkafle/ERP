"""CRM full field coverage

Revision ID: s3t5u7v9w021
Revises: r2s4t6v820
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "s3t5u7v9w021"
down_revision: Union[str, None] = "r2s4t6v820"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return column in {c["name"] for c in insp.get_columns(table)}


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    if not _has_column("customers", "year_founded"):
        op.add_column("customers", sa.Column("year_founded", sa.Integer(), nullable=True))
    if not _has_column("customers", "ownership_type"):
        op.add_column("customers", sa.Column("ownership_type", sa.String(length=64), nullable=True))
    if not _has_column("customers", "territory"):
        op.add_column("customers", sa.Column("territory", sa.String(length=120), nullable=True))
    if not _has_column("customers", "employee_count"):
        op.add_column("customers", sa.Column("employee_count", sa.Integer(), nullable=True))
    if not _has_column("customers", "account_owner_id"):
        op.add_column(
            "customers",
            sa.Column("account_owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        )
        op.create_index("ix_customers_account_owner_id", "customers", ["account_owner_id"])

    contact_cols = [
        ("contact_code", sa.String(length=32)),
        ("salutation", sa.String(length=32)),
        ("first_name", sa.String(length=120)),
        ("middle_name", sa.String(length=120)),
        ("last_name", sa.String(length=120)),
        ("phone_secondary", sa.String(length=64)),
        ("email_secondary", sa.String(length=255)),
        ("linkedin_url", sa.String(length=512)),
        ("preferred_language", sa.String(length=64)),
    ]
    for col_name, col_type in contact_cols:
        if not _has_column("customer_contacts", col_name):
            op.add_column("customer_contacts", sa.Column(col_name, col_type, nullable=True))
    if not _has_column("customer_contacts", "social_profiles"):
        op.add_column("customer_contacts", sa.Column("social_profiles", postgresql.JSONB(), nullable=True))
    if not _has_column("customer_contacts", "birthday"):
        op.add_column("customer_contacts", sa.Column("birthday", sa.Date(), nullable=True))
    if not _has_column("customer_contacts", "anniversary"):
        op.add_column("customer_contacts", sa.Column("anniversary", sa.Date(), nullable=True))
    if not _has_column("customer_contacts", "reports_to_id"):
        op.add_column(
            "customer_contacts",
            sa.Column(
                "reports_to_id",
                sa.Integer(),
                sa.ForeignKey("customer_contacts.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )

    lead_cols = [
        ("lead_score", sa.Integer()),
        ("campaign_source", sa.String(length=120)),
        ("expected_close_date", sa.Date()),
        ("bant_budget", sa.String(length=255)),
        ("bant_authority", sa.String(length=255)),
        ("bant_need", sa.String(length=255)),
        ("bant_timeline", sa.String(length=255)),
    ]
    for col_name, col_type in lead_cols:
        if not _has_column("crm_leads", col_name):
            op.add_column("crm_leads", sa.Column(col_name, col_type, nullable=True))

    if not _has_column("crm_opportunities", "competitor_info"):
        op.add_column("crm_opportunities", sa.Column("competitor_info", sa.Text(), nullable=True))

    activity_cols = [
        ("duration_minutes", sa.Integer()),
        ("outcome", sa.String(length=255)),
        ("next_follow_up_at", sa.DateTime(timezone=True)),
        ("attachments", postgresql.JSONB()),
    ]
    for col_name, col_type in activity_cols:
        if not _has_column("crm_activities", col_name):
            op.add_column("crm_activities", sa.Column(col_name, col_type, nullable=True))

    if not _has_table("crm_opportunity_stage_history"):
        op.create_table(
        "crm_opportunity_stage_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("opportunity_id", sa.Integer(), nullable=False),
        sa.Column("from_stage", sa.String(length=32), nullable=True),
        sa.Column("to_stage", sa.String(length=32), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm_opportunities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_crm_opportunity_stage_history_opportunity_id",
            "crm_opportunity_stage_history",
            ["opportunity_id"],
        )

    for val in ("HEAD_OFFICE", "BRANCH", "FACTORY"):
        op.execute(sa.text(f"ALTER TYPE customeraddresstype ADD VALUE IF NOT EXISTS '{val}'"))

    for val in ("TASK", "DEMO", "SITE_VISIT"):
        op.execute(sa.text(f"ALTER TYPE crmactivitytype ADD VALUE IF NOT EXISTS '{val}'"))


def downgrade() -> None:
    op.drop_table("crm_opportunity_stage_history")

    op.drop_column("crm_activities", "attachments")
    op.drop_column("crm_activities", "next_follow_up_at")
    op.drop_column("crm_activities", "outcome")
    op.drop_column("crm_activities", "duration_minutes")

    op.drop_column("crm_opportunities", "competitor_info")

    for col in ("bant_timeline", "bant_need", "bant_authority", "bant_budget", "expected_close_date", "campaign_source", "lead_score"):
        op.drop_column("crm_leads", col)

    op.drop_column("customer_contacts", "reports_to_id")
    op.drop_column("customer_contacts", "anniversary")
    op.drop_column("customer_contacts", "birthday")
    op.drop_column("customer_contacts", "social_profiles")
    for col in (
        "preferred_language",
        "linkedin_url",
        "email_secondary",
        "phone_secondary",
        "last_name",
        "middle_name",
        "first_name",
        "salutation",
        "contact_code",
    ):
        op.drop_column("customer_contacts", col)

    op.drop_index("ix_customers_account_owner_id", table_name="customers")
    for col in ("account_owner_id", "employee_count", "territory", "ownership_type", "year_founded"):
        op.drop_column("customers", col)
