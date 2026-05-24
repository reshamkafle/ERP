from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromotionRunCreateBody(BaseModel):
    sales_lookback_days: int = Field(default=30, ge=1, le=365)
    max_anchor_products: int = Field(default=15, ge=1, le=200)
    max_related_per_anchor: int = Field(default=5, ge=1, le=30)
    max_projects: int = Field(default=25, ge=1, le=100)
    category_id: int | None = Field(default=None, ge=1)
    co_purchase_pair_limit: int = Field(default=800, ge=10, le=5000)


class PromotionRelatedItemConfirm(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product_id: int = Field(ge=1)
    sku: str = Field(default="", max_length=100)
    name: str = Field(default="", max_length=255)
    relationship_note: str = Field(default="", max_length=500)


class PromotionAnchorConfirm(BaseModel):
    model_config = ConfigDict(extra="ignore")

    product_id: int = Field(ge=1)
    sku: str = Field(default="", max_length=100)
    name: str = Field(default="", max_length=255)


class PromotionProjectConfirm(BaseModel):
    model_config = ConfigDict(extra="ignore")

    project_id: str = Field(default="", max_length=64)
    anchor: PromotionAnchorConfirm
    related_items: list[PromotionRelatedItemConfirm] = Field(default_factory=list)
    discount_kind: Literal["percent", "fixed"] = "percent"
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    discount_amount: str | None = Field(default=None, max_length=32)
    duration_days: int = Field(default=14, ge=1, le=365)
    start_date: str | None = Field(default=None, max_length=32)
    end_date: str | None = Field(default=None, max_length=32)
    rationale: str = Field(default="", max_length=2000)
    confidence: str = Field(default="medium", max_length=32)

    @field_validator("discount_amount")
    @classmethod
    def validate_discount_amount(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return value
        try:
            amount = Decimal(value)
        except Exception as exc:
            msg = "discount_amount must be a decimal string"
            raise ValueError(msg) from exc
        if amount < 0:
            msg = "discount_amount must be non-negative"
            raise ValueError(msg)
        return value


class PromotionConfirmBody(BaseModel):
    """Manager-edited project list. Empty projects with reject=false approves none."""

    projects: list[PromotionProjectConfirm] = Field(default_factory=list)
    reject: bool = False


class PromotionRunResponse(BaseModel):
    id: int
    status: str
    warnings: list[str]
    error_message: str | None = None


class PromotionRunDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    proposals_json: dict[str, Any] | None
    approved_json: dict[str, Any] | None
    error_message: str | None
