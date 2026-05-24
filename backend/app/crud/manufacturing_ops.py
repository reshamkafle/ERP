from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.manufacturing import BOMAlternate, BOMSubstitute
from app.models.manufacturing_ops import (
    EngineeringChange,
    InspectionCharacteristic,
    InspectionResult,
    MasterProductionSchedule,
    MrpForecast,
    MrpPlannedOrder,
    MrpRun,
    MpsLine,
    NonConformance,
    ProductionCalendar,
    ProductionOrder,
    ProductionOrderOperation,
    ProductionVersion,
    QualityInspectionPlan,
    Routing,
    RoutingOperation,
    ToolingAsset,
    WorkCenter,
)
from app.models.product import Product
from app.schemas.manufacturing import (
    BomConfigurationCreate,
    BOMAlternateIn,
    BOMSubstituteIn,
    EngineeringChangeCreate,
    MrpForecastCreate,
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionVersionCreate,
    QualityPlanCreate,
    RoutingCreate,
    RoutingUpdate,
    ToolingAssetCreate,
    WorkCenterCreate,
    WorkCenterUpdate,
)
from app.models.manufacturing_ops import BomConfiguration


async def list_work_centers(db: AsyncSession) -> list[WorkCenter]:
    result = await db.execute(select(WorkCenter).order_by(WorkCenter.code))
    return list(result.scalars().all())


async def get_work_center(db: AsyncSession, wc_id: int) -> WorkCenter | None:
    return await db.get(WorkCenter, wc_id)


async def create_work_center(db: AsyncSession, payload: WorkCenterCreate) -> WorkCenter:
    wc = WorkCenter(**payload.model_dump())
    db.add(wc)
    await db.flush()
    await db.refresh(wc)
    return wc


async def update_work_center(
    db: AsyncSession, wc: WorkCenter, payload: WorkCenterUpdate
) -> WorkCenter:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(wc, k, v)
    await db.flush()
    await db.refresh(wc)
    return wc


async def list_routings(db: AsyncSession) -> list[Routing]:
    result = await db.execute(
        select(Routing)
        .options(selectinload(Routing.operations))
        .order_by(Routing.code),
    )
    return list(result.scalars().unique().all())


async def get_routing(db: AsyncSession, routing_id: int) -> Routing | None:
    result = await db.execute(
        select(Routing)
        .where(Routing.id == routing_id)
        .options(selectinload(Routing.operations)),
    )
    return result.scalar_one_or_none()


async def create_routing(db: AsyncSession, payload: RoutingCreate) -> Routing:
    routing = Routing(
        code=payload.code,
        name=payload.name,
        description=payload.description,
        parent_item_id=payload.parent_item_id,
        is_active=payload.is_active,
    )
    db.add(routing)
    await db.flush()
    for op_in in payload.operations:
        db.add(RoutingOperation(routing_id=routing.id, **op_in.model_dump()))
    await db.flush()
    return await get_routing(db, routing.id)  # type: ignore[return-value]


async def update_routing(db: AsyncSession, routing: Routing, payload: RoutingUpdate) -> Routing:
    for k, v in payload.model_dump(exclude_unset=True, exclude={"operations"}).items():
        setattr(routing, k, v)
    if payload.operations is not None:
        for op in list(routing.operations):
            await db.delete(op)
        await db.flush()
        for op_in in payload.operations:
            db.add(RoutingOperation(routing_id=routing.id, **op_in.model_dump()))
    await db.flush()
    return await get_routing(db, routing.id)  # type: ignore[return-value]


async def list_production_versions(db: AsyncSession, product_id: int | None = None) -> list[ProductionVersion]:
    q = select(ProductionVersion)
    if product_id:
        q = q.where(ProductionVersion.product_id == product_id)
    result = await db.execute(q.order_by(ProductionVersion.version_code))
    return list(result.scalars().all())


async def create_production_version(db: AsyncSession, payload: ProductionVersionCreate) -> ProductionVersion:
    pv = ProductionVersion(**payload.model_dump())
    db.add(pv)
    await db.flush()
    await db.refresh(pv)
    return pv


async def _next_po_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"MO-{year}-"
    result = await db.execute(
        select(func.count()).select_from(ProductionOrder).where(
            ProductionOrder.order_number.like(f"{prefix}%"),
        ),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:06d}"


async def list_production_orders(
    db: AsyncSession,
    *,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[ProductionOrder], int]:
    q = select(ProductionOrder).options(
        selectinload(ProductionOrder.operations),
        selectinload(ProductionOrder.product),
    )
    if status:
        q = q.where(ProductionOrder.status == status)
    count_q = select(func.count()).select_from(ProductionOrder)
    if status:
        count_q = count_q.where(ProductionOrder.status == status)
    total = (await db.execute(count_q)).scalar_one() or 0
    result = await db.execute(q.order_by(ProductionOrder.id.desc()).offset(skip).limit(limit))
    return list(result.scalars().unique().all()), total


