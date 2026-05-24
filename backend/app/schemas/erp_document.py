from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ErpDocumentStatus, ErpDocumentType


class JourneyStepRead(BaseModel):
    document_type: ErpDocumentType
    journey_step: int
    phase: str
    label: str
    slug: str
    number_prefix: str


class JourneyResponse(BaseModel):
    steps: list[JourneyStepRead]
    phases: list[str]


class ErpDocumentBase(BaseModel):
    document_type: ErpDocumentType
    title: str = Field(min_length=1, max_length=255)
    reference_number: str | None = Field(default=None, max_length=128)
    notes: str | None = None
    content: dict[str, Any] = Field(default_factory=dict)
    supplier_id: int | None = None
    customer_id: int | None = None
    purchase_id: int | None = None
    sale_id: int | None = None
    related_document_id: int | None = None


class ErpDocumentCreate(ErpDocumentBase):
    status: ErpDocumentStatus = ErpDocumentStatus.DRAFT


class ErpDocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: ErpDocumentStatus | None = None
    reference_number: str | None = Field(default=None, max_length=128)
    notes: str | None = None
    content: dict[str, Any] | None = None
    supplier_id: int | None = None
    customer_id: int | None = None
    purchase_id: int | None = None
    sale_id: int | None = None
    related_document_id: int | None = None


class ErpDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_number: str
    document_type: ErpDocumentType
    type_label: str
    journey_step: int
    phase: str
    status: ErpDocumentStatus
    title: str
    reference_number: str | None
    notes: str | None
    content: dict[str, Any]
    supplier_id: int | None
    customer_id: int | None
    purchase_id: int | None
    sale_id: int | None
    related_document_id: int | None
    created_by_id: int | None
    created_at: datetime
    updated_at: datetime


class ErpDocumentListResponse(BaseModel):
    items: list[ErpDocumentRead]
    total: int


class ErpDocumentJourneyGroup(BaseModel):
    phase: str
    journey_step_start: int
    steps: list[JourneyStepRead]
    documents: list[ErpDocumentRead]


class ErpDocumentJourneyViewResponse(BaseModel):
    phases: list[ErpDocumentJourneyGroup]
    total_documents: int
