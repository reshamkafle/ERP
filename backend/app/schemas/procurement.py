from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProcurementRunCreateBody(BaseModel):
    sales_lookback_days: int = Field(default=14, ge=1, le=365)
    max_lines_per_supplier: int = Field(default=50, ge=1, le=200)
    velocity_limit: int = Field(default=30, ge=1, le=200)


class ProcurementRunResponse(BaseModel):
    id: int
    status: str
    draft_purchase_ids: list[int]
    warnings: list[str]
    error_message: str | None = None


class ProcurementRunDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    summary_json: dict | None
    error_message: str | None
    draft_purchase_ids: list[int]
