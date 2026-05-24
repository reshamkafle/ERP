"""CRUD for garment production planning."""

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.garment_planning import (
    CmtMaterialSupply,
    CutOrder,
    CutOrderFabricAllocation,
    CutOrderSizeBreakdown,
    LineBalanceAssignment,
    LineBalanceSession,
    ProductionContract,
    ProductionPlan,
    ProductionPlanLine,
    ProductionPlanSchedule,
    SewingLine,
)
from app.models.product import Product
from app.models.product_variant import AttributeValue
from app.schemas.garment_planning import (
    CmtMaterialSupplyIn,
    CutOrderCreate,
    CutOrderUpdate,
    ProductionContractCreate,
    ProductionContractUpdate,
    ProductionPlanCreate,
    ProductionPlanLineIn,
    ProductionPlanUpdate,
    SewingLineCreate,
)


async def _next_contract_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"PC-{year}-"
    result = await db.execute(
        select(func.count()).select_from(ProductionContract).where(
            ProductionContract.contract_number.like(f"{prefix}%"),
        ),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:04d}"


async def _next_plan_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"PP-{year}-"
    result = await db.execute(
        select(func.count()).select_from(ProductionPlan).where(
            ProductionPlan.plan_number.like(f"{prefix}%"),
        ),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:04d}"


async def _next_cut_order_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"CO-{year}-"
    result = await db.execute(
        select(func.count()).select_from(CutOrder).where(
            CutOrder.cut_order_number.like(f"{prefix}%"),
        ),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:04d}"


def _plan_load_options():
    return (
        selectinload(ProductionPlan.lines).selectinload(ProductionPlanLine.product),
        selectinload(ProductionPlan.lines).selectinload(ProductionPlanLine.color_value),
        selectinload(ProductionPlan.lines).selectinload(ProductionPlanLine.size_value),
        selectinload(ProductionPlan.schedules).selectinload(ProductionPlanSchedule.sewing_line),
        selectinload(ProductionPlan.contract),
    )


def _cut_order_load_options():
    return (
        selectinload(CutOrder.size_breakdowns),
        selectinload(CutOrder.fabric_allocations),
        selectinload(CutOrder.fabric_item),
    )


# --- Contracts ---


async def list_contracts(db: AsyncSession) -> list[ProductionContract]:
    result = await db.execute(
        select(ProductionContract)
        .options(selectinload(ProductionContract.material_supplies))
        .order_by(ProductionContract.contract_number.desc()),
    )
    return list(result.scalars().unique().all())


async def get_contract(db: AsyncSession, contract_id: int) -> ProductionContract | None:
    result = await db.execute(
        select(ProductionContract)
        .where(ProductionContract.id == contract_id)
        .options(selectinload(ProductionContract.material_supplies)),
    )
    return result.scalar_one_or_none()


async def create_contract(db: AsyncSession, payload: ProductionContractCreate) -> ProductionContract:
    number = payload.contract_number or await _next_contract_number(db)
    contract = ProductionContract(
        contract_number=number,
        contract_type=payload.contract_type,
        customer_id=payload.customer_id,
        sales_order_id=payload.sales_order_id,
        buyer_name=payload.buyer_name,
        notes=payload.notes,
        is_active=payload.is_active,
    )
    db.add(contract)
    await db.flush()
    for supply in payload.material_supplies:
        db.add(CmtMaterialSupply(contract_id=contract.id, **supply.model_dump()))
    await db.flush()
    return await get_contract(db, contract.id)  # type: ignore[return-value]


async def update_contract(
    db: AsyncSession, contract: ProductionContract, payload: ProductionContractUpdate
) -> ProductionContract:
    for k, v in payload.model_dump(exclude_unset=True, exclude={"material_supplies"}).items():
        setattr(contract, k, v)
    if payload.material_supplies is not None:
        for row in list(contract.material_supplies):
            await db.delete(row)
        await db.flush()
        for supply in payload.material_supplies:
            db.add(CmtMaterialSupply(contract_id=contract.id, **supply.model_dump()))
    await db.flush()
    return await get_contract(db, contract.id)  # type: ignore[return-value]


async def get_cmt_supply_for_item(
    db: AsyncSession, contract_id: int, manufacturing_item_id: int
) -> CmtMaterialSupply | None:
    result = await db.execute(
        select(CmtMaterialSupply).where(
            CmtMaterialSupply.contract_id == contract_id,
            CmtMaterialSupply.manufacturing_item_id == manufacturing_item_id,
        ),
    )
    return result.scalar_one_or_none()


# --- Sewing lines ---


async def list_sewing_lines(db: AsyncSession) -> list[SewingLine]:
    result = await db.execute(select(SewingLine).order_by(SewingLine.code))
    return list(result.scalars().all())


async def create_sewing_line(db: AsyncSession, payload: SewingLineCreate) -> SewingLine:
    line = SewingLine(**payload.model_dump())
    db.add(line)
    await db.flush()
    await db.refresh(line)
    return line


# --- Production plans ---


