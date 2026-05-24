from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.crm import build_contact_display_name
from app.models.enums import (
    CommunicationChannel,
    CrmActivityType,
    InfluenceLevel,
    LeadStatus,
    OpportunityStage,
)


class CustomerContactBase(BaseModel):
    contact_code: str | None = Field(default=None, max_length=32)
    salutation: str | None = Field(default=None, max_length=32)
    first_name: str | None = Field(default=None, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    email_secondary: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    phone_secondary: str | None = Field(default=None, max_length=64)
    title: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=120)
    is_primary: bool = False
    preferred_channel: CommunicationChannel | None = None
    influence_level: InfluenceLevel | None = None
    relationship_strength: str | None = Field(default=None, max_length=32)
    linkedin_url: str | None = Field(default=None, max_length=512)
    social_profiles: dict[str, Any] | None = None
    birthday: date | None = None
    anniversary: date | None = None
    preferred_language: str | None = Field(default=None, max_length=64)
    reports_to_id: int | None = None
    notes: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def resolve_name(cls, v: str | None, info) -> str:
        if v and str(v).strip():
            return str(v).strip()
        data = info.data
        return build_contact_display_name(
            salutation=data.get("salutation"),
            first_name=data.get("first_name"),
            middle_name=data.get("middle_name"),
            last_name=data.get("last_name"),
            fallback="Contact",
        )


class CustomerContactCreate(CustomerContactBase):
    pass


class CustomerContactUpdate(BaseModel):
    contact_code: str | None = Field(default=None, max_length=32)
    salutation: str | None = Field(default=None, max_length=32)
    first_name: str | None = Field(default=None, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    email_secondary: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    phone_secondary: str | None = Field(default=None, max_length=64)
    title: str | None = Field(default=None, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=120)
    is_primary: bool | None = None
    preferred_channel: CommunicationChannel | None = None
    influence_level: InfluenceLevel | None = None
    relationship_strength: str | None = Field(default=None, max_length=32)
    linkedin_url: str | None = Field(default=None, max_length=512)
    social_profiles: dict[str, Any] | None = None
    birthday: date | None = None
    anniversary: date | None = None
    preferred_language: str | None = Field(default=None, max_length=64)
    reports_to_id: int | None = None
    notes: str | None = None


class CustomerContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    contact_code: str | None
    salutation: str | None
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    name: str
    email: str | None
    email_secondary: str | None
    phone: str | None
    phone_secondary: str | None
    title: str | None
    department: str | None
    role: str | None
    is_primary: bool
    preferred_channel: CommunicationChannel | None
    influence_level: InfluenceLevel | None
    relationship_strength: str | None
    linkedin_url: str | None
    social_profiles: dict[str, Any] | None
    birthday: date | None
    anniversary: date | None
    preferred_language: str | None
    reports_to_id: int | None
    notes: str | None
    created_at: datetime


class CrmActivityBase(BaseModel):
    activity_type: CrmActivityType
    subject: str = Field(min_length=1, max_length=255)
    body: str | None = None
    occurred_at: datetime
    contact_id: int | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    outcome: str | None = Field(default=None, max_length=255)
    next_follow_up_at: datetime | None = None
    attachments: list[dict[str, Any]] | None = None


class CrmActivityCreate(CrmActivityBase):
    pass


class CrmActivityUpdate(BaseModel):
    activity_type: CrmActivityType | None = None
    subject: str | None = Field(default=None, min_length=1, max_length=255)
    body: str | None = None
    occurred_at: datetime | None = None
    contact_id: int | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    outcome: str | None = Field(default=None, max_length=255)
    next_follow_up_at: datetime | None = None
    attachments: list[dict[str, Any]] | None = None


class CrmActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    contact_id: int | None
    activity_type: CrmActivityType
    subject: str
    body: str | None
    occurred_at: datetime
    duration_minutes: int | None
    outcome: str | None
    next_follow_up_at: datetime | None
    attachments: list[dict[str, Any]] | None
    created_by_id: int | None
    created_at: datetime


class CrmLeadBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    contact_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    source: str | None = Field(default=None, max_length=120)
    status: LeadStatus = LeadStatus.NEW
    customer_id: int | None = None
    owner_id: int | None = None
    lead_score: int | None = Field(default=None, ge=0, le=100)
    campaign_source: str | None = Field(default=None, max_length=120)
    expected_close_date: date | None = None
    bant_budget: str | None = Field(default=None, max_length=255)
    bant_authority: str | None = Field(default=None, max_length=255)
    bant_need: str | None = Field(default=None, max_length=255)
    bant_timeline: str | None = Field(default=None, max_length=255)
    description: str | None = None


class CrmLeadCreate(CrmLeadBase):
    pass


class CrmLeadUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    contact_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    source: str | None = Field(default=None, max_length=120)
    status: LeadStatus | None = None
    customer_id: int | None = None
    owner_id: int | None = None
    lead_score: int | None = Field(default=None, ge=0, le=100)
    campaign_source: str | None = Field(default=None, max_length=120)
    expected_close_date: date | None = None
    bant_budget: str | None = Field(default=None, max_length=255)
    bant_authority: str | None = Field(default=None, max_length=255)
    bant_need: str | None = Field(default=None, max_length=255)
    bant_timeline: str | None = Field(default=None, max_length=255)
    description: str | None = None


class CrmLeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int | None
    company_name: str
    contact_name: str | None
    email: str | None
    phone: str | None
    source: str | None
    status: LeadStatus
    owner_id: int | None
    lead_score: int | None
    campaign_source: str | None
    expected_close_date: date | None
    bant_budget: str | None
    bant_authority: str | None
    bant_need: str | None
    bant_timeline: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class CrmLeadListResponse(BaseModel):
    items: list[CrmLeadRead]
    total: int


class CrmOpportunityBase(BaseModel):
    customer_id: int
    title: str = Field(min_length=1, max_length=255)
    stage: OpportunityStage = OpportunityStage.PROSPECTING
    probability: int = Field(default=10, ge=0, le=100)
    expected_value: Decimal | None = Field(default=None, ge=0)
    close_date: date | None = None
    lead_id: int | None = None
    owner_id: int | None = None
    competitor_info: str | None = None
    description: str | None = None
    win_loss_reason: str | None = Field(default=None, max_length=255)


class CrmOpportunityCreate(CrmOpportunityBase):
    pass


class CrmOpportunityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    stage: OpportunityStage | None = None
    probability: int | None = Field(default=None, ge=0, le=100)
    expected_value: Decimal | None = Field(default=None, ge=0)
    close_date: date | None = None
    lead_id: int | None = None
    owner_id: int | None = None
    competitor_info: str | None = None
    description: str | None = None
    win_loss_reason: str | None = Field(default=None, max_length=255)
    sale_id: int | None = None


class CrmOpportunityStageHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    opportunity_id: int
    from_stage: str | None
    to_stage: str
    changed_at: datetime
    changed_by_id: int | None


class CrmOpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    lead_id: int | None
    title: str
    stage: OpportunityStage
    probability: int
    expected_value: Decimal | None
    close_date: date | None
    win_loss_reason: str | None
    competitor_info: str | None
    sale_id: int | None
    owner_id: int | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    stage_history: list[CrmOpportunityStageHistoryRead] = Field(default_factory=list)


class CrmOpportunityListResponse(BaseModel):
    items: list[CrmOpportunityRead]
    total: int


class PipelineStageSummary(BaseModel):
    stage: OpportunityStage
    count: int
    total_value: Decimal


class PipelineSummaryRead(BaseModel):
    stages: list[PipelineStageSummary]
    open_lead_count: int
    total_open_value: Decimal
