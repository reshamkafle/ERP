"""Production plan lifecycle: from sales order, schedule, release to cut orders and MOs."""

from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import garment_planning as gp_crud
from app.crud import manufacturing_ops as mfg_crud
from app.manufacturing.bom.service import BOMService
from app.manufacturing.bom.sql_repository import SqlBOMRepository
from app.models.enums import (
    CutOrderStatus,
    ProductionOrderSource,
    ProductionPhase,
    ProductionPlanStatus,
)
from app.models.garment_planning import (
    CutOrder,
    CutOrderSizeBreakdown,
    ProductionPlan,
    ProductionPlanLine,
    ProductionPlanSchedule,
)
from app.models.manufacturing import ManufacturingItem
from app.models.product import Product
from app.models.product_variant import AttributeValue
from app.models.sale import Sale, SaleItem
from app.schemas.garment_planning import (
    CutOrderCreate,
    CutOrderSizeBreakdownIn,
    ProductionPlanCreate,
    ProductionPlanFromSalesIn,
    ProductionPlanLineIn,
)
from app.schemas.manufacturing import ProductionOrderCreate
from app.services.line_balance_service import build_session_from_calculate
from app.schemas.garment_planning import LineBalanceCalculateIn, LineBalanceOperationIn


async def create_plan_from_sales_order(
    db: AsyncSession,
    payload: ProductionPlanFromSalesIn,
    *,
    created_by_id: int | None,
) -> ProductionPlan:
    result = await db.execute(
        select(Sale)
        .where(Sale.id == payload.sales_order_id)
        .options(selectinload(Sale.items).selectinload(SaleItem.product)),
    )
    sale = result.scalar_one_or_none()
    if sale is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Sales order not found")

    lines: list[ProductionPlanLineIn] = []
    style_template_id: int | None = None

    for item in sale.items or []:
        if item.product_id is None:
            continue
        product = item.product
        if product is None:
            product = await db.get(Product, item.product_id)
        if product is None:
            continue
        if product.template_id and style_template_id is None:
            style_template_id = product.template_id

        color_id = product.color_value_id
        size_id = product.size_value_id
        lines.append(
            ProductionPlanLineIn(
                product_id=product.id,
                color_value_id=color_id,
                size_value_id=size_id,
                quantity_planned=Decimal(str(item.quantity)),
                due_date=sale.requested_delivery_date or sale.order_date,
                priority=5,
            ),
        )

    if not lines:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Sales order has no product lines")

    plan_payload = ProductionPlanCreate(
        sales_order_id=sale.id,
        style_template_id=style_template_id,
        contract_id=payload.contract_id,
        bom_parent_item_id=payload.bom_parent_item_id,
        routing_id=payload.routing_id,
        target_ship_date=payload.target_ship_date or sale.requested_delivery_date,
        lines=lines,
    )
    return await gp_crud.create_production_plan(db, plan_payload, created_by_id=created_by_id)


async def auto_schedule_plan(db: AsyncSession, plan: ProductionPlan) -> ProductionPlan:
    """Earliest-due-date heuristic: spread total qty across sewing lines by capacity."""
    if not plan.lines:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Plan has no lines")

    sewing_lines = await gp_crud.list_sewing_lines(db)
    active_lines = [sl for sl in sewing_lines if sl.is_active]
    if not active_lines:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No active sewing lines configured")

    total_qty = sum((ln.quantity_planned for ln in plan.lines), Decimal("0"))
    start = date.today()
    schedules: list[ProductionPlanSchedule] = []

    line_idx = 0
    days_needed = max(1, int((total_qty / Decimal("500")).to_integral_value()) + 1)
    daily_output = (total_qty / Decimal(str(days_needed))).quantize(Decimal("0.01"))

    for day_offset in range(days_needed):
        sl = active_lines[line_idx % len(active_lines)]
        eff = sl.efficiency_pct / Decimal("100")
        cap = sl.minutes_per_shift / Decimal("60") * eff * Decimal(str(sl.operators_count))
        output = min(daily_output, cap * Decimal("8")) if cap > 0 else daily_output
        schedules.append(
            ProductionPlanSchedule(
                production_plan_id=plan.id,
                sewing_line_id=sl.id,
                schedule_date=start + timedelta(days=day_offset),
                shift_code="DAY",
                planned_output=output,
            ),
        )
        line_idx += 1

    await gp_crud.replace_plan_schedules(db, plan, schedules)
    plan.status = ProductionPlanStatus.SCHEDULED
    await db.flush()
    return await gp_crud.get_production_plan(db, plan.id)  # type: ignore[return-value]


async def _label_for_value(db: AsyncSession, value_id: int | None) -> str | None:
    if value_id is None:
        return None
    av = await db.get(AttributeValue, value_id)
    return av.code if av else None


