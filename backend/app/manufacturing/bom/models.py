from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.manufacturing.bom.enums import (
    BOMStatus,
    BOMType,
    ConsumptionType,
    ItemCategory,
    UnitOfMeasure,
)


class Item(BaseModel):
    """Manufacturing item master (fabric, trim, sub-assembly, finished good)."""

    model_config = ConfigDict(frozen=True)

    id: int
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    category: ItemCategory
    unit: UnitOfMeasure
    cost_per_unit: Decimal = Field(default=Decimal("0"), ge=0)
    secondary_uom: UnitOfMeasure | None = None
    conversion_factor: Decimal | None = Field(default=None, gt=0)

    @field_validator("conversion_factor")
    @classmethod
    def conversion_requires_secondary(
        cls,
        v: Decimal | None,
        info,
    ) -> Decimal | None:
        secondary = info.data.get("secondary_uom")
        if secondary and (v is None or v <= 0):
            raise ValueError("conversion_factor is required when secondary_uom is set")
        if v is not None and not secondary:
            raise ValueError("secondary_uom is required when conversion_factor is set")
        return v


class BOMItem(BaseModel):
    """One line in a bill of materials."""

    model_config = ConfigDict(frozen=True)

    parent_item_id: int
    component_item_id: int
    line_sequence: int = Field(ge=1)
    quantity_per_unit: Decimal = Field(gt=0)
    consumption_type: ConsumptionType = ConsumptionType.OTHER
    wastage_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    yield_percentage: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    is_phantom: bool = False
    lead_time_offset_days: int | None = None
    notes: str | None = None


class BOM(BaseModel):
    """Bill of materials for a parent item."""

    parent_item_id: int
    parent_sku: str
    lines: list[BOMItem] = Field(default_factory=list)
    bom_number: str = ""
    version: int = 1
    status: BOMStatus = BOMStatus.DRAFT
    bom_type: BOMType = BOMType.MANUFACTURING
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    eco_number: str | None = None
    approved_at: datetime | None = None
    approved_by_id: int | None = None
    created_by_id: int | None = None
    created_at: datetime | None = None
    updated_by_id: int | None = None
    updated_at: datetime | None = None


class BOMTreeNode(BaseModel):
    """Recursive BOM tree node for engineering view."""

    item: Item
    line_sequence: int = 1
    quantity_per_unit: Decimal = Field(default=Decimal("1"), gt=0)
    consumption_type: ConsumptionType = ConsumptionType.OTHER
    wastage_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    yield_percentage: Decimal = Field(default=Decimal("0"), ge=0)
    is_phantom: bool = False
    lead_time_offset_days: int | None = None
    notes: str | None = None
    children: list[BOMTreeNode] = Field(default_factory=list)
    rolled_up_cost: Decimal | None = None


class BOMTree(BaseModel):
    """Full multi-level BOM tree rooted at a parent SKU."""

    root: BOMTreeNode
    parent_sku: str


class ExplosionLine(BaseModel):
    """Flattened material requirement for one raw component."""

    model_config = ConfigDict(frozen=True)

    item_id: int
    sku: str
    name: str
    category: ItemCategory
    consumption_type: ConsumptionType
    unit: UnitOfMeasure
    gross_qty: Decimal = Field(ge=0)
    wastage_qty: Decimal = Field(ge=0)
    total_qty: Decimal = Field(ge=0)
    cost_per_unit: Decimal = Field(ge=0)
    extended_cost: Decimal = Field(ge=0)


class ExplosionResult(BaseModel):
    """Complete flattened explosion for an order quantity."""

    parent_sku: str
    parent_item_id: int
    order_quantity: int = Field(ge=1)
    lines: list[ExplosionLine] = Field(default_factory=list)
    total_material_cost: Decimal = Field(default=Decimal("0"), ge=0)


class FabricLine(BaseModel):
    """Fabric-specific consumption line."""

    sku: str
    name: str
    unit: UnitOfMeasure
    gross_qty: Decimal
    wastage_qty: Decimal
    total_qty: Decimal
    wastage_percentage: Decimal
    extended_cost: Decimal


class FabricSummary(BaseModel):
    parent_sku: str
    order_quantity: int
    fabrics: list[FabricLine] = Field(default_factory=list)
    total_meters: Decimal = Field(default=Decimal("0"))
    total_fabric_cost: Decimal = Field(default=Decimal("0"))


class TrimLine(BaseModel):
    sku: str
    name: str
    unit: UnitOfMeasure
    gross_qty: Decimal
    wastage_qty: Decimal
    total_qty: Decimal
    extended_cost: Decimal


class TrimSummary(BaseModel):
    parent_sku: str
    order_quantity: int
    trims: list[TrimLine] = Field(default_factory=list)
    total_trim_cost: Decimal = Field(default=Decimal("0"))


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
