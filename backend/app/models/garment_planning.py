"""Garment production planning: CMT contracts, APS plans, cut orders, line balancing."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    CutOrderStatus,
    ProductionContractType,
    ProductionPlanStatus,
)

_enum_values = lambda enum_cls: [member.value for member in enum_cls]


class ProductionContract(Base):
    __tablename__ = "production_contracts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    contract_type: Mapped[ProductionContractType] = mapped_column(
        Enum(ProductionContractType, name="productioncontracttype", values_callable=_enum_values),
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sales_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="SET NULL"), nullable=True, index=True
    )
    buyer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    material_supplies: Mapped[list[CmtMaterialSupply]] = relationship(back_populates="contract")
    production_plans: Mapped[list[ProductionPlan]] = relationship(back_populates="contract")


class CmtMaterialSupply(Base):
    __tablename__ = "cmt_material_supplies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("production_contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manufacturing_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity_received: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_consumed: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    uom: Mapped[str | None] = mapped_column(String(16), nullable=True)
    lot_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)

    contract: Mapped[ProductionContract] = relationship(back_populates="material_supplies")
    manufacturing_item: Mapped["ManufacturingItem"] = relationship()


class SewingLine(Base):
    __tablename__ = "sewing_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    operators_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    minutes_per_shift: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=480)
    efficiency_pct: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=100)
    calendar_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_calendars.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    schedules: Mapped[list[ProductionPlanSchedule]] = relationship(back_populates="sewing_line")
    balance_sessions: Mapped[list[LineBalanceSession]] = relationship(back_populates="sewing_line")


class OperationDefinition(Base):
    """Garment operation library (IE) — can link to routing operations."""

    __tablename__ = "operation_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    smv_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    machine_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    skill_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    routing_operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("routing_operations.id", ondelete="SET NULL"), nullable=True
    )
    parent_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    routing_operation: Mapped["RoutingOperation | None"] = relationship()


class ProductionPlan(Base):
    __tablename__ = "production_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    status: Mapped[ProductionPlanStatus] = mapped_column(
        Enum(ProductionPlanStatus, name="productionplanstatus", values_callable=_enum_values),
        nullable=False,
        default=ProductionPlanStatus.DRAFT,
    )
    sales_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="SET NULL"), nullable=True, index=True
    )
    style_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_templates.id", ondelete="SET NULL"), nullable=True
    )
    contract_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_contracts.id", ondelete="SET NULL"), nullable=True
    )
    bom_parent_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    routing_id: Mapped[int | None] = mapped_column(
        ForeignKey("routings.id", ondelete="SET NULL"), nullable=True
    )
    target_ship_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planning_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
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

    contract: Mapped[ProductionContract | None] = relationship(back_populates="production_plans")
    lines: Mapped[list[ProductionPlanLine]] = relationship(
        back_populates="plan", order_by="ProductionPlanLine.id"
    )
    schedules: Mapped[list[ProductionPlanSchedule]] = relationship(back_populates="plan")
    cut_orders: Mapped[list[CutOrder]] = relationship(back_populates="plan")
    balance_sessions: Mapped[list[LineBalanceSession]] = relationship(back_populates="plan")


class ProductionPlanLine(Base):
    __tablename__ = "production_plan_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_plan_id: Mapped[int] = mapped_column(
        ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    color_value_id: Mapped[int | None] = mapped_column(
        ForeignKey("attribute_values.id", ondelete="SET NULL"), nullable=True
    )
    size_value_id: Mapped[int | None] = mapped_column(
        ForeignKey("attribute_values.id", ondelete="SET NULL"), nullable=True
    )
    quantity_planned: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    quantity_cut: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_sewn: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    quantity_packed: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    plan: Mapped[ProductionPlan] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()
    color_value: Mapped["AttributeValue | None"] = relationship(foreign_keys=[color_value_id])
    size_value: Mapped["AttributeValue | None"] = relationship(foreign_keys=[size_value_id])


class ProductionPlanSchedule(Base):
    __tablename__ = "production_plan_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_plan_id: Mapped[int] = mapped_column(
        ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sewing_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("sewing_lines.id", ondelete="SET NULL"), nullable=True
    )
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)
    shift_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    planned_output: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)

    plan: Mapped[ProductionPlan] = relationship(back_populates="schedules")
    sewing_line: Mapped[SewingLine | None] = relationship(back_populates="schedules")


class CutOrder(Base):
    __tablename__ = "cut_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cut_order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    production_plan_id: Mapped[int] = mapped_column(
        ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[CutOrderStatus] = mapped_column(
        Enum(CutOrderStatus, name="cutorderstatus", values_callable=_enum_values),
        nullable=False,
        default=CutOrderStatus.DRAFT,
    )
    fabric_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="SET NULL"), nullable=True
    )
    cutting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    marker_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    marker_length: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    marker_width: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    efficiency_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    plies: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    plan: Mapped[ProductionPlan] = relationship(back_populates="cut_orders")
    fabric_item: Mapped["ManufacturingItem | None"] = relationship()
    size_breakdowns: Mapped[list[CutOrderSizeBreakdown]] = relationship(back_populates="cut_order")
    fabric_allocations: Mapped[list[CutOrderFabricAllocation]] = relationship(
        back_populates="cut_order"
    )


class CutOrderSizeBreakdown(Base):
    __tablename__ = "cut_order_size_breakdowns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cut_order_id: Mapped[int] = mapped_column(
        ForeignKey("cut_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    production_plan_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_plan_lines.id", ondelete="SET NULL"), nullable=True
    )
    color_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pieces_to_cut: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    pieces_cut: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    wastage_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)

    cut_order: Mapped[CutOrder] = relationship(back_populates="size_breakdowns")


class CutOrderFabricAllocation(Base):
    __tablename__ = "cut_order_fabric_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cut_order_id: Mapped[int] = mapped_column(
        ForeignKey("cut_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    roll_lot_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    material_roll_id: Mapped[int | None] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    meters_allocated: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)

    cut_order: Mapped[CutOrder] = relationship(back_populates="fabric_allocations")


class LineBalanceSession(Base):
    __tablename__ = "line_balance_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    production_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_plans.id", ondelete="CASCADE"), nullable=True, index=True
    )
    production_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=True, index=True
    )
    sewing_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("sewing_lines.id", ondelete="SET NULL"), nullable=True
    )
    target_output_per_hour: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    available_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    target_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    operators_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    calculated_takt_minutes: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    line_efficiency_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    bottleneck_station: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    plan: Mapped[ProductionPlan | None] = relationship(back_populates="balance_sessions")
    sewing_line: Mapped[SewingLine | None] = relationship(back_populates="balance_sessions")
    assignments: Mapped[list[LineBalanceAssignment]] = relationship(
        back_populates="session", order_by="LineBalanceAssignment.station_no"
    )


class LineBalanceAssignment(Base):
    __tablename__ = "line_balance_assignments"
    __table_args__ = (
        UniqueConstraint("session_id", "station_no", name="uq_lb_session_station"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("line_balance_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    routing_operation_id: Mapped[int | None] = mapped_column(
        ForeignKey("routing_operations.id", ondelete="SET NULL"), nullable=True
    )
    operation_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("operation_definitions.id", ondelete="SET NULL"), nullable=True
    )
    operation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    station_no: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_smv: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    operator_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)

    session: Mapped[LineBalanceSession] = relationship(back_populates="assignments")