async def get_production_order(db: AsyncSession, po_id: int) -> ProductionOrder | None:
    result = await db.execute(
        select(ProductionOrder)
        .where(ProductionOrder.id == po_id)
        .options(
            selectinload(ProductionOrder.operations),
            selectinload(ProductionOrder.product),
            selectinload(ProductionOrder.material_issues),
            selectinload(ProductionOrder.confirmations),
            selectinload(ProductionOrder.shop_floor_entries),
        ),
    )
    return result.scalar_one_or_none()


async def create_production_order(
    db: AsyncSession,
    payload: ProductionOrderCreate,
    *,
    created_by_id: int | None,
) -> ProductionOrder:
    order_number = payload.order_number or await _next_po_number(db)
    data = payload.model_dump(exclude={"order_number"})
    po = ProductionOrder(order_number=order_number, created_by_id=created_by_id, **data)
    db.add(po)
    await db.flush()
    if payload.routing_id:
        routing = await get_routing(db, payload.routing_id)
        if routing:
            for rop in routing.operations:
                db.add(
                    ProductionOrderOperation(
                        production_order_id=po.id,
                        routing_operation_id=rop.id,
                        sequence=rop.sequence,
                        operation_name=rop.operation_name,
                        work_center_id=rop.work_center_id,
                        setup_time_minutes=rop.setup_time_minutes,
                        run_time_minutes=rop.run_time_minutes,
                    ),
                )
    await db.flush()
    return await get_production_order(db, po.id)  # type: ignore[return-value]


async def update_production_order(
    db: AsyncSession, po: ProductionOrder, payload: ProductionOrderUpdate
) -> ProductionOrder:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(po, k, v)
    await db.flush()
    return await get_production_order(db, po.id)  # type: ignore[return-value]


async def add_bom_alternate(db: AsyncSession, parent_item_id: int, payload: BOMAlternateIn) -> BOMAlternate:
    alt = BOMAlternate(parent_item_id=parent_item_id, **payload.model_dump())
    db.add(alt)
    await db.flush()
    await db.refresh(alt)
    return alt


async def add_bom_substitute(db: AsyncSession, bom_line_id: int, payload: BOMSubstituteIn) -> BOMSubstitute:
    sub = BOMSubstitute(bom_line_id=bom_line_id, **payload.model_dump())
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return sub


async def create_quality_plan(db: AsyncSession, payload: QualityPlanCreate) -> QualityInspectionPlan:
    plan = QualityInspectionPlan(
        code=payload.code,
        name=payload.name,
        stage=payload.stage,
        product_id=payload.product_id,
        production_order_id=payload.production_order_id,
    )
    db.add(plan)
    await db.flush()
    for ch in payload.characteristics:
        db.add(InspectionCharacteristic(plan_id=plan.id, **ch.model_dump()))
    await db.flush()
    await db.refresh(plan)
    return plan


async def list_quality_plans(db: AsyncSession) -> list[QualityInspectionPlan]:
    result = await db.execute(select(QualityInspectionPlan).order_by(QualityInspectionPlan.code))
    return list(result.scalars().all())


async def create_mrp_forecast(db: AsyncSession, payload: MrpForecastCreate) -> MrpForecast:
    fc = MrpForecast(**payload.model_dump())
    db.add(fc)
    await db.flush()
    await db.refresh(fc)
    return fc


async def list_mrp_forecasts(db: AsyncSession) -> list[MrpForecast]:
    result = await db.execute(select(MrpForecast).order_by(MrpForecast.forecast_date))
    return list(result.scalars().all())


async def get_mrp_run(db: AsyncSession, run_id: int) -> MrpRun | None:
    result = await db.execute(
        select(MrpRun)
        .where(MrpRun.id == run_id)
        .options(selectinload(MrpRun.planned_orders)),
    )
    return result.scalar_one_or_none()


async def create_engineering_change(db: AsyncSession, payload: EngineeringChangeCreate) -> EngineeringChange:
    ec = EngineeringChange(**payload.model_dump())
    db.add(ec)
    await db.flush()
    await db.refresh(ec)
    return ec


async def create_tooling_asset(db: AsyncSession, payload: ToolingAssetCreate) -> ToolingAsset:
    asset = ToolingAsset(**payload.model_dump())
    db.add(asset)
    await db.flush()
    await db.refresh(asset)
    return asset


async def create_bom_configuration(db: AsyncSession, payload: BomConfigurationCreate) -> BomConfiguration:
    cfg = BomConfiguration(**payload.model_dump())
    db.add(cfg)
    await db.flush()
    await db.refresh(cfg)
    return cfg


async def list_calendars(db: AsyncSession) -> list[ProductionCalendar]:
    result = await db.execute(select(ProductionCalendar).order_by(ProductionCalendar.code))
    return list(result.scalars().all())
