"""Material Requirements Planning — demand collection and planned orders."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.manufacturing.bom.service import BOMService
from app.manufacturing.bom.sql_repository import SqlBOMRepository
from app.models.enums import MrpRunStatus, PlannedOrderType, SaleOrderStatus
from app.models.manufacturing import ManufacturingItem
from app.models.manufacturing_ops import (
    MasterProductionSchedule,
    MrpDemandLine,
    MrpForecast,
    MrpPlannedOrder,
    MrpRun,
    MpsLine,
    ProductionOrder,
    ProductionOrderOperation,
    RoutingOperation,
    WorkCenter,
)
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.manufacturing import CapacityLoadItem, MrpRunCreate, ProductionOrderCreate
from app.crud import manufacturing_ops as mfg_crud
from app.models.enums import ProductionOrderSource, ProductionOrderStatus


async def _next_mrp_run_number(db: AsyncSession) -> str:
    from sqlalchemy import func

    year = datetime.now(timezone.utc).year
    prefix = f"MRP-{year}-"
    from app.models.manufacturing_ops import MrpRun as MrpRunModel

    result = await db.execute(
        select(func.count()).select_from(MrpRunModel).where(MrpRunModel.run_number.like(f"{prefix}%")),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:04d}"


async def collect_demand(
    db: AsyncSession,
    run: MrpRun,
    *,
    include_sales: bool,
    include_forecasts: bool,
) -> list[MrpDemandLine]:
    lines: list[MrpDemandLine] = []
    horizon_end = date.today() + timedelta(days=run.horizon_days)

    if include_sales:
        result = await db.execute(
            select(Sale, SaleItem)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(
                Sale.order_status.in_(
                    [SaleOrderStatus.RELEASED, SaleOrderStatus.IN_PROCESS, SaleOrderStatus.CREATED],
                ),
            ),
        )
        for sale, item in result.all():
            if item.product_id is None:
                continue
            lines.append(
                MrpDemandLine(
                    mrp_run_id=run.id,
                    product_id=item.product_id,
                    demand_date=sale.requested_delivery_date or sale.order_date,
                    quantity=Decimal(str(item.quantity)),
                    source_type="SALES",
                    source_id=sale.id,
                    source_reference=sale.order_number,
                ),
            )

    if include_forecasts:
        fc_result = await db.execute(
            select(MrpForecast).where(MrpForecast.forecast_date <= horizon_end),
        )
        for fc in fc_result.scalars().all():
            lines.append(
                MrpDemandLine(
                    mrp_run_id=run.id,
                    product_id=fc.product_id,
                    demand_date=fc.forecast_date,
                    quantity=fc.quantity,
                    source_type="FORECAST",
                    source_id=fc.id,
                ),
            )

    mps_result = await db.execute(
        select(MpsLine)
        .join(MasterProductionSchedule)
        .where(MasterProductionSchedule.is_active.is_(True)),
    )
    for mps_line in mps_result.scalars().all():
        if mps_line.week_start <= horizon_end:
            lines.append(
                MrpDemandLine(
                    mrp_run_id=run.id,
                    product_id=mps_line.product_id,
                    demand_date=mps_line.week_start,
                    quantity=mps_line.quantity,
                    source_type="MPS",
                    source_id=mps_line.id,
                ),
            )

    for line in lines:
        db.add(line)
    await db.flush()
    return lines


async def run_mrp(db: AsyncSession, payload: MrpRunCreate, user_id: int | None) -> MrpRun:
    run = MrpRun(
        run_number=await _next_mrp_run_number(db),
        status=MrpRunStatus.RUNNING,
        horizon_days=payload.horizon_days,
        parameters=payload.parameters,
        started_at=datetime.now(timezone.utc),
        created_by_id=user_id,
    )
    db.add(run)
    await db.flush()

    demand_lines = await collect_demand(
        db,
        run,
        include_sales=payload.include_sales,
        include_forecasts=payload.include_forecasts,
    )

    bom_svc = BOMService(SqlBOMRepository(db))
    planned: list[MrpPlannedOrder] = []

    for dline in demand_lines:
        if dline.product_id is None:
            continue
        product = await db.get(Product, dline.product_id)
        if product is None:
            continue
        mfg_result = await db.execute(
            select(ManufacturingItem).where(ManufacturingItem.product_id == product.id),
        )
        mfg_item = mfg_result.scalar_one_or_none()
        order_type = PlannedOrderType.MAKE if mfg_item else PlannedOrderType.BUY
        start = dline.demand_date - timedelta(days=7)
        po = MrpPlannedOrder(
            mrp_run_id=run.id,
            order_type=order_type,
            product_id=product.id,
            manufacturing_item_id=mfg_item.id if mfg_item else None,
            quantity=dline.quantity,
            planned_start_date=start,
            planned_end_date=dline.demand_date,
            pegged_demand_line_id=dline.id,
        )
        db.add(po)
        planned.append(po)

        if mfg_item and order_type == PlannedOrderType.MAKE:
            try:
                explosion = await bom_svc.explode_bom(
                    mfg_item.sku,
                    order_quantity=int(dline.quantity),
                )
                for eline in explosion.lines:
                    comp_mfg = await db.get(ManufacturingItem, eline.item_id)
                    if comp_mfg and comp_mfg.product_id:
                        from app.services.cmt_service import is_buyer_supplied_item

                        if await is_buyer_supplied_item(db, comp_mfg.id):
                            continue
                        db.add(
                            MrpPlannedOrder(
                                mrp_run_id=run.id,
                                order_type=PlannedOrderType.BUY,
                                product_id=comp_mfg.product_id,
                                manufacturing_item_id=comp_mfg.id,
                                quantity=eline.total_qty,
                                planned_start_date=start - timedelta(days=eline.item_id % 5 + 1),
                                planned_end_date=start,
                                pegged_demand_line_id=dline.id,
                            ),
                        )
            except Exception:
                pass

    run.status = MrpRunStatus.COMPLETED
    run.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return await mfg_crud.get_mrp_run(db, run.id)  # type: ignore[return-value]


async def firm_planned_order(
    db: AsyncSession,
    planned: MrpPlannedOrder,
    user_id: int | None,
) -> ProductionOrder:
    if planned.is_firmed:
        po = await db.get(ProductionOrder, planned.production_order_id)
        if po:
            return po
    if planned.order_type != PlannedOrderType.MAKE or planned.product_id is None:
        raise ValueError("Only MAKE planned orders can be firmed to production orders")

    mfg_item_id = planned.manufacturing_item_id
    create_payload = ProductionOrderCreate(
        product_id=planned.product_id,
        quantity_planned=planned.quantity,
        start_date=planned.planned_start_date,
        end_date=planned.planned_end_date,
        bom_parent_item_id=mfg_item_id,
        creation_source=ProductionOrderSource.MRP,
    )
    po = await mfg_crud.create_production_order(db, create_payload, created_by_id=user_id)
    planned.is_firmed = True
    planned.production_order_id = po.id
    await db.flush()
    return po


async def rough_cut_capacity(db: AsyncSession) -> list[CapacityLoadItem]:
    wc_result = await db.execute(select(WorkCenter).where(WorkCenter.is_active.is_(True)))
    work_centers = list(wc_result.scalars().all())
    loads: list[CapacityLoadItem] = []

    po_result = await db.execute(
        select(ProductionOrder)
        .where(
            ProductionOrder.status.in_(
                [
                    ProductionOrderStatus.RELEASED,
                    ProductionOrderStatus.IN_PROGRESS,
                    ProductionOrderStatus.PLANNED,
                ],
            ),
        )
        .options(selectinload(ProductionOrder.operations)),
    )
    orders = list(po_result.scalars().unique().all())

    required_by_wc: dict[int, Decimal] = {}
    for po in orders:
        qty = po.quantity_planned
        for op in po.operations:
            if op.work_center_id:
                hours = (op.setup_time_minutes + op.run_time_minutes * qty) / Decimal("60")
                required_by_wc[op.work_center_id] = required_by_wc.get(op.work_center_id, Decimal("0")) + hours

    for wc in work_centers:
        available = wc.capacity_hrs_per_shift * (wc.efficiency_pct / Decimal("100"))
        required = required_by_wc.get(wc.id, Decimal("0"))
        util = (required / available * Decimal("100")) if available > 0 else Decimal("0")
        loads.append(
            CapacityLoadItem(
                work_center_id=wc.id,
                work_center_code=wc.code,
                required_hours=required,
                available_hours=available,
                utilization_pct=util,
            ),
        )
    return loads
