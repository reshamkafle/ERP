"""Pydantic schemas for fabric roll / lot tracking."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.enums import (
    MaterialFinishType,
    MaterialRollAllocationStatus,
    MaterialRollMovementType,
    MaterialRollStatus,
    StockQualityStatus,
)


class MaterialRollInspectionIn(BaseModel):
    inspector_name: str | None = None
    passed: bool = True
    test_parameters: dict[str, Any] | None = None
    notes: str | None = None


class MaterialRollInspectionRead(BaseModel):
    id: int
    material_roll_id: int
    inspector_name: str | None
    inspected_by_id: int | None
    inspected_at: datetime
    passed: bool
    test_parameters: dict[str, Any] | None
    notes: str | None

    model_config = {"from_attributes": True}


class MaterialRollMovementRead(BaseModel):
    id: int
    material_roll_id: int
    movement_type: MaterialRollMovementType
    quantity_delta: Decimal
    uom: str
    from_warehouse_id: int | None
    to_warehouse_id: int | None
    from_location_id: int | None
    to_location_id: int | None
    reference_type: str | None
    reference_id: int | None
    reference_document: str | None
    user_id: int | None
    remarks: str | None
    transaction_at: datetime

    model_config = {"from_attributes": True}


class MaterialRollAllocationRead(BaseModel):
    id: int
    material_roll_id: int
    reference_type: str
    reference_id: int
    allocated_quantity: Decimal
    consumed_quantity: Decimal
    status: MaterialRollAllocationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class MaterialRollBase(BaseModel):
    product_id: int
    barcode: str | None = Field(default=None, max_length=64)
    rfid_tag: str | None = Field(default=None, max_length=128)
    serial_number: str | None = Field(default=None, max_length=128)
    material_type: str | None = Field(default=None, max_length=120)
    composition: str | None = None
    color: str | None = Field(default=None, max_length=64)
    dye_lot: str | None = Field(default=None, max_length=64)
    pattern: str | None = Field(default=None, max_length=120)
    gsm: Decimal | None = Field(default=None, ge=0)
    width: Decimal | None = Field(default=None, ge=0)
    thickness: Decimal | None = Field(default=None, ge=0)
    grade: str | None = Field(default=None, max_length=32)
    finish_type: MaterialFinishType | None = None
    primary_uom: str = Field(default="meter", max_length=32)
    secondary_uom: str | None = Field(default=None, max_length=32)
    conversion_factor: Decimal | None = Field(default=None, ge=0)
    supplier_id: int | None = None
    supplier_lot_number: str | None = Field(default=None, max_length=64)
    po_number: str | None = Field(default=None, max_length=64)
    grn_reference: str | None = Field(default=None, max_length=64)
    invoice_number: str | None = Field(default=None, max_length=64)
    receipt_date: date | None = None
    unit_cost: Decimal | None = Field(default=None, ge=0)
    currency_code: str = Field(default="USD", max_length=3)
    manufacture_date: date | None = None
    expiry_date: date | None = None
    warehouse_id: int | None = None
    location_id: int | None = None
    quality_status: StockQualityStatus = StockQualityStatus.APPROVED
    inspection_passed: bool | None = None
    inspection_notes: str | None = None
    certifications: list[dict[str, Any]] | None = None
    defect_log: list[dict[str, Any]] | None = None
    shrinkage_test_data: dict[str, Any] | None = None
    custom_attributes: dict[str, Any] | None = None
    attachments: list[dict[str, Any]] | None = None


class MaterialRollCreate(MaterialRollBase):
    initial_quantity: Decimal = Field(gt=0)
    initial_weight_kg: Decimal | None = Field(default=None, ge=0)
    roll_number: str | None = Field(default=None, max_length=64)


class MaterialRollUpdate(BaseModel):
    barcode: str | None = Field(default=None, max_length=64)
    rfid_tag: str | None = Field(default=None, max_length=128)
    color: str | None = None
    dye_lot: str | None = None
    status: MaterialRollStatus | None = None
    warehouse_id: int | None = None
    location_id: int | None = None
    quality_status: StockQualityStatus | None = None
    inspection_passed: bool | None = None
    inspection_notes: str | None = None
    certifications: list[dict[str, Any]] | None = None
    defect_log: list[dict[str, Any]] | None = None
    shrinkage_test_data: dict[str, Any] | None = None
    custom_attributes: dict[str, Any] | None = None
    attachments: list[dict[str, Any]] | None = None
    reserved_for_type: str | None = None
    reserved_for_id: int | None = None


class MaterialRollRead(MaterialRollBase):
    id: int
    roll_number: str
    initial_quantity: Decimal
    remaining_quantity: Decimal
    initial_weight_kg: Decimal | None
    remaining_weight_kg: Decimal | None
    total_cost: Decimal | None
    status: MaterialRollStatus
    purchase_id: int | None
    purchase_item_id: int | None
    reserved_for_type: str | None
    reserved_for_id: int | None
    reserved_until: datetime | None
    last_scanned_at: datetime | None
    last_scanned_by_id: int | None
    created_at: datetime
    updated_at: datetime
    product_sku: str | None = None
    product_name: str | None = None

    model_config = {"from_attributes": True}


class MaterialRollDetailRead(MaterialRollRead):
    movements: list[MaterialRollMovementRead] = Field(default_factory=list)
    inspections: list[MaterialRollInspectionRead] = Field(default_factory=list)
    allocations: list[MaterialRollAllocationRead] = Field(default_factory=list)


class MaterialRollListResponse(BaseModel):
    items: list[MaterialRollRead]
    total: int


class MaterialRollReceiveIn(MaterialRollBase):
    initial_quantity: Decimal = Field(gt=0)
    initial_weight_kg: Decimal | None = Field(default=None, ge=0)
    roll_number: str | None = None
    purchase_id: int | None = None
    purchase_item_id: int | None = None


class MaterialRollBulkReceiveLine(BaseModel):
    product_id: int
    quantity_per_roll: Decimal = Field(gt=0)
    roll_count: int = Field(ge=1, le=500)
    primary_uom: str = "meter"
    dye_lot: str | None = None
    color: str | None = None
    supplier_lot_number: str | None = None
    warehouse_id: int | None = None
    location_id: int | None = None
    unit_cost: Decimal | None = None


class MaterialRollBulkReceiveIn(BaseModel):
    lines: list[MaterialRollBulkReceiveLine] = Field(min_length=1)
    purchase_id: int | None = None
    supplier_id: int | None = None
    grn_reference: str | None = None
    receipt_date: date | None = None


class MaterialRollTransferIn(BaseModel):
    to_warehouse_id: int
    to_location_id: int | None = None
    remarks: str | None = None


class MaterialRollIssueIn(BaseModel):
    quantity: Decimal = Field(gt=0)
    reference_type: str | None = None
    reference_id: int | None = None
    reference_document: str | None = None
    remarks: str | None = None


class MaterialRollReturnIn(BaseModel):
    quantity: Decimal = Field(gt=0)
    remarks: str | None = None


class MaterialRollQuarantineIn(BaseModel):
    quality_status: StockQualityStatus = StockQualityStatus.QUARANTINE
    status: MaterialRollStatus = MaterialRollStatus.QUARANTINED
    remarks: str | None = None


class MaterialRollScanIn(BaseModel):
    barcode: str | None = None
    rfid_tag: str | None = None
    roll_number: str | None = None

    @model_validator(mode="after")
    def at_least_one_identifier(self) -> MaterialRollScanIn:
        if not any([self.barcode, self.rfid_tag, self.roll_number]):
            raise ValueError("Provide barcode, rfid_tag, or roll_number")
        return self


class MaterialRollScanRead(BaseModel):
    roll: MaterialRollRead
    product_sku: str
    product_name: str


class TraceabilityNode(BaseModel):
    node_type: str
    reference_id: int | None
    label: str
    detail: str | None = None


class MaterialRollTraceabilityRead(BaseModel):
    roll_id: int
    roll_number: str
    backward: list[TraceabilityNode]
    forward: list[TraceabilityNode]


class MaterialRollLabelRead(BaseModel):
    roll_number: str
    barcode: str
    product_sku: str
    product_name: str
    color: str | None
    dye_lot: str | None
    remaining_quantity: Decimal
    primary_uom: str
    html: str


class PurchaseReceiveRollsIn(BaseModel):
    purchase_id: int
    lines: list[MaterialRollBulkReceiveLine] = Field(min_length=1)
    grn_reference: str | None = None
    skip_stock_rollup: bool = False