async def generate_cut_orders_for_plan(db: AsyncSession, plan: ProductionPlan) -> list[CutOrder]:
    """Create cut orders from BOM fabric explosion grouped by fabric item."""
    if plan.bom_parent_item_id is None:
        mfg = await db.execute(
            select(ManufacturingItem).where(ManufacturingItem.product_id == plan.lines[0].product_id).limit(1),
        )
        mfg_item = mfg.scalar_one_or_none()
        if mfg_item is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Set bom_parent_item_id or link products to manufacturing items",
            )
        bom_sku = mfg_item.sku
    else:
        mfg_item = await db.get(ManufacturingItem, plan.bom_parent_item_id)
        if mfg_item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="BOM parent item not found")
        bom_sku = mfg_item.sku

    total_qty = int(sum((ln.quantity_planned for ln in plan.lines), Decimal("0")))
    if total_qty < 1:
        total_qty = 1

    bom_svc = BOMService(SqlBOMRepository(db))
    try:
        fabric_summary = await bom_svc.get_fabric_consumption_summary(bom_sku, order_qty=total_qty)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot explode fabric from BOM: {exc}",
        ) from exc

    created: list[CutOrder] = []
    size_breakdowns: list[CutOrderSizeBreakdownIn] = []
    for pline in plan.lines:
        color_label = await _label_for_value(db, pline.color_value_id)
        size_label = await _label_for_value(db, pline.size_value_id)
        size_breakdowns.append(
            CutOrderSizeBreakdownIn(
                production_plan_line_id=pline.id,
                color_label=color_label,
                size_label=size_label,
                pieces_to_cut=pline.quantity_planned,
            ),
        )

    for fabric_line in fabric_summary.fabrics:
        mfg_result = await db.execute(
            select(ManufacturingItem).where(ManufacturingItem.sku == fabric_line.sku),
        )
        mfg_fabric = mfg_result.scalar_one_or_none()
        fabric_item_id = mfg_fabric.id if mfg_fabric else None
        co = await gp_crud.create_cut_order(
            db,
            CutOrderCreate(
                production_plan_id=plan.id,
                fabric_item_id=fabric_item_id,
                cutting_date=plan.target_ship_date,
                priority=5,
                marker_ref=f"MKR-{plan.plan_number}",
                plies=max(1, total_qty // 100),
                size_breakdowns=size_breakdowns,
            ),
        )
        co.status = CutOrderStatus.RELEASED
        created.append(co)

    if not created and plan.lines:
        co = await gp_crud.create_cut_order(
            db,
            CutOrderCreate(
                production_plan_id=plan.id,
                cutting_date=plan.target_ship_date,
                size_breakdowns=size_breakdowns,
            ),
        )
        co.status = CutOrderStatus.RELEASED
        created.append(co)

    await db.flush()
    return created


async def release_production_plan(
    db: AsyncSession,
    plan: ProductionPlan,
    *,
    created_by_id: int | None,
    create_line_balance: bool = True,
) -> ProductionPlan:
    if plan.status not in (ProductionPlanStatus.DRAFT, ProductionPlanStatus.SCHEDULED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Plan cannot be released in current status")

    plan = await gp_crud.get_production_plan(db, plan.id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Plan not found")

    await generate_cut_orders_for_plan(db, plan)

    grouped: dict[int, Decimal] = {}
    for line in plan.lines:
        grouped[line.product_id] = grouped.get(line.product_id, Decimal("0")) + line.quantity_planned

    for product_id, qty in grouped.items():
        po = await mfg_crud.create_production_order(
            db,
            ProductionOrderCreate(
                product_id=product_id,
                quantity_planned=qty,
                bom_parent_item_id=plan.bom_parent_item_id,
                routing_id=plan.routing_id,
                sales_order_id=plan.sales_order_id,
                creation_source=ProductionOrderSource.SALES,
                start_date=plan.target_ship_date,
                notes=f"From plan {plan.plan_number}",
            ),
            created_by_id=created_by_id,
        )
        po.production_plan_id = plan.id
        po.contract_id = plan.contract_id
        po.production_phase = ProductionPhase.MAKE

    if create_line_balance and plan.routing_id:
        routing = await mfg_crud.get_routing(db, plan.routing_id)
        if routing and routing.operations:
            total_qty = sum((ln.quantity_planned for ln in plan.lines), Decimal("0")) or Decimal("1")
            ops = []
            for rop in routing.operations:
                smv = rop.smv_minutes if rop.smv_minutes is not None else rop.run_time_minutes
                ops.append(
                    LineBalanceOperationIn(
                        routing_operation_id=rop.id,
                        operation_name=rop.operation_name,
                        smv_minutes=smv,
                    ),
                )
            sewing_lines = await gp_crud.list_sewing_lines(db)
            sl_id = sewing_lines[0].id if sewing_lines else None
            minutes = Decimal("480")
            if sewing_lines:
                minutes = sewing_lines[0].minutes_per_shift

            calc = LineBalanceCalculateIn(
                operations=ops,
                operators_count=sewing_lines[0].operators_count if sewing_lines else 5,
                target_quantity=total_qty,
                available_minutes=minutes,
            )
            session, assignments = build_session_from_calculate(
                calc,
                production_plan_id=plan.id,
                production_order_id=None,
                sewing_line_id=sl_id,
                target_output_per_hour=total_qty / (minutes / Decimal("60")),
            )
            await gp_crud.save_line_balance_session(db, session, assignments)

    plan.status = ProductionPlanStatus.IN_PROGRESS
    await db.flush()
    return await gp_crud.get_production_plan(db, plan.id)  # type: ignore[return-value]


async def complete_cut_order(db: AsyncSession, cut_order: CutOrder) -> CutOrder:
    if cut_order.status not in (CutOrderStatus.RELEASED, CutOrderStatus.CUTTING):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cut order cannot be completed")

    plan = await gp_crud.get_production_plan(db, cut_order.production_plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production plan not found")

    for bd in cut_order.size_breakdowns:
        bd.pieces_cut = bd.pieces_to_cut
        if bd.production_plan_line_id:
            for pline in plan.lines:
                if pline.id == bd.production_plan_line_id:
                    pline.quantity_cut = bd.pieces_cut

    cut_order.status = CutOrderStatus.COMPLETED
    await db.flush()
    return await gp_crud.get_cut_order(db, cut_order.id)  # type: ignore[return-value]
