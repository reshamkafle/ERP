"""Manufacturing operations: routings, work centers, production orders, MRP, quality

Revision ID: o9p1r3t5v717
Revises: n8p0r2t4u516
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "o9p1r3t5v717"
down_revision: Union[str, None] = "n8p0r2t4u516"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum(name: str, values: list[str]) -> None:
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(sa.text(f"CREATE TYPE {name} AS ENUM ({vals})"))


def _apply_enum_extensions() -> None:
    bind = op.get_bind()
    for name, values in [
        ("productionorderstatus", ["PLANNED", "RELEASED", "IN_PROGRESS", "COMPLETED", "CLOSED", "CANCELLED"]),
        ("productionordersource", ["MANUAL", "MRP", "SALES"]),
        ("materialissuemethod", ["MANUAL", "BACKFLUSH"]),
        ("mrprunstatus", ["DRAFT", "RUNNING", "COMPLETED", "FAILED"]),
        ("plannedordertype", ["MAKE", "BUY"]),
        ("inspectionstage", ["INBOUND", "IN_PROCESS", "FINAL"]),
        ("nonconformancedisposition", ["SCRAP", "REWORK", "RETURN", "USE_AS_IS"]),
        ("engineeringchangestatus", ["DRAFT", "APPROVED", "IMPLEMENTED"]),
        ("variancetype", ["MATERIAL", "LABOR", "OVERHEAD"]),
    ]:
        sa.Enum(*values, name=name).create(bind, checkfirst=True)

    for val in ("PRODUCTION_ISSUE", "PRODUCTION_RECEIPT", "WIP_TRANSFER"):
        op.execute(sa.text(f"ALTER TYPE inventorytransactiontype ADD VALUE IF NOT EXISTS '{val}'"))
    op.execute(sa.text("ALTER TYPE journalsourcetype ADD VALUE IF NOT EXISTS 'MANUFACTURING'"))
    op.execute(sa.text("ALTER TYPE storagelocationtype ADD VALUE IF NOT EXISTS 'WIP'"))
    op.execute(sa.text("ALTER TYPE erpdocumenttype ADD VALUE IF NOT EXISTS 'CERTIFICATE_OF_ANALYSIS'"))


def upgrade() -> None:
    _apply_enum_extensions()

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "production_calendars" in inspector.get_table_names():
        if "company_settings" in inspector.get_table_names():
            cols = {c["name"] for c in inspector.get_columns("company_settings")}
            if "mrp_order_creation_mode" not in cols:
                op.add_column(
                    "company_settings",
                    sa.Column(
                        "mrp_order_creation_mode",
                        sa.String(length=32),
                        nullable=False,
                        server_default="manual",
                    ),
                )
        return

    op.create_table(
        "production_calendars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("working_days", sa.String(length=32), nullable=False, server_default="1111100"),
        sa.Column("hours_per_day", sa.Numeric(6, 2), nullable=False, server_default="8"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "shift_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("calendar_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("start_time", sa.String(length=8), nullable=False),
        sa.Column("end_time", sa.String(length=8), nullable=False),
        sa.Column("break_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["calendar_id"], ["production_calendars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "work_centers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("capacity_hrs_per_shift", sa.Numeric(8, 2), nullable=False, server_default="8"),
        sa.Column("efficiency_pct", sa.Numeric(6, 2), nullable=False, server_default="100"),
        sa.Column("labor_rate_per_hr", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("machine_rate_per_hr", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("overhead_rate_per_hr", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("calendar_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["calendar_id"], ["production_calendars.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "work_center_maintenance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("work_center_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["work_center_id"], ["work_centers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "routings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_item_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "routing_operations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("routing_id", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("operation_name", sa.String(length=255), nullable=False),
        sa.Column("work_center_id", sa.Integer(), nullable=True),
        sa.Column("setup_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("run_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("cycle_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("requires_labor", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("requires_machine", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_subcontract", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("supplier_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["routing_id"], ["routings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_center_id"], ["work_centers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("routing_id", "sequence", name="uq_routing_op_sequence"),
    )

    op.create_table(
        "production_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("bom_parent_item_id", sa.Integer(), nullable=False),
        sa.Column("routing_id", sa.Integer(), nullable=False),
        sa.Column("version_code", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("effective_start_date", sa.Date(), nullable=True),
        sa.Column("effective_end_date", sa.Date(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["bom_parent_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["routing_id"], ["routings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "version_code", name="uq_prod_version_product_code"),
    )

    op.create_table(
        "production_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PLANNED", "RELEASED", "IN_PROGRESS", "COMPLETED", "CLOSED", "CANCELLED",
                name="productionorderstatus", create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("priority", sa.Enum("HIGH", "MEDIUM", "LOW", name="orderpriority", create_type=False), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity_planned", sa.Numeric(14, 4), nullable=False),
        sa.Column("quantity_completed", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_scrapped", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_rework", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("bom_parent_item_id", sa.Integer(), nullable=True),
        sa.Column("routing_id", sa.Integer(), nullable=True),
        sa.Column("production_version_id", sa.Integer(), nullable=True),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("warehouse_id", sa.Integer(), nullable=True),
        sa.Column("wip_warehouse_id", sa.Integer(), nullable=True),
        sa.Column(
            "creation_source",
            sa.Enum("MANUAL", "MRP", "SALES", name="productionordersource", create_type=False),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bom_parent_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_id"], ["routings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_version_id"], ["production_versions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["wip_warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_number"),
    )

    op.create_table(
        "production_order_operations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column("routing_operation_id", sa.Integer(), nullable=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("operation_name", sa.String(length=255), nullable=False),
        sa.Column("work_center_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("setup_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("run_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["routing_operation_id"], ["routing_operations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_center_id"], ["work_centers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("production_order_id", "sequence", name="uq_po_op_sequence"),
    )

    op.create_table(
        "production_material_issues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column("component_item_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column(
            "issue_method",
            sa.Enum("MANUAL", "BACKFLUSH", name="materialissuemethod", create_type=False),
            nullable=False,
        ),
        sa.Column("lot_number", sa.String(length=64), nullable=True),
        sa.Column("serial_number", sa.String(length=128), nullable=True),
        sa.Column("warehouse_id", sa.Integer(), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("issued_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["component_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["issued_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "production_confirmations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=True),
        sa.Column("quantity_completed", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_rejected", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_rework", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("confirmed_by_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_id"], ["production_order_operations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["confirmed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "shop_floor_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.Integer(), nullable=True),
        sa.Column("actual_time_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("output_quantity", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("scrap_quantity", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("downtime_minutes", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("downtime_reason", sa.String(length=255), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("recorded_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["operation_id"], ["production_order_operations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recorded_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "mrp_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "RUNNING", "COMPLETED", "FAILED", name="mrprunstatus", create_type=False),
            nullable=False,
        ),
        sa.Column("parameters", JSONB(), nullable=True),
        sa.Column("horizon_days", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_number"),
    )

    op.create_table(
        "mrp_demand_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mrp_run_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("manufacturing_item_id", sa.Integer(), nullable=True),
        sa.Column("demand_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("source_reference", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["mrp_run_id"], ["mrp_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["manufacturing_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "mrp_planned_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mrp_run_id", sa.Integer(), nullable=False),
        sa.Column(
            "order_type",
            sa.Enum("MAKE", "BUY", name="plannedordertype", create_type=False),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("manufacturing_item_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("planned_start_date", sa.Date(), nullable=False),
        sa.Column("planned_end_date", sa.Date(), nullable=True),
        sa.Column("is_firmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("production_order_id", sa.Integer(), nullable=True),
        sa.Column("pegged_demand_line_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["mrp_run_id"], ["mrp_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["manufacturing_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["pegged_demand_line_id"], ["mrp_demand_lines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "mrp_forecasts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("forecast_date", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "master_production_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "mps_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["master_production_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "quality_inspection_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "stage",
            sa.Enum("INBOUND", "IN_PROCESS", "FINAL", name="inspectionstage", create_type=False),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("production_order_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "inspection_characteristics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("attribute_type", sa.String(length=32), nullable=False, server_default="NUMERIC"),
        sa.Column("min_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("target_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("acceptance_criteria", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["quality_inspection_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inspection_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=True),
        sa.Column("characteristic_id", sa.Integer(), nullable=False),
        sa.Column("measured_value", sa.Numeric(14, 4), nullable=True),
        sa.Column("attribute_result", sa.String(length=64), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("inspected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("inspected_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["quality_inspection_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["characteristic_id"], ["inspection_characteristics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inspected_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "non_conformances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference", sa.String(length=64), nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=True),
        sa.Column("inspection_result_id", sa.Integer(), nullable=True),
        sa.Column("defect_code", sa.String(length=64), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column(
            "disposition",
            sa.Enum("SCRAP", "REWORK", "RETURN", "USE_AS_IS", name="nonconformancedisposition", create_type=False),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["inspection_result_id"], ["inspection_results.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )

    op.create_table(
        "product_standard_costs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("material_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("labor_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("overhead_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "effective_date", name="uq_std_cost_product_date"),
    )
    op.create_table(
        "production_order_costs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column("cost_type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "production_variances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_order_id", sa.Integer(), nullable=False),
        sa.Column(
            "variance_type",
            sa.Enum("MATERIAL", "LABOR", "OVERHEAD", name="variancetype", create_type=False),
            nullable=False,
        ),
        sa.Column("standard_amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("actual_amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("variance_amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "engineering_changes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("eco_number", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "APPROVED", "IMPLEMENTED", name="engineeringchangestatus", create_type=False),
            nullable=False,
        ),
        sa.Column("bom_parent_item_id", sa.Integer(), nullable=True),
        sa.Column("routing_id", sa.Integer(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["bom_parent_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_id"], ["routings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("eco_number"),
    )
    op.create_table(
        "tooling_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("routing_operation_id", sa.Integer(), nullable=True),
        sa.Column("lifecycle_status", sa.String(length=32), nullable=False, server_default="ACTIVE"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_operation_id"], ["routing_operations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "bom_configurations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_item_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("parameters", JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "bom_alternates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_item_id", sa.Integer(), nullable=False),
        sa.Column("alternate_parent_item_id", sa.Integer(), nullable=False),
        sa.Column("alternate_group", sa.String(length=32), nullable=False, server_default="DEFAULT"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alternate_parent_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "parent_item_id", "alternate_group", "priority", name="uq_bom_alt_parent_group_priority"
        ),
    )
    op.create_table(
        "bom_substitutes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bom_line_id", sa.Integer(), nullable=False),
        sa.Column("substitute_item_id", sa.Integer(), nullable=False),
        sa.Column("substitute_quantity", sa.Numeric(12, 4), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["bom_line_id"], ["bom_lines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["substitute_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    if "company_settings" in sa.inspect(op.get_bind()).get_table_names():
        cols = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("company_settings")}
        if "mrp_order_creation_mode" not in cols:
            op.add_column(
                "company_settings",
                sa.Column("mrp_order_creation_mode", sa.String(length=32), nullable=False, server_default="manual"),
            )


def downgrade() -> None:
    op.drop_column("company_settings", "mrp_order_creation_mode")
    for table in [
        "bom_substitutes",
        "bom_alternates",
        "bom_configurations",
        "tooling_assets",
        "engineering_changes",
        "production_variances",
        "production_order_costs",
        "product_standard_costs",
        "non_conformances",
        "inspection_results",
        "inspection_characteristics",
        "quality_inspection_plans",
        "mps_lines",
        "master_production_schedules",
        "mrp_forecasts",
        "mrp_planned_orders",
        "mrp_demand_lines",
        "mrp_runs",
        "shop_floor_entries",
        "production_confirmations",
        "production_material_issues",
        "production_order_operations",
        "production_orders",
        "production_versions",
        "routing_operations",
        "routings",
        "work_center_maintenance",
        "work_centers",
        "shift_definitions",
        "production_calendars",
    ]:
        op.drop_table(table)