async def list_production_plans(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> tuple[list[ProductionPlan], int]:
    q = select(ProductionPlan).options(*_plan_load_options())
    total = (await db.execute(select(func.count()).select_from(ProductionPlan))).scalar_one() or 0
    result = await db.execute(q.order_by(ProductionPlan.id.desc()).offset(skip).limit(limit))
    return list(result.scalars().unique().all()), total


async def get_production_plan(db: AsyncSession, plan_id: int) -> ProductionPlan | None:
    result = await db.execute(
        select(ProductionPlan).where(ProductionPlan.id == plan_id).options(*_plan_load_options()),
    )
    return result.scalar_one_or_none()


async def create_production_plan(
    db: AsyncSession,
    payload: ProductionPlanCreate,
    *,
    created_by_id: int | None,
) -> ProductionPlan:
    number = payload.plan_number or await _next_plan_number(db)
    plan = ProductionPlan(
        plan_number=number,
        sales_order_id=payload.sales_order_id,
        style_template_id=payload.style_template_id,
        contract_id=payload.contract_id,
        bom_parent_item_id=payload.bom_parent_item_id,
        routing_id=payload.routing_id,
        target_ship_date=payload.target_ship_date,
        planning_horizon_days=payload.planning_horizon_days,
        notes=payload.notes,
        created_by_id=created_by_id,
    )
    db.add(plan)
    await db.flush()
    for line_in in payload.lines:
        db.add(ProductionPlanLine(production_plan_id=plan.id, **line_in.model_dump()))
    await db.flush()
    return await get_production_plan(db, plan.id)  # type: ignore[return-value]


async def update_production_plan(
    db: AsyncSession, plan: ProductionPlan, payload: ProductionPlanUpdate
) -> ProductionPlan:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.flush()
    return await get_production_plan(db, plan.id)  # type: ignore[return-value]


async def add_plan_lines(
    db: AsyncSession, plan: ProductionPlan, lines: list[ProductionPlanLineIn]
) -> ProductionPlan:
    for line_in in lines:
        db.add(ProductionPlanLine(production_plan_id=plan.id, **line_in.model_dump()))
    await db.flush()
    return await get_production_plan(db, plan.id)  # type: ignore[return-value]


async def replace_plan_schedules(
    db: AsyncSession,
    plan: ProductionPlan,
    schedules: list[ProductionPlanSchedule],
) -> None:
    for s in list(plan.schedules):
        await db.delete(s)
    await db.flush()
    for s in schedules:
        db.add(s)


# --- Cut orders ---


async def list_cut_orders(
    db: AsyncSession, *, plan_id: int | None = None, skip: int = 0, limit: int = 100
) -> tuple[list[CutOrder], int]:
    q = select(CutOrder).options(*_cut_order_load_options())
    count_q = select(func.count()).select_from(CutOrder)
    if plan_id is not None:
        q = q.where(CutOrder.production_plan_id == plan_id)
        count_q = count_q.where(CutOrder.production_plan_id == plan_id)
    total = (await db.execute(count_q)).scalar_one() or 0
    result = await db.execute(q.order_by(CutOrder.id.desc()).offset(skip).limit(limit))
    return list(result.scalars().unique().all()), total


async def get_cut_order(db: AsyncSession, cut_order_id: int) -> CutOrder | None:
    result = await db.execute(
        select(CutOrder).where(CutOrder.id == cut_order_id).options(*_cut_order_load_options()),
    )
    return result.scalar_one_or_none()


async def create_cut_order(db: AsyncSession, payload: CutOrderCreate) -> CutOrder:
    number = payload.cut_order_number or await _next_cut_order_number(db)
    co = CutOrder(
        cut_order_number=number,
        production_plan_id=payload.production_plan_id,
        fabric_item_id=payload.fabric_item_id,
        cutting_date=payload.cutting_date,
        priority=payload.priority,
        marker_ref=payload.marker_ref,
        marker_length=payload.marker_length,
        marker_width=payload.marker_width,
        efficiency_pct=payload.efficiency_pct,
        plies=payload.plies,
        notes=payload.notes,
    )
    db.add(co)
    await db.flush()
    for bd in payload.size_breakdowns:
        db.add(CutOrderSizeBreakdown(cut_order_id=co.id, **bd.model_dump()))
    for fa in payload.fabric_allocations:
        fa_data = fa.model_dump()
        if fa.material_roll_id is not None:
            from app.models.material_roll import MaterialRoll

            roll = await db.get(MaterialRoll, fa.material_roll_id)
            if roll is None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"Material roll {fa.material_roll_id} not found",
                )
            if fa.meters_allocated > roll.remaining_quantity:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"Roll {roll.roll_number} has only {roll.remaining_quantity} available",
                )
            fa_data["roll_lot_ref"] = roll.roll_number
        db.add(CutOrderFabricAllocation(cut_order_id=co.id, **fa_data))
    await db.flush()
    return await get_cut_order(db, co.id)  # type: ignore[return-value]


async def update_cut_order(db: AsyncSession, co: CutOrder, payload: CutOrderUpdate) -> CutOrder:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(co, k, v)
    await db.flush()
    return await get_cut_order(db, co.id)  # type: ignore[return-value]


# --- Line balance sessions ---


async def get_line_balance_session(db: AsyncSession, session_id: int) -> LineBalanceSession | None:
    result = await db.execute(
        select(LineBalanceSession)
        .where(LineBalanceSession.id == session_id)
        .options(selectinload(LineBalanceSession.assignments)),
    )
    return result.scalar_one_or_none()


async def save_line_balance_session(
    db: AsyncSession,
    session: LineBalanceSession,
    assignments: list[LineBalanceAssignment],
) -> LineBalanceSession:
    db.add(session)
    await db.flush()
    for a in assignments:
        a.session_id = session.id
        db.add(a)
    await db.flush()
    return await get_line_balance_session(db, session.id)  # type: ignore[return-value]


async def update_line_balance_assignment(
    db: AsyncSession, assignment: LineBalanceAssignment, station_no: int, operator_ref: str | None
) -> LineBalanceAssignment:
    assignment.station_no = station_no
    assignment.operator_ref = operator_ref
    await db.flush()
    return assignment
