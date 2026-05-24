from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.manufacturing.bom.enums import BOMStatus, BOMType, ConsumptionType


class BOMItemInput(BaseModel):
    """Input DTO for creating/updating a BOM line (SKU-based)."""

    component_sku: str = Field(min_length=1, max_length=64)
    line_sequence: int | None = Field(default=None, ge=1)
    quantity_per_unit: Decimal = Field(gt=0)
    consumption_type: ConsumptionType = ConsumptionType.OTHER
    wastage_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    yield_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    is_phantom: bool = False
    lead_time_offset_days: int | None = Field(default=None, ge=0)
    notes: str | None = None


class BOMHeaderInput(BaseModel):
    status: BOMStatus = BOMStatus.DRAFT
    bom_type: BOMType = BOMType.MANUFACTURING
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    eco_number: str | None = Field(default=None, max_length=64)


class SaveBOMRequest(BaseModel):
    """Save BOM header and lines; header optional for backward-compatible line-only saves."""

    header: BOMHeaderInput | None = None
    lines: list[BOMItemInput]


class UpdateBOMStatusRequest(BaseModel):
    status: BOMStatus
