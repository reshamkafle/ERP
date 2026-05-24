"""Garment production planning: CMT, APS, cut orders, line balancing

Revision ID: u8w0y2a4b623
Revises: t7v9x1z3a522
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "u8w0y2a4b623"
down_revision: Union[str, None] = "t7v9x1z3a522"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum(name: str, values: list[str]) -> None:
    vals = ", ".join(f"'{v}'" for v in values)
    op.execute(sa.text(f"CREATE TYPE {name} AS ENUM ({vals})"))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "production_plans" in inspector.get_table_names():
        return

    for name, values in [
        ("productioncontracttype", ["CMT", "FOB"]),
        ("productionphase", ["CUT", "MAKE", "TRIM"]),
        ("productionplanstatus", ["DRAFT", "SCHEDULED", "IN_PROGRESS", "CLOSED", "CANCELLED"]),
        ("cutorderstatus", ["DRAFT", "RELEASED", "CUTTING", "COMPLETED", "CANCELLED"]),
    ]:
        sa.Enum(*values, name=name).create(bind, checkfirst=True)

    op.add_column(
        "routing_operations",
        sa.Column("smv_minutes", sa.Numeric(10, 4), nullable=True),
    )

    op.create_table(
        "production_contracts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contract_number", sa.String(length=32), nullable=False),
        sa.Column(
            "contract_type",
            sa.Enum("CMT", "FOB", name="productioncontracttype", create_type=False),
            nullable=False,
        ),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("buyer_name", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contract_number"),
    )
    op.create_index("ix_production_contracts_contract_number", "production_contracts", ["contract_number"])

    op.create_table(
        "cmt_material_supplies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("manufacturing_item_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("quantity_received", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_consumed", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("uom", sa.String(length=16), nullable=True),
        sa.Column("lot_reference", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["production_contracts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manufacturing_item_id"], ["manufacturing_items.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sewing_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("operators_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("minutes_per_shift", sa.Numeric(8, 2), nullable=False, server_default="480"),
        sa.Column("efficiency_pct", sa.Numeric(6, 2), nullable=False, server_default="100"),
        sa.Column("calendar_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["calendar_id"], ["production_calendars.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "production_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SCHEDULED",
                "IN_PROGRESS",
                "CLOSED",
                "CANCELLED",
                name="productionplanstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("sales_order_id", sa.Integer(), nullable=True),
        sa.Column("style_template_id", sa.Integer(), nullable=True),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("bom_parent_item_id", sa.Integer(), nullable=True),
        sa.Column("routing_id", sa.Integer(), nullable=True),
        sa.Column("target_ship_date", sa.Date(), nullable=True),
        sa.Column("planning_horizon_days", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["bom_parent_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["contract_id"], ["production_contracts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_id"], ["routings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["style_template_id"], ["product_templates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_number"),
    )

    op.create_table(
        "operation_definitions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("smv_minutes", sa.Numeric(10, 4), nullable=False),
        sa.Column("machine_type", sa.String(length=64), nullable=True),
        sa.Column("skill_level", sa.String(length=32), nullable=True),
        sa.Column("routing_operation_id", sa.Integer(), nullable=True),
        sa.Column("parent_item_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["parent_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_operation_id"], ["routing_operations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "production_plan_lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_plan_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("color_value_id", sa.Integer(), nullable=True),
        sa.Column("size_value_id", sa.Integer(), nullable=True),
        sa.Column("quantity_planned", sa.Numeric(14, 4), nullable=False),
        sa.Column("quantity_cut", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_sewn", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("quantity_packed", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.ForeignKeyConstraint(["color_value_id"], ["attribute_values.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_plan_id"], ["production_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["size_value_id"], ["attribute_values.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "production_plan_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_plan_id", sa.Integer(), nullable=False),
        sa.Column("sewing_line_id", sa.Integer(), nullable=True),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("shift_code", sa.String(length=32), nullable=True),
        sa.Column("planned_output", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["production_plan_id"], ["production_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sewing_line_id"], ["sewing_lines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cut_orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cut_order_number", sa.String(length=32), nullable=False),
        sa.Column("production_plan_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "RELEASED",
                "CUTTING",
                "COMPLETED",
                "CANCELLED",
                name="cutorderstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("fabric_item_id", sa.Integer(), nullable=True),
        sa.Column("cutting_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("marker_ref", sa.String(length=128), nullable=True),
        sa.Column("marker_length", sa.Numeric(10, 4), nullable=True),
        sa.Column("marker_width", sa.Numeric(10, 4), nullable=True),
        sa.Column("efficiency_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("plies", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["fabric_item_id"], ["manufacturing_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["production_plan_id"], ["production_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cut_order_number"),
    )

    op.create_table(
        "cut_order_size_breakdowns",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cut_order_id", sa.Integer(), nullable=False),
        sa.Column("production_plan_line_id", sa.Integer(), nullable=True),
        sa.Column("color_label", sa.String(length=64), nullable=True),
        sa.Column("size_label", sa.String(length=64), nullable=True),
        sa.Column("pieces_to_cut", sa.Numeric(14, 4), nullable=False),
        sa.Column("pieces_cut", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("wastage_pct", sa.Numeric(6, 2), nullable=True),
        sa.ForeignKeyConstraint(["cut_order_id"], ["cut_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_plan_line_id"], ["production_plan_lines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cut_order_fabric_allocations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cut_order_id", sa.Integer(), nullable=False),
        sa.Column("roll_lot_ref", sa.String(length=64), nullable=True),
        sa.Column("meters_allocated", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["cut_order_id"], ["cut_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "line_balance_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("production_plan_id", sa.Integer(), nullable=True),
        sa.Column("production_order_id", sa.Integer(), nullable=True),
        sa.Column("sewing_line_id", sa.Integer(), nullable=True),
        sa.Column("target_output_per_hour", sa.Numeric(10, 4), nullable=False),
        sa.Column("available_minutes", sa.Numeric(10, 2), nullable=False),
        sa.Column("target_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("operators_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("calculated_takt_minutes", sa.Numeric(10, 4), nullable=True),
        sa.Column("line_efficiency_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("bottleneck_station", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["production_order_id"], ["production_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["production_plan_id"], ["production_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sewing_line_id"], ["sewing_lines.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "line_balance_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("routing_operation_id", sa.Integer(), nullable=True),
        sa.Column("operation_definition_id", sa.Integer(), nullable=True),
        sa.Column("operation_name", sa.String(length=255), nullable=False),
        sa.Column("station_no", sa.Integer(), nullable=False),
        sa.Column("assigned_smv", sa.Numeric(10, 4), nullable=False),
        sa.Column("operator_ref", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["operation_definition_id"], ["operation_definitions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["routing_operation_id"], ["routing_operations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["line_balance_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "station_no", name="uq_lb_session_station"),
    )

    op.add_column(
        "production_orders",
        sa.Column("production_plan_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "production_orders",
        sa.Column("contract_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "production_orders",
        sa.Column(
            "production_phase",
            sa.Enum("CUT", "MAKE", "TRIM", name="productionphase", create_type=False),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_production_orders_plan",
        "production_orders",
        "production_plans",
        ["production_plan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_production_orders_contract",
        "production_orders",
        "production_contracts",
        ["contract_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_production_orders_contract", "production_orders", type_="foreignkey")
    op.drop_constraint("fk_production_orders_plan", "production_orders", type_="foreignkey")
    op.drop_column("production_orders", "production_phase")
    op.drop_column("production_orders", "contract_id")
    op.drop_column("production_orders", "production_plan_id")
    op.drop_table("line_balance_assignments")
    op.drop_table("line_balance_sessions")
    op.drop_table("cut_order_fabric_allocations")
    op.drop_table("cut_order_size_breakdowns")
    op.drop_table("cut_orders")
    op.drop_table("production_plan_schedules")
    op.drop_table("production_plan_lines")
    op.drop_table("operation_definitions")
    op.drop_table("production_plans")
    op.drop_table("sewing_lines")
    op.drop_table("cmt_material_supplies")
    op.drop_table("production_contracts")
    op.drop_column("routing_operations", "smv_minutes")
    for name in ("cutorderstatus", "productionplanstatus", "productionphase", "productioncontracttype"):
        op.execute(sa.text(f"DROP TYPE IF EXISTS {name}"))
