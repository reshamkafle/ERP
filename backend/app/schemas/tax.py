from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TaxType


class TaxRateCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    rate_percent: Decimal = Field(ge=0, le=100)
    tax_type: TaxType = TaxType.OTHER
    country_code: str = Field(min_length=2, max_length=2)
    effective_from: date
    effective_to: date | None = None
    is_active: bool = True

    @field_validator("effective_to")
    @classmethod
    def validate_dates(cls, v: date | None, info) -> date | None:
        if v is not None and info.data.get("effective_from") and v < info.data["effective_from"]:
            raise ValueError("effective_to must be on or after effective_from")
        return v


class TaxRateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    rate_percent: Decimal | None = Field(default=None, ge=0, le=100)
    tax_type: TaxType | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    is_active: bool | None = None


class TaxRateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    rate_percent: Decimal
    tax_type: TaxType
    country_code: str
    effective_from: date
    effective_to: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TaxRateListResponse(BaseModel):
    items: list[TaxRateRead]
    total: int
