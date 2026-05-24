"""Schemas for garment production planning."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    CutOrderStatus,
    ProductionContractType,
    ProductionPlanStatus,
)


# --- Contracts (CMT / FOB) ---


class CmtMaterialSupplyIn(BaseModel):
    manufacturing_item_id: int
    description: str | None = None
    quantity_received: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_consumed: Decimal = Field(default=Decimal("0"), ge=0)
    uom: str | None = None
    lot_reference: str | None = None


class CmtMaterialSupplyRead(CmtMaterialSupplyIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_id: int


class ProductionContractBase(BaseModel):
    contract_type: ProductionContractType
    customer_id: int | None = None
    sales_order_id: int | None = None
    buyer_name: str | None = None
    notes: str | None = None
    is_active: bool = True


class ProductionContractCreate(ProductionContractBase):
    contract_number: str | None = None
    material_supplies: list[CmtMaterialSupplyIn] = Field(default_factory=list)


class ProductionContractUpdate(BaseModel):
    buyer_name: str | None = None
    notes: str | None = None
    is_active: bool | None = None
    material_supplies: list[CmtMaterialSupplyIn] | None = None


class ProductionContractRead(ProductionContractBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contract_number: str
    created_at: datetime
    updated_at: datetime
    material_supplies: list[CmtMaterialSupplyRead] = Field(default_factory=list)


# --- Sewing lines ---


class SewingLineBase(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    operators_count: int = Field(default=1, ge=1)
    minutes_per_shift: Decimal = Field(default=Decimal("480"))
    efficiency_pct: Decimal = Field(default=Decimal("100"))
    calendar_id: int | None = None
    is_active: bool = True


class SewingLineCreate(SewingLineBase):
    pass


class SewingLineRead(SewingLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# --- Production plan ---


class ProductionPlanLineIn(BaseModel):
    product_id: int
    color_value_id: int | None = None
    size_value_id: int | None = None
    quantity_planned: Decimal = Field(gt=0)
    due_date: date | None = None
    priority: int = 5


class ProductionPlanLineRead(ProductionPlanLineIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    production_plan_id: int
    quantity_cut: Decimal
    quantity_sewn: Decimal
    quantity_packed: Decimal
    product_sku: str | None = None
    product_name: str | None = None
    color_label: str | None = None
    size_label: str | None = None


class ProductionPlanScheduleIn(BaseModel):
    sewing_line_id: int | None = None
    schedule_date: date
    shift_code: str | None = None
    planned_output: Decimal = Field(default=Decimal("0"), ge=0)


class ProductionPlanScheduleRead(ProductionPlanScheduleIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    production_plan_id: int
    sewing_line_code: str | None = None


class ProductionPlanBase(BaseModel):
    sales_order_id: int | None = None
    style_template_id: int | None = None
    contract_id: int | None = None
    bom_parent_item_id: int | None = None
    routing_id: int | None = None
    target_ship_date: date | None = None
    planning_horizon_days: int = 90
    notes: str | None = None


class ProductionPlanCreate(ProductionPlanBase):
    plan_number: str | None = None
    lines: list[ProductionPlanLineIn] = Field(default_factory=list)


class ProductionPlanUpdate(BaseModel):
    status: ProductionPlanStatus | None = None
    target_ship_date: date | None = None
    notes: str | None = None
    routing_id: int | None = None
    bom_parent_item_id: int | None = None


class ProductionPlanRead(ProductionPlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan_number: str
    status: ProductionPlanStatus
    created_at: datetime
    updated_at: datetime
    lines: list[ProductionPlanLineRead] = Field(default_factory=list)
    schedules: list[ProductionPlanScheduleRead] = Field(default_factory=list)
    contract_type: ProductionContractType | None = None
    contract_number: str | None = None


class ProductionPlanListResponse(BaseModel):
    items: list[ProductionPlanRead]
    total: int


class ProductionPlanFromSalesIn(BaseModel):
    sales_order_id: int
    contract_id: int | None = None
    bom_parent_item_id: int | None = None
    routing_id: int | None = None
    target_ship_date: date | None = None


# --- Cut orders ---


class CutOrderSizeBreakdownIn(BaseModel):
    production_plan_line_id: int | None = None
    color_label: str | None = None
    size_label: str | None = None
    pieces_to_cut: Decimal = Field(gt=0)
    wastage_pct: Decimal | None = None


class CutOrderSizeBreakdownRead(CutOrderSizeBreakdownIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cut_order_id: int
    pieces_cut: Decimal


class CutOrderFabricAllocationIn(BaseModel):
    roll_lot_ref: str | None = None
    material_roll_id: int | None = None
    meters_allocated: Decimal = Field(default=Decimal("0"), ge=0)


class CutOrderFabricAllocationRead(CutOrderFabricAllocationIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cut_order_id: int


class CutOrderBase(BaseModel):
    production_plan_id: int
    fabric_item_id: int | None = None
    cutting_date: date | None = None
    priority: int = 5
    marker_ref: str | None = None
    marker_length: Decimal | None = None
    marker_width: Decimal | None = None
    efficiency_pct: Decimal | None = None
    plies: int | None = None
    notes: str | None = None


class CutOrderCreate(CutOrderBase):
    cut_order_number: str | None = None
    size_breakdowns: list[CutOrderSizeBreakdownIn] = Field(default_factory=list)
    fabric_allocations: list[CutOrderFabricAllocationIn] = Field(default_factory=list)


class CutOrderUpdate(BaseModel):
    status: CutOrderStatus | None = None
    cutting_date: date | None = None
    marker_ref: str | None = None
    marker_length: Decimal | None = None
    marker_width: Decimal | None = None
    efficiency_pct: Decimal | None = None
    plies: int | None = None
    notes: str | None = None


class CutOrderRead(CutOrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cut_order_number: str
    status: CutOrderStatus
    created_at: datetime
    updated_at: datetime
    size_breakdowns: list[CutOrderSizeBreakdownRead] = Field(default_factory=list)
    fabric_allocations: list[CutOrderFabricAllocationRead] = Field(default_factory=list)
    fabric_item_sku: str | None = None


class CutOrderCompleteIn(BaseModel):
    size_breakdowns: list[CutOrderSizeBreakdownIn] | None = None


# --- Line balancing ---


class LineBalanceOperationIn(BaseModel):
    routing_operation_id: int | None = None
    operation_definition_id: int | None = None
    operation_name: str
    smv_minutes: Decimal = Field(gt=0)


class LineBalanceCalculateIn(BaseModel):
    operations: list[LineBalanceOperationIn]
    operators_count: int = Field(ge=1)
    target_quantity: Decimal = Field(gt=0)
    available_minutes: Decimal = Field(gt=0)


class LineBalanceAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    session_id: int
    routing_operation_id: int | None
    operation_definition_id: int | None
    operation_name: str
    station_no: int
    assigned_smv: Decimal
    operator_ref: str | None


class LineBalanceStationLoad(BaseModel):
    station_no: int
    total_smv: Decimal
    utilization_pct: Decimal


class LineBalanceCalculateResult(BaseModel):
    calculated_takt_minutes: Decimal
    line_efficiency_pct: Decimal
    bottleneck_station: int
    assignments: list[LineBalanceAssignmentRead]
    station_loads: list[LineBalanceStationLoad]


class LineBalanceSessionCreate(BaseModel):
    production_plan_id: int | None = None
    production_order_id: int | None = None
    sewing_line_id: int | None = None
    target_output_per_hour: Decimal
    available_minutes: Decimal
    target_quantity: Decimal
    operators_count: int = Field(ge=1)
    operations: list[LineBalanceOperationIn]


class LineBalanceSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    production_plan_id: int | None
    production_order_id: int | None
    sewing_line_id: int | None
    target_output_per_hour: Decimal
    available_minutes: Decimal
    target_quantity: Decimal
    operators_count: int
    calculated_takt_minutes: Decimal | None
    line_efficiency_pct: Decimal | None
    bottleneck_station: int | None
    created_at: datetime
    assignments: list[LineBalanceAssignmentRead] = Field(default_factory=list)
    station_loads: list[LineBalanceStationLoad] = Field(default_factory=list)


class LineBalanceAssignmentPatch(BaseModel):
    station_no: int
    operator_ref: str | None = None
