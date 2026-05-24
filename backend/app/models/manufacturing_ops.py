"""Manufacturing operations: routings, work centers, production orders, MRP, quality."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    EngineeringChangeStatus,
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

_enum_values = lambda enum_cls: [member.value for member in enum_cls]


class WorkCenter(Base):
    __tablename__ = "work_centers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    capacity_hrs_per_shift: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=8)
    efficiency_pct: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=100)
    labor_rate_per_hr: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    machine_rate_per_hr: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    overhead_rate_per_hr: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    calendar_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_calendars.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    calendar: Mapped[ProductionCalendar | None] = relationship(back_populates="work_centers")
    maintenance_records: Mapped[list[WorkCenterMaintenance]] = relationship(back_populates="work_center")
    routing_operations: Mapped[list[RoutingOperation]] = relationship(back_populates="work_center")


class WorkCenterMaintenance(Base):
    __tablename__ = "work_center_maintenance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_center_id: Mapped[int] = mapped_column(
        ForeignKey("work_centers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    work_center: Mapped[WorkCenter] = relationship(back_populates="maintenance_records")


class ProductionCalendar(Base):
    __tablename__ = "production_calendars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    working_days: Mapped[str] = mapped_column(String(32), nullable=False, default="1111100")
    hours_per_day: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=8)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    work_centers: Mapped[list[WorkCenter]] = relationship(back_populates="calendar")
    shifts: Mapped[list[ShiftDefinition]] = relationship(back_populates="calendar")


class ShiftDefinition(Base):
    __tablename__ = "shift_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("production_calendars.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    start_time: Mapped[str] = mapped_column(String(8), nullable=False)
    end_time: Mapped[str] = mapped_column(String(8), nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    calendar: Mapped[ProductionCalendar] = relationship(back_populates="shifts")


class Routing(Base):
    __tablename__ = "routings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    parent_item: Mapped["ManufacturingItem | None"] = relationship(foreign_keys=[parent_item_id])
    operations: Mapped[list[RoutingOperation]] = relationship(
        back_populates="routing", order_by="RoutingOperation.sequence"
    )
    production_versions: Mapped[list[ProductionVersion]] = relationship(back_populates="routing")


class RoutingOperation(Base):
    __tablename__ = "routing_operations"
    __table_args__ = (UniqueConstraint("routing_id", "sequence", name="uq_routing_op_sequence"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    routing_id: Mapped[int] = mapped_column(
        ForeignKey("routings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    work_center_id: Mapped[int | None] = mapped_column(
        ForeignKey("work_centers.id", ondelete="SET NULL"), nullable=True
    )
    setup_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    run_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    cycle_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    smv_minutes: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    requires_labor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_machine: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_subcontract: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    routing: Mapped[Routing] = relationship(back_populates="operations")
    work_center: Mapped[WorkCenter | None] = relationship(back_populates="routing_operations")


class ProductionVersion(Base):
    __tablename__ = "production_versions"
    __table_args__ = (
        UniqueConstraint("product_id", "version_code", name="uq_prod_version_product_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bom_parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"), nullable=False
    )
    routing_id: Mapped[int] = mapped_column(
        ForeignKey("routings.id", ondelete="RESTRICT"), nullable=False
    )
    version_code: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    product: Mapped["Product"] = relationship()
    bom_parent_item: Mapped["ManufacturingItem"] = relationship(foreign_keys=[bom_parent_item_id])
    routing: Mapped[Routing] = relationship(back_populates="production_versions")


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    status: Mapped[ProductionOrderStatus] = mapped_column(
        Enum(ProductionOrderStatus, name="productionorderstatus", values_callable=_enum_values),
        nullable=False,
        default=ProductionOrderStatus.PLANNED,
    )
    priority: Mapped[OrderPriority] = mapped_column(
        Enum(OrderPriority, name="orderpriority", create_constraint=False),
        nullable=False,
        default=OrderPriority.MEDIUM,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity_planned: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    quantity_completed: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_scrapped: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_rework: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    bom_parent_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    routing_id: Mapped[int | None] = mapped_column(
        ForeignKey("routings.id", ondelete="SET NULL"), nullable=True
    )
    production_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_versions.id", ondelete="SET NULL"), nullable=True
    )
    sales_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="SET NULL"), nullable=True
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True
    )
    wip_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True
    )
    creation_source: Mapped[ProductionOrderSource] = mapped_column(
        Enum(ProductionOrderSource, name="productionordersource", values_callable=_enum_values),
        nullable=False,
        default=ProductionOrderSource.MANUAL,
    )
    production_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_plans.id", ondelete="SET NULL"), nullable=True, index=True
    )
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_contracts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    production_phase: Mapped[ProductionPhase | None] = mapped_column(
        Enum(ProductionPhase, name="productionphase", values_callable=_enum_values),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship()
    bom_parent_item: Mapped["ManufacturingItem | None"] = relationship(foreign_keys=[bom_parent_item_id])
    routing: Mapped["Routing | None"] = relationship()
    production_version: Mapped["ProductionVersion | None"] = relationship()
    sale: Mapped["Sale | None"] = relationship()
    operations: Mapped[list[ProductionOrderOperation]] = relationship(
        back_populates="production_order", order_by="ProductionOrderOperation.sequence"
    )
    material_issues: Mapped[list[ProductionMaterialIssue]] = relationship(back_populates="production_order")
    confirmations: Mapped[list[ProductionConfirmation]] = relationship(back_populates="production_order")
    shop_floor_entries: Mapped[list[ShopFloorEntry]] = relationship(back_populates="production_order")
    costs: Mapped[list[ProductionOrderCost]] = relationship(back_populates="production_order")
    variances: Mapped[list[ProductionVariance]] = relationship(back_populates="production_order")


class ProductionOrderOperation(Base):
    __tablename__ = "production_order_operations"
    __table_args__ = (
        UniqueConstraint("production_order_id", "sequence", name="uq_po_op_sequence"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    routing_operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("routing_operations.id", ondelete="SET NULL"), nullable=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    work_center_id: Mapped[int | None] = mapped_column(
        ForeignKey("work_centers.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    setup_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    run_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    production_order: Mapped[ProductionOrder] = relationship(back_populates="operations")
    work_center: Mapped[WorkCenter | None] = relationship()


class ProductionMaterialIssue(Base):
    __tablename__ = "production_material_issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    component_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    issue_method: Mapped[MaterialIssueMethod] = mapped_column(
        Enum(MaterialIssueMethod, name="materialissuemethod", values_callable=_enum_values),
        nullable=False,
        default=MaterialIssueMethod.MANUAL,
    )
    lot_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    material_roll_id: Mapped[int | None] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    issued_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    production_order: Mapped[ProductionOrder] = relationship(back_populates="material_issues")
    component_item: Mapped["ManufacturingItem"] = relationship()
    material_roll: Mapped["MaterialRoll | None"] = relationship()


class ProductionConfirmation(Base):
    __tablename__ = "production_confirmations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_order_operations.id", ondelete="SET NULL"), nullable=True
    )
    quantity_completed: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_rejected: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_rework: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    confirmed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    production_order: Mapped[ProductionOrder] = relationship(back_populates="confirmations")


class ShopFloorEntry(Base):
    __tablename__ = "shop_floor_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_order_operations.id", ondelete="SET NULL"), nullable=True
    )
    actual_time_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    output_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    scrap_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    downtime_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    downtime_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    recorded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    production_order: Mapped[ProductionOrder] = relationship(back_populates="shop_floor_entries")


class MrpRun(Base):
    __tablename__ = "mrp_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    status: Mapped[MrpRunStatus] = mapped_column(
        Enum(MrpRunStatus, name="mrprunstatus", values_callable=_enum_values),
        nullable=False,
        default=MrpRunStatus.DRAFT,
    )
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    planned_orders: Mapped[list[MrpPlannedOrder]] = relationship(back_populates="mrp_run")
    demand_lines: Mapped[list[MrpDemandLine]] = relationship(back_populates="mrp_run")


class MrpDemandLine(Base):
    __tablename__ = "mrp_demand_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mrp_run_id: Mapped[int] = mapped_column(
        ForeignKey("mrp_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    manufacturing_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    demand_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)

    mrp_run: Mapped[MrpRun] = relationship(back_populates="demand_lines")


class MrpPlannedOrder(Base):
    __tablename__ = "mrp_planned_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mrp_run_id: Mapped[int] = mapped_column(
        ForeignKey("mrp_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_type: Mapped[PlannedOrderType] = mapped_column(
        Enum(PlannedOrderType, name="plannedordertype", values_callable=_enum_values),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    manufacturing_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_firmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    production_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_orders.id", ondelete="SET NULL"), nullable=True
    )
    pegged_demand_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("mrp_demand_lines.id", ondelete="SET NULL"), nullable=True
    )

    mrp_run: Mapped[MrpRun] = relationship(back_populates="planned_orders")


class MrpForecast(Base):
    __tablename__ = "mrp_forecasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MasterProductionSchedule(Base):
    __tablename__ = "master_production_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    lines: Mapped[list[MpsLine]] = relationship(back_populates="schedule")


class MpsLine(Base):
    __tablename__ = "mps_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("master_production_schedules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)

    schedule: Mapped[MasterProductionSchedule] = relationship(back_populates="lines")


class QualityInspectionPlan(Base):
    __tablename__ = "quality_inspection_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[InspectionStage] = mapped_column(
        Enum(InspectionStage, name="inspectionstage", values_callable=_enum_values),
        nullable=False,
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    production_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_orders.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    characteristics: Mapped[list[InspectionCharacteristic]] = relationship(back_populates="plan")
    results: Mapped[list[InspectionResult]] = relationship(back_populates="plan")


class InspectionCharacteristic(Base):
    __tablename__ = "inspection_characteristics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("quality_inspection_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    attribute_type: Mapped[str] = mapped_column(String(32), nullable=False, default="NUMERIC")
    min_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    max_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    acceptance_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan: Mapped[QualityInspectionPlan] = relationship(back_populates="characteristics")


class InspectionResult(Base):
    __tablename__ = "inspection_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("quality_inspection_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    production_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_orders.id", ondelete="SET NULL"), nullable=True
    )
    characteristic_id: Mapped[int] = mapped_column(
        ForeignKey("inspection_characteristics.id", ondelete="CASCADE"), nullable=False
    )
    measured_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    attribute_result: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    inspected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    inspected_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    plan: Mapped[QualityInspectionPlan] = relationship(back_populates="results")


class NonConformance(Base):
    __tablename__ = "non_conformances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    production_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_orders.id", ondelete="SET NULL"), nullable=True
    )
    inspection_result_id: Mapped[int | None] = mapped_column(
        ForeignKey("inspection_results.id", ondelete="SET NULL"), nullable=True
    )
    defect_code: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    disposition: Mapped[NonConformanceDisposition] = mapped_column(
        Enum(NonConformanceDisposition, name="nonconformancedisposition", values_callable=_enum_values),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ProductStandardCost(Base):
    __tablename__ = "product_standard_costs"
    __table_args__ = (UniqueConstraint("product_id", "effective_date", name="uq_std_cost_product_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    material_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)


class ProductionOrderCost(Base):
    __tablename__ = "production_order_costs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cost_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    production_order: Mapped[ProductionOrder] = relationship(back_populates="costs")


class ProductionVariance(Base):
    __tablename__ = "production_variances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variance_type: Mapped[VarianceType] = mapped_column(
        Enum(VarianceType, name="variancetype", values_callable=_enum_values),
        nullable=False,
    )
    standard_amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    variance_amount: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="SET NULL"), nullable=True
    )

    production_order: Mapped[ProductionOrder] = relationship(back_populates="variances")


class EngineeringChange(Base):
    __tablename__ = "engineering_changes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eco_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[EngineeringChangeStatus] = mapped_column(
        Enum(EngineeringChangeStatus, name="engineeringchangestatus", values_callable=_enum_values),
        nullable=False,
        default=EngineeringChangeStatus.DRAFT,
    )
    bom_parent_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    routing_id: Mapped[int | None] = mapped_column(
        ForeignKey("routings.id", ondelete="SET NULL"), nullable=True
    )
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ToolingAsset(Base):
    __tablename__ = "tooling_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    routing_operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("routing_operations.id", ondelete="SET NULL"), nullable=True
    )
    lifecycle_status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class BomConfiguration(Base):
    __tablename__ = "bom_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="CASCADE"), nullable=False
    )
    sales_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="SET NULL"), nullable=True
    )
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.manufacturing import ManufacturingItem
    from app.models.product import Product
    from app.models.sale import Sale
