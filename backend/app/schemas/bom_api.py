from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.manufacturing.bom.enums import (
    BOMStatus,
    BOMType,
    ConsumptionType,
    ItemCategory,
    UnitOfMeasure,
)
from app.manufacturing.bom.models import (
    BOMTree,
    ExplosionResult,
    FabricSummary,
    Item,
    TrimSummary,
    ValidationResult,
)
from app.manufacturing.bom.product_snapshot import ProductSnapshot
from app.manufacturing.bom.schemas import BOMHeaderInput, BOMItemInput, SaveBOMRequest, UpdateBOMStatusRequest


class ItemRead(BaseModel):
    id: int
    sku: str
    name: str
    category: ItemCategory
    unit: UnitOfMeasure
    cost_per_unit: Decimal

    @classmethod
    def from_item(cls, item: Item) -> ItemRead:
        return cls(
            id=item.id,
            sku=item.sku,
            name=item.name,
            category=item.category,
            unit=item.unit,
            cost_per_unit=item.cost_per_unit,
        )


class ItemListResponse(BaseModel):
    items: list[ItemRead]


class BOMSubstituteRead(BaseModel):
    id: int
    substitute_item_id: int
    substitute_sku: str
    substitute_name: str
    substitute_quantity: Decimal
    priority: int
    notes: str | None = None


class BOMAlternateRead(BaseModel):
    id: int
    alternate_parent_item_id: int
    alternate_parent_sku: str
    alternate_parent_name: str
    alternate_group: str
    priority: int
    notes: str | None = None


class BOMAlternateCreate(BaseModel):
    alternate_parent_sku: str
    alternate_group: str = "DEFAULT"
    priority: int = 1
    notes: str | None = None


class BOMSubstituteCreate(BaseModel):
    substitute_sku: str
    substitute_quantity: Decimal
    priority: int = 1
    notes: str | None = None


class BOMLineRead(BaseModel):
    line_id: int | None = None
    line_sequence: int
    component_sku: str
    component_name: str
    component_category: ItemCategory
    quantity_per_unit: Decimal
    consumption_type: ConsumptionType
    wastage_percentage: Decimal
    yield_percentage: Decimal = Decimal("0")
    is_phantom: bool = False
    lead_time_offset_days: int | None = None
    notes: str | None = None
    product_snapshot: ProductSnapshot | None = None
    substitutes: list[BOMSubstituteRead] = Field(default_factory=list)


class BOMSummaryRead(BaseModel):
    parent_sku: str
    parent_name: str
    bom_number: str
    version: int
    status: BOMStatus
    bom_type: BOMType
    line_count: int
    effective_start_date: date | None = None
    updated_at: datetime | None = None


class BOMListResponse(BaseModel):
    boms: list[BOMSummaryRead]


class BOMRead(BaseModel):
    parent_item_id: int | None = None
    parent_sku: str
    parent_name: str
    parent_description: str | None = None
    bom_number: str
    version: int
    status: BOMStatus
    bom_type: BOMType
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    eco_number: str | None = None
    approved_at: datetime | None = None
    approved_by_id: int | None = None
    created_by_id: int | None = None
    created_at: datetime | None = None
    updated_by_id: int | None = None
    updated_at: datetime | None = None
    parent_product_snapshot: ProductSnapshot | None = None
    lines: list[BOMLineRead] = Field(default_factory=list)
    alternates: list[BOMAlternateRead] = Field(default_factory=list)


class AddBOMResponse(BaseModel):
    bom: BOMRead
    validation: ValidationResult


# Re-export request/response models for OpenAPI
BOMTreeResponse = BOMTree
ExplosionResponse = ExplosionResult
FabricSummaryResponse = FabricSummary
TrimSummaryResponse = TrimSummary

__all__ = [
    "AddBOMResponse",
    "BOMHeaderInput",
    "BOMItemInput",
    "BOMAlternateCreate",
    "BOMAlternateRead",
    "BOMSubstituteCreate",
    "BOMSubstituteRead",
    "BOMLineRead",
    "BOMListResponse",
    "BOMRead",
    "BOMSummaryRead",
    "BOMTreeResponse",
    "ExplosionResponse",
    "FabricSummaryResponse",
    "ItemListResponse",
    "ItemRead",
    "ProductSnapshot",
    "SaveBOMRequest",
    "TrimSummaryResponse",
    "UpdateBOMStatusRequest",
]
