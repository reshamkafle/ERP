from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PromotionRunCreateBody(BaseModel):
    sales_lookback_days: int = Field(default=30, ge=1, le=365)
    max_anchor_products: int = Field(default=15, ge=1, le=200)
    max_related_per_anchor: int = Field(default=5, ge=1, le=30)
    max_projects: int = Field(default=25, ge=1, le=100)
    category_id: int | None = Field(default=None, ge=1)
    co_purchase_pair_limit: int = Field(default=800, ge=10, le=5000)


class PromotionConfirmBody(BaseModel):
    """Manager-edited project list. Empty projects with reject=false approves none."""

    projects: list[dict[str, Any]] = Field(default_factory=list)
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
