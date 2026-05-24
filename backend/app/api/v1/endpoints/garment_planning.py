"""Garment production planning API: contracts, plans, cut orders, line balancing."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import garment_planning as gp_crud
from app.dependencies.auth import require_permission
from app.models.enums import CutOrderStatus
from app.models.garment_planning import LineBalanceAssignment
from app.models.user import User
from app.schemas.garment_planning import (
    CutOrderCompleteIn,
    CutOrderCreate,
    CutOrderRead,
    CutOrderUpdate,
    LineBalanceAssignmentPatch,
    LineBalanceAssignmentRead,
    LineBalanceCalculateIn,
    LineBalanceCalculateResult,
    LineBalanceSessionCreate,
    LineBalanceSessionRead,
    LineBalanceStationLoad,
    ProductionContractCreate,
    ProductionContractRead,
    ProductionContractUpdate,
    ProductionPlanCreate,
    ProductionPlanFromSalesIn,
    ProductionPlanListResponse,
    ProductionPlanRead,
    ProductionPlanUpdate,
    SewingLineCreate,
    SewingLineRead,
)
from app.services.line_balance_service import (
    calculate_line_balance,
    recalc_session_metrics,
)
from app.services.production_plan_service import (
    auto_schedule_plan,
    complete_cut_order,
    create_plan_from_sales_order,
    release_production_plan,
)

router = APIRouter(prefix="/manufacturing")

PlanRead = require_permission("manufacturing.planning.read", "manufacturing.ops.read")
PlanWrite = require_permission("manufacturing.planning.write", "manufacturing.ops.write")


def _plan_line_read(line) -> dict:
    product = line.product
    color = line.color_value
    size = line.size_value
    data = {
        "id": line.id,
        "production_plan_id": line.production_plan_id,
        "product_id": line.product_id,
        "color_value_id": line.color_value_id,
        "size_value_id": line.size_value_id,
        "quantity_planned": line.quantity_planned,
        "quantity_cut": line.quantity_cut,
        "quantity_sewn": line.quantity_sewn,
        "quantity_packed": line.quantity_packed,
        "due_date": line.due_date,
        "priority": line.priority,
        "product_sku": product.sku if product else None,
        "product_name": product.name if product else None,
        "color_label": color.code if color else None,
        "size_label": size.code if size else None,
    }
    return data


def _plan_to_read(plan) -> ProductionPlanRead:
    contract = plan.contract
    from app.schemas.garment_planning import ProductionPlanLineRead, ProductionPlanScheduleRead

    lines = [ProductionPlanLineRead(**_plan_line_read(ln)) for ln in (plan.lines or [])]
    schedules = [
        ProductionPlanScheduleRead(
            id=s.id,
            production_plan_id=s.production_plan_id,
            sewing_line_id=s.sewing_line_id,
            schedule_date=s.schedule_date,
            shift_code=s.shift_code,
            planned_output=s.planned_output,
            sewing_line_code=s.sewing_line.code if s.sewing_line else None,
        )
        for s in (plan.schedules or [])
    ]
    return ProductionPlanRead(
        id=plan.id,
        plan_number=plan.plan_number,
        status=plan.status,
        sales_order_id=plan.sales_order_id,
        style_template_id=plan.style_template_id,
        contract_id=plan.contract_id,
        bom_parent_item_id=plan.bom_parent_item_id,
        routing_id=plan.routing_id,
        target_ship_date=plan.target_ship_date,
        planning_horizon_days=plan.planning_horizon_days,
        notes=plan.notes,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        lines=lines,
        schedules=schedules,
        contract_type=contract.contract_type if contract else None,
        contract_number=contract.contract_number if contract else None,
    )


def _cut_order_to_read(co) -> CutOrderRead:
    fabric = co.fabric_item
    return CutOrderRead(
        id=co.id,
        cut_order_number=co.cut_order_number,
        production_plan_id=co.production_plan_id,
        status=co.status,
        fabric_item_id=co.fabric_item_id,
        cutting_date=co.cutting_date,
        priority=co.priority,
        marker_ref=co.marker_ref,
        marker_length=co.marker_length,
        marker_width=co.marker_width,
        efficiency_pct=co.efficiency_pct,
        plies=co.plies,
        notes=co.notes,
        created_at=co.created_at,
        updated_at=co.updated_at,
        size_breakdowns=co.size_breakdowns or [],
        fabric_allocations=co.fabric_allocations or [],
        fabric_item_sku=fabric.sku if fabric else None,
    )


def _session_to_read(session) -> LineBalanceSessionRead:
    loads: dict[int, float] = {}
    for a in session.assignments or []:
        loads[a.station_no] = loads.get(a.station_no, 0) + float(a.assigned_smv)
    takt = float(session.calculated_takt_minutes or 1)
    station_loads = [
        LineBalanceStationLoad(
            station_no=st,
            total_smv=sum(float(x.assigned_smv) for x in session.assignments if x.station_no == st),
            utilization_pct=round(loads[st] / takt * 100, 2) if takt else 0,
        )
        for st in sorted(loads.keys())
    ]
    return LineBalanceSessionRead(
        id=session.id,
        production_plan_id=session.production_plan_id,
        production_order_id=session.production_order_id,
        sewing_line_id=session.sewing_line_id,
        target_output_per_hour=session.target_output_per_hour,
        available_minutes=session.available_minutes,
        target_quantity=session.target_quantity,
        operators_count=session.operators_count,
        calculated_takt_minutes=session.calculated_takt_minutes,
        line_efficiency_pct=session.line_efficiency_pct,
        bottleneck_station=session.bottleneck_station,
        created_at=session.created_at,
        assignments=[LineBalanceAssignmentRead.model_validate(a) for a in (session.assignments or [])],
        station_loads=station_loads,
    )


# --- Contracts ---


@router.get("/contracts", response_model=list[ProductionContractRead])
async def list_contracts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    items = await gp_crud.list_contracts(db)
    return [ProductionContractRead.model_validate(i) for i in items]


@router.post("/contracts", response_model=ProductionContractRead, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ProductionContractCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    contract = await gp_crud.create_contract(db, payload)
    await db.commit()
    return ProductionContractRead.model_validate(contract)


@router.get("/contracts/{contract_id}", response_model=ProductionContractRead)
async def get_contract(
    contract_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    contract = await gp_crud.get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return ProductionContractRead.model_validate(contract)


@router.patch("/contracts/{contract_id}", response_model=ProductionContractRead)
async def update_contract(
    contract_id: int,
    payload: ProductionContractUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    contract = await gp_crud.get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Contract not found")
    contract = await gp_crud.update_contract(db, contract, payload)
    await db.commit()
    return ProductionContractRead.model_validate(contract)


# --- Sewing lines ---


@router.get("/sewing-lines", response_model=list[SewingLineRead])
async def list_sewing_lines(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    items = await gp_crud.list_sewing_lines(db)
    return [SewingLineRead.model_validate(i) for i in items]


@router.post("/sewing-lines", response_model=SewingLineRead, status_code=status.HTTP_201_CREATED)
async def create_sewing_line(
    payload: SewingLineCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    line = await gp_crud.create_sewing_line(db, payload)
    await db.commit()
    return SewingLineRead.model_validate(line)


# --- Production plans ---


@router.get("/planning/plans", response_model=ProductionPlanListResponse)
async def list_production_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
    skip: int = 0,
    limit: int = 100,
):
    items, total = await gp_crud.list_production_plans(db, skip=skip, limit=limit)
    return ProductionPlanListResponse(items=[_plan_to_read(p) for p in items], total=total)


@router.post("/planning/plans", response_model=ProductionPlanRead, status_code=status.HTTP_201_CREATED)
async def create_production_plan(
    payload: ProductionPlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PlanWrite)],
):
    plan = await gp_crud.create_production_plan(db, payload, created_by_id=user.id)
    await db.commit()
    plan = await gp_crud.get_production_plan(db, plan.id)
    return _plan_to_read(plan)


@router.post("/planning/plans/from-sales", response_model=ProductionPlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan_from_sales(
    payload: ProductionPlanFromSalesIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PlanWrite)],
):
    plan = await create_plan_from_sales_order(db, payload, created_by_id=user.id)
    await db.commit()
    plan = await gp_crud.get_production_plan(db, plan.id)
    return _plan_to_read(plan)


@router.get("/planning/plans/{plan_id}", response_model=ProductionPlanRead)
async def get_production_plan(
    plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    plan = await gp_crud.get_production_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production plan not found")
    return _plan_to_read(plan)


@router.patch("/planning/plans/{plan_id}", response_model=ProductionPlanRead)
async def update_production_plan(
    plan_id: int,
    payload: ProductionPlanUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    plan = await gp_crud.get_production_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production plan not found")
    plan = await gp_crud.update_production_plan(db, plan, payload)
    await db.commit()
    plan = await gp_crud.get_production_plan(db, plan.id)
    return _plan_to_read(plan)


@router.post("/planning/plans/{plan_id}/schedule", response_model=ProductionPlanRead)
async def schedule_production_plan(
    plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    plan = await gp_crud.get_production_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production plan not found")
    plan = await auto_schedule_plan(db, plan)
    await db.commit()
    plan = await gp_crud.get_production_plan(db, plan.id)
    return _plan_to_read(plan)


@router.post("/planning/plans/{plan_id}/release", response_model=ProductionPlanRead)
async def release_plan(
    plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PlanWrite)],
):
    plan = await gp_crud.get_production_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production plan not found")
    plan = await release_production_plan(db, plan, created_by_id=user.id)
    await db.commit()
    plan = await gp_crud.get_production_plan(db, plan.id)
    return _plan_to_read(plan)


# --- Cut orders ---


@router.get("/cut-orders", response_model=list[CutOrderRead])
async def list_cut_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
    plan_id: int | None = Query(None),
    skip: int = 0,
    limit: int = 100,
):
    items, _ = await gp_crud.list_cut_orders(db, plan_id=plan_id, skip=skip, limit=limit)
    return [_cut_order_to_read(co) for co in items]


@router.post("/cut-orders", response_model=CutOrderRead, status_code=status.HTTP_201_CREATED)
async def create_cut_order(
    payload: CutOrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    co = await gp_crud.create_cut_order(db, payload)
    await db.commit()
    co = await gp_crud.get_cut_order(db, co.id)
    return _cut_order_to_read(co)


@router.get("/cut-orders/{cut_order_id}", response_model=CutOrderRead)
async def get_cut_order(
    cut_order_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    co = await gp_crud.get_cut_order(db, cut_order_id)
    if co is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cut order not found")
    return _cut_order_to_read(co)


@router.patch("/cut-orders/{cut_order_id}", response_model=CutOrderRead)
async def update_cut_order(
    cut_order_id: int,
    payload: CutOrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    co = await gp_crud.get_cut_order(db, cut_order_id)
    if co is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cut order not found")
    co = await gp_crud.update_cut_order(db, co, payload)
    await db.commit()
    co = await gp_crud.get_cut_order(db, co.id)
    return _cut_order_to_read(co)


@router.post("/cut-orders/{cut_order_id}/complete", response_model=CutOrderRead)
async def complete_cut_order_endpoint(
    cut_order_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
    body: CutOrderCompleteIn | None = None,
):
    co = await gp_crud.get_cut_order(db, cut_order_id)
    if co is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cut order not found")
    if body and body.size_breakdowns:
        co.status = CutOrderStatus.CUTTING
    co = await complete_cut_order(db, co)
    await db.commit()
    co = await gp_crud.get_cut_order(db, co.id)
    return _cut_order_to_read(co)


# --- Line balancing ---


@router.post("/line-balancing/calculate", response_model=LineBalanceCalculateResult)
async def calculate_balance(
    payload: LineBalanceCalculateIn,
    _: Annotated[User, Depends(PlanRead)],
):
    return calculate_line_balance(payload)


@router.post("/line-balancing/sessions", response_model=LineBalanceSessionRead, status_code=status.HTTP_201_CREATED)
async def create_balance_session(
    payload: LineBalanceSessionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    from app.services.line_balance_service import build_session_from_calculate

    calc = LineBalanceCalculateIn(
        operations=payload.operations,
        operators_count=payload.operators_count,
        target_quantity=payload.target_quantity,
        available_minutes=payload.available_minutes,
    )
    session, assignments = build_session_from_calculate(
        calc,
        production_plan_id=payload.production_plan_id,
        production_order_id=payload.production_order_id,
        sewing_line_id=payload.sewing_line_id,
        target_output_per_hour=payload.target_output_per_hour,
    )
    session = await gp_crud.save_line_balance_session(db, session, assignments)
    await db.commit()
    session = await gp_crud.get_line_balance_session(db, session.id)
    return _session_to_read(session)


@router.get("/line-balancing/sessions/{session_id}", response_model=LineBalanceSessionRead)
async def get_balance_session(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanRead)],
):
    session = await gp_crud.get_line_balance_session(db, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Line balance session not found")
    return _session_to_read(session)


@router.patch(
    "/line-balancing/sessions/{session_id}/assignments/{assignment_id}",
    response_model=LineBalanceAssignmentRead,
)
async def patch_balance_assignment(
    session_id: int,
    assignment_id: int,
    payload: LineBalanceAssignmentPatch,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PlanWrite)],
):
    session = await gp_crud.get_line_balance_session(db, session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Session not found")
    assignment = next((a for a in session.assignments if a.id == assignment_id), None)
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    assignment = await gp_crud.update_line_balance_assignment(
        db, assignment, payload.station_no, payload.operator_ref
    )
    recalc_session_metrics(session)
    await db.flush()
    await db.commit()
    session = await gp_crud.get_line_balance_session(db, session_id)
    return LineBalanceAssignmentRead.model_validate(
        next(a for a in session.assignments if a.id == assignment_id),
    )
