from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ModuleRecordBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    status: str = Field(default="DRAFT", max_length=32)
    description: str | None = None
    party_name: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = None
    quantity: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    extra_data: dict | None = None


class ModuleRecordCreate(ModuleRecordBase):
    feature_code: str = Field(min_length=1, max_length=64)
    reference: str = Field(min_length=1, max_length=64)


class ModuleRecordUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = Field(default=None, max_length=32)
    description: str | None = None
    party_name: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = None
    quantity: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    extra_data: dict | None = None


class ModuleRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_code: str
    feature_code: str
    reference: str
    title: str
    status: str
    description: str | None
    party_name: str | None
    amount: Decimal | None
    quantity: int | None
    start_date: date | None
    end_date: date | None
    extra_data: dict | None
    created_at: datetime
    updated_at: datetime


class ModuleRecordListResponse(BaseModel):
    items: list[ModuleRecordRead]
    total: int


class ModuleFeatureCount(BaseModel):
    code: str
    name: str
    description: str
    record_count: int


class ModuleIntegrationMetric(BaseModel):
    label: str
    value: str
    hint: str | None = None


class ModuleOverviewResponse(BaseModel):
    module_code: str
    module_name: str
    description: str
    features: list[ModuleFeatureCount]
    integration_metrics: list[ModuleIntegrationMetric]
    total_records: int


class ModuleFeatureDefRead(BaseModel):
    code: str
    name: str
    description: str


class ModuleDefRead(BaseModel):
    code: str
    name: str
    short_name: str
    description: str
    route_path: str
    permission_read: str
    permission_write: str
    linked_routes: list[str]
    features: list[ModuleFeatureDefRead]


class ModuleCatalogResponse(BaseModel):
    modules: list[ModuleDefRead]
