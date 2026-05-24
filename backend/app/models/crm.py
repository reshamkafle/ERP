from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    CommunicationChannel,
    CrmActivityType,
    InfluenceLevel,
    LeadStatus,
    OpportunityStage,
)


def build_contact_display_name(
    *,
    salutation: str | None = None,
    first_name: str | None = None,
    middle_name: str | None = None,
    last_name: str | None = None,
    fallback: str | None = None,
) -> str:
    parts = [p for p in (salutation, first_name, middle_name, last_name) if p and str(p).strip()]
    if parts:
        return " ".join(str(p).strip() for p in parts)
    if fallback and str(fallback).strip():
        return str(fallback).strip()
    return "Contact"


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    contact_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    salutation: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_secondary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone_secondary: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    department: Mapped[str | None] = mapped_column(String(120), nullable=True)
    role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    preferred_channel: Mapped[CommunicationChannel | None] = mapped_column(
        Enum(CommunicationChannel, name="communicationchannel", create_constraint=False),
        nullable=True,
    )
    influence_level: Mapped[InfluenceLevel | None] = mapped_column(
        Enum(InfluenceLevel, name="influencelevel", create_constraint=False),
        nullable=True,
    )
    relationship_strength: Mapped[str | None] = mapped_column(String(32), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    social_profiles: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)
    anniversary: Mapped[date | None] = mapped_column(Date, nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reports_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer_contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="contacts")
    activities: Mapped[list["CrmActivity"]] = relationship(back_populates="contact")
    reports_to: Mapped[CustomerContact | None] = relationship(
        remote_side="CustomerContact.id",
        foreign_keys=[reports_to_id],
    )


class CrmActivity(Base):
    __tablename__ = "crm_activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer_contacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    activity_type: Mapped[CrmActivityType] = mapped_column(
        Enum(CrmActivityType, name="crmactivitytype", create_constraint=False),
        nullable=False,
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(255), nullable=True)
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attachments: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="activities")
    contact: Mapped[CustomerContact | None] = relationship(back_populates="activities")


class CrmLead(Base):
    __tablename__ = "crm_leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="leadstatus", create_constraint=False),
        nullable=False,
        default=LeadStatus.NEW,
    )
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    campaign_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expected_close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bant_budget: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bant_authority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bant_need: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bant_timeline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer | None"] = relationship(back_populates="leads")
    opportunities: Mapped[list["CrmOpportunity"]] = relationship(back_populates="lead")


class CrmOpportunity(Base):
    __tablename__ = "crm_opportunities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, name="opportunitystage", create_constraint=False),
        nullable=False,
        default=OpportunityStage.PROSPECTING,
    )
    probability: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    expected_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    close_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    win_loss_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    competitor_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id", ondelete="SET NULL"), nullable=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(back_populates="opportunities")
    lead: Mapped[CrmLead | None] = relationship(back_populates="opportunities")
    stage_history: Mapped[list["CrmOpportunityStageHistory"]] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan",
        order_by="CrmOpportunityStageHistory.changed_at.desc()",
    )


class CrmOpportunityStageHistory(Base):
    __tablename__ = "crm_opportunity_stage_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(
        ForeignKey("crm_opportunities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    from_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_stage: Mapped[str] = mapped_column(String(32), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    changed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    opportunity: Mapped[CrmOpportunity] = relationship(back_populates="stage_history")
