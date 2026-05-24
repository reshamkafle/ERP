from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    InspectionStage,
    MaterialIssueMethod,
    MrpRunStatus,
    NonConformanceDisposition,
    OrderPriority,
    PlannedOrderType,
    ProductionOrderSource,
    ProductionOrderStatus,
    ProductionPhase,
    VarianceType,
)


# --- Work centers ---


class WorkCenterBase(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    capacity_hrs_per_shift: Decimal = Field(default=Decimal("8"))
    efficiency_pct: Decimal = Field(default=Decimal("100"))
    labor_rate_per_hr: Decimal = Field(default=Decimal("0"))
    machine_rate_per_hr: Decimal = Field(default=Decimal("0"))
    overhead_rate_per_hr: Decimal = Field(default=Decimal("0"))
    calendar_id: int | None = None
    is_active: bool = True


class WorkCenterCreate(WorkCenterBase):
    pass


class WorkCenterUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    capacity_hrs_per_shift: Decimal | None = None
    efficiency_pct: Decimal | None = None
    labor_rate_per_hr: Decimal | None = None
    machine_rate_per_hr: Decimal | None = None
    overhead_rate_per_hr: Decimal | None = None
    calendar_id: int | None = None
    is_active: bool | None = None


class WorkCenterRead(WorkCenterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


# --- Routing ---


class RoutingOperationIn(BaseModel):
    sequence: int
    operation_name: str
    work_center_id: int | None = None
    setup_time_minutes: Decimal = Decimal("0")
    run_time_minutes: Decimal = Decimal("0")
    cycle_time_minutes: Decimal = Decimal("0")
    smv_minutes: Decimal | None = None
    requires_labor: bool = True
    requires_machine: bool = True
    is_subcontract: bool = False
    supplier_id: int | None = None
    notes: str | None = None


class RoutingOperationRead(RoutingOperationIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    routing_id: int


class RoutingBase(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    parent_item_id: int | None = None
    is_active: bool = True


class RoutingCreate(RoutingBase):
    operations: list[RoutingOperationIn] = Field(default_factory=list)


class RoutingUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    parent_item_id: int | None = None
    is_active: bool | None = None
    operations: list[RoutingOperationIn] | None = None


class RoutingRead(RoutingBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    operations: list[RoutingOperationRead] = Field(default_factory=list)


# --- Production version ---


class ProductionVersionBase(BaseModel):
    product_id: int
    bom_parent_item_id: int
    routing_id: int
    version_code: str = Field(min_length=1, max_length=32)
    description: str | None = None
    effective_start_date: date | None = None
    effective_end_date: date | None = None
    is_default: bool = False
    is_active: bool = True


class ProductionVersionCreate(ProductionVersionBase):
    pass


class ProductionVersionRead(ProductionVersionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# --- Production order ---


class ProductionOrderBase(BaseModel):
    product_id: int
    quantity_planned: Decimal = Field(gt=0)
    priority: OrderPriority = OrderPriority.MEDIUM
    start_date: date | None = None
    end_date: date | None = None
    bom_parent_item_id: int | None = None
    routing_id: int | None = None
    production_version_id: int | None = None
    sales_order_id: int | None = None
    warehouse_id: int | None = None
    wip_warehouse_id: int | None = None
    creation_source: ProductionOrderSource = ProductionOrderSource.MANUAL
    production_plan_id: int | None = None
    contract_id: int | None = None
    production_phase: ProductionPhase | None = None
    notes: str | None = None


class ProductionOrderCreate(ProductionOrderBase):
    order_number: str | None = None


class ProductionOrderUpdate(BaseModel):
    quantity_planned: Decimal | None = None
    priority: OrderPriority | None = None
    start_date: date | None = None
    end_date: date | None = None
    bom_parent_item_id: int | None = None
    routing_id: int | None = None
    production_version_id: int | None = None
    warehouse_id: int | None = None
    wip_warehouse_id: int | None = None
    notes: str | None = None


class ProductionOrderOperationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sequence: int
    operation_name: str
    work_center_id: int | None
    status: str
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    actual_start: datetime | None
    actual_end: datetime | None
    setup_time_minutes: Decimal
    run_time_minutes: Decimal


class ProductionOrderRead(ProductionOrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: str
    status: ProductionOrderStatus
    quantity_completed: Decimal
    quantity_scrapped: Decimal
    quantity_rework: Decimal
    created_at: datetime
    updated_at: datetime
    operations: list[ProductionOrderOperationRead] = Field(default_factory=list)
    product_name: str | None = None
    product_sku: str | None = None


class ProductionOrderListResponse(BaseModel):
    items: list[ProductionOrderRead]
    total: int


# --- Execution actions ---


class MaterialIssueIn(BaseModel):
    component_item_id: int
    quantity: Decimal = Field(gt=0)
    issue_method: MaterialIssueMethod = MaterialIssueMethod.MANUAL
    lot_number: str | None = None
    serial_number: str | None = None
    material_roll_id: int | None = None
    warehouse_id: int | None = None


class ProductionConfirmationIn(BaseModel):
    operation_id: int | None = None
    quantity_completed: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_rejected: Decimal = Field(default=Decimal("0"), ge=0)
    quantity_rework: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None
    backflush: bool = False


class ShopFloorEntryIn(BaseModel):
    operation_id: int | None = None
    actual_time_minutes: Decimal = Decimal("0")
    output_quantity: Decimal = Decimal("0")
    scrap_quantity: Decimal = Decimal("0")
    downtime_minutes: Decimal = Decimal("0")
    downtime_reason: str | None = None


# --- MRP ---


class MrpRunCreate(BaseModel):
    horizon_days: int = Field(default=90, ge=1, le=365)
    parameters: dict[str, Any] | None = None
    include_sales: bool = True
    include_forecasts: bool = True


class MrpPlannedOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_type: PlannedOrderType
    product_id: int | None
    manufacturing_item_id: int | None
    quantity: Decimal
    planned_start_date: date
    planned_end_date: date | None
    is_firmed: bool
    production_order_id: int | None


class MrpRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    run_number: str
    status: MrpRunStatus
    horizon_days: int
    parameters: dict[str, Any] | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    planned_orders: list[MrpPlannedOrderRead] = Field(default_factory=list)


class MrpForecastCreate(BaseModel):
    product_id: int
    forecast_date: date
    quantity: Decimal = Field(gt=0)
    notes: str | None = None


class MrpForecastRead(MrpForecastCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class CapacityLoadItem(BaseModel):
    work_center_id: int
    work_center_code: str
    required_hours: Decimal
    available_hours: Decimal
    utilization_pct: Decimal


# --- Quality ---


class InspectionCharacteristicIn(BaseModel):
    name: str
    attribute_type: str = "NUMERIC"
    min_value: Decimal | None = None
    max_value: Decimal | None = None
    target_value: Decimal | None = None
    acceptance_criteria: str | None = None


class QualityPlanCreate(BaseModel):
    code: str
    name: str
    stage: InspectionStage
    product_id: int | None = None
    production_order_id: int | None = None
    characteristics: list[InspectionCharacteristicIn] = Field(default_factory=list)


class QualityPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    stage: InspectionStage
    product_id: int | None
    production_order_id: int | None
    is_active: bool


class InspectionResultIn(BaseModel):
    plan_id: int
    characteristic_id: int
    production_order_id: int | None = None
    measured_value: Decimal | None = None
    attribute_result: str | None = None


class NonConformanceCreate(BaseModel):
    production_order_id: int | None = None
    inspection_result_id: int | None = None
    defect_code: str
    quantity: Decimal = Field(gt=0)
    disposition: NonConformanceDisposition
    description: str | None = None


# --- Costing & reports ---


class StandardCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    effective_date: date
    material_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    total_cost: Decimal


class ProductionReportMetrics(BaseModel):
    oee_pct: Decimal
    yield_pct: Decimal
    avg_cycle_time_minutes: Decimal
    total_downtime_minutes: Decimal
    orders_completed: int


class TraceabilityLine(BaseModel):
    lot_number: str | None
    serial_number: str | None
    component_sku: str
    production_order_number: str
    quantity: Decimal


# --- BOM alternates ---


class BOMAlternateIn(BaseModel):
    alternate_parent_item_id: int
    alternate_group: str = "DEFAULT"
    priority: int = 1
    notes: str | None = None


class BOMSubstituteIn(BaseModel):
    substitute_item_id: int
    substitute_quantity: Decimal
    priority: int = 1
    notes: str | None = None


# --- Advanced ---


class EngineeringChangeCreate(BaseModel):
    eco_number: str
    title: str
    bom_parent_item_id: int | None = None
    routing_id: int | None = None
    effective_date: date | None = None
    description: str | None = None


class ToolingAssetCreate(BaseModel):
    code: str
    name: str
    product_id: int | None = None
    routing_operation_id: int | None = None
    notes: str | None = None


class BomConfigurationCreate(BaseModel):
    code: str
    name: str
    parent_item_id: int
    sales_order_id: int | None = None
    parameters: dict[str, Any] | None = None
