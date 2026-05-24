"""Manufacturing operations API."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import manufacturing_ops as mfg_crud
from app.dependencies.auth import require_permission
from app.models.manufacturing_ops import MrpPlannedOrder, ProductionOrder
from app.models.product import Product
from app.models.user import User
from app.schemas.manufacturing import (
    ProductionOrderOperationRead,
    BomConfigurationCreate,
    BOMAlternateIn,
    BOMSubstituteIn,
    CapacityLoadItem,
    EngineeringChangeCreate,
    InspectionResultIn,
    MaterialIssueIn,
    MrpForecastCreate,
    MrpForecastRead,
    MrpRunCreate,
    MrpRunRead,
    NonConformanceCreate,
    ProductionConfirmationIn,
    ProductionOrderCreate,
    ProductionOrderListResponse,
    ProductionOrderRead,
    ProductionOrderUpdate,
    ProductionReportMetrics,
    ProductionVersionCreate,
    ProductionVersionRead,
    QualityPlanCreate,
    QualityPlanRead,
    RoutingCreate,
    RoutingRead,
    RoutingUpdate,
    ShopFloorEntryIn,
    StandardCostRead,
    ToolingAssetCreate,
    TraceabilityLine,
    WorkCenterCreate,
    WorkCenterRead,
    WorkCenterUpdate,
)
from app.services.mrp_service import firm_planned_order, rough_cut_capacity, run_mrp
from app.services.production_costing import production_report_metrics, rollup_standard_cost
from app.services.production_order_service import (
    close_production_order,
    complete_production_order,
    confirm_production,
    issue_material,
    record_shop_floor,
    release_production_order,
    start_production_order,
)
from app.services.quality_coa_service import (
    create_non_conformance,
    generate_coa_document,
    record_inspection_result,
)

router = APIRouter(prefix="/manufacturing")

MfgRead = require_permission("manufacturing.ops.read", "manufacturing.master.read")
MfgWrite = require_permission("manufacturing.ops.write", "manufacturing.master.write")


def _po_to_read(po: ProductionOrder) -> ProductionOrderRead:
    product = po.product
    return ProductionOrderRead(
        id=po.id,
        order_number=po.order_number,
        status=po.status,
        priority=po.priority,
        product_id=po.product_id,
        quantity_planned=po.quantity_planned,
        quantity_completed=po.quantity_completed,
        quantity_scrapped=po.quantity_scrapped,
        quantity_rework=po.quantity_rework,
        start_date=po.start_date,
        end_date=po.end_date,
        bom_parent_item_id=po.bom_parent_item_id,
        routing_id=po.routing_id,
        production_version_id=po.production_version_id,
        sales_order_id=po.sales_order_id,
        warehouse_id=po.warehouse_id,
        wip_warehouse_id=po.wip_warehouse_id,
        creation_source=po.creation_source,
        production_plan_id=po.production_plan_id,
        contract_id=po.contract_id,
        production_phase=po.production_phase,
        notes=po.notes,
        created_at=po.created_at,
        updated_at=po.updated_at,
        product_name=product.name if product else None,
        product_sku=product.sku if product else None,
        operations=[
            ProductionOrderOperationRead.model_validate(op) for op in (po.operations or [])
        ],
    )


# --- Work centers ---


@router.get("/work-centers", response_model=list[WorkCenterRead])
async def list_work_centers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    items = await mfg_crud.list_work_centers(db)
    return [WorkCenterRead.model_validate(i) for i in items]


@router.post("/work-centers", response_model=WorkCenterRead, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    payload: WorkCenterCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    wc = await mfg_crud.create_work_center(db, payload)
    await db.commit()
    return WorkCenterRead.model_validate(wc)


@router.patch("/work-centers/{wc_id}", response_model=WorkCenterRead)
async def update_work_center(
    wc_id: int,
    payload: WorkCenterUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    wc = await mfg_crud.get_work_center(db, wc_id)
    if wc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Work center not found")
    wc = await mfg_crud.update_work_center(db, wc, payload)
    await db.commit()
    return WorkCenterRead.model_validate(wc)


# --- Routings ---


@router.get("/routings", response_model=list[RoutingRead])
async def list_routings(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    items = await mfg_crud.list_routings(db)
    return [RoutingRead.model_validate(i) for i in items]


@router.post("/routings", response_model=RoutingRead, status_code=status.HTTP_201_CREATED)
async def create_routing(
    payload: RoutingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    routing = await mfg_crud.create_routing(db, payload)
    await db.commit()
    return RoutingRead.model_validate(routing)


@router.get("/routings/{routing_id}", response_model=RoutingRead)
async def get_routing(
    routing_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    routing = await mfg_crud.get_routing(db, routing_id)
    if routing is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Routing not found")
    return RoutingRead.model_validate(routing)


@router.patch("/routings/{routing_id}", response_model=RoutingRead)
async def update_routing(
    routing_id: int,
    payload: RoutingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    routing = await mfg_crud.get_routing(db, routing_id)
    if routing is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Routing not found")
    routing = await mfg_crud.update_routing(db, routing, payload)
    await db.commit()
    return RoutingRead.model_validate(routing)


# --- Production versions ---


@router.get("/production-versions", response_model=list[ProductionVersionRead])
async def list_production_versions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
    product_id: int | None = None,
):
    items = await mfg_crud.list_production_versions(db, product_id)
    return [ProductionVersionRead.model_validate(i) for i in items]


@router.post("/production-versions", response_model=ProductionVersionRead, status_code=201)
async def create_production_version(
    payload: ProductionVersionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    pv = await mfg_crud.create_production_version(db, payload)
    await db.commit()
    return ProductionVersionRead.model_validate(pv)


# --- Production orders ---


@router.get("/production-orders", response_model=ProductionOrderListResponse)
async def list_production_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
    status_filter: str | None = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 100,
):
    items, total = await mfg_crud.list_production_orders(
        db, status=status_filter, skip=skip, limit=limit
    )
    return ProductionOrderListResponse(
        items=[_po_to_read(po) for po in items],
        total=total,
    )


@router.post("/production-orders", response_model=ProductionOrderRead, status_code=201)
async def create_production_order(
    payload: ProductionOrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.create_production_order(db, payload, created_by_id=user.id)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.get("/production-orders/{po_id}", response_model=ProductionOrderRead)
async def get_production_order(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production order not found")
    return _po_to_read(po)


@router.patch("/production-orders/{po_id}", response_model=ProductionOrderRead)
async def update_production_order(
    po_id: int,
    payload: ProductionOrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production order not found")
    po = await mfg_crud.update_production_order(db, po, payload)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/release", response_model=ProductionOrderRead)
async def release_po(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await release_production_order(db, po)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/start", response_model=ProductionOrderRead)
async def start_po(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await start_production_order(db, po)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/issue-material", response_model=ProductionOrderRead)
async def issue_material_endpoint(
    po_id: int,
    payload: MaterialIssueIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await issue_material(db, po, payload, user.id)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/confirm", response_model=ProductionOrderRead)
async def confirm_po(
    po_id: int,
    payload: ProductionConfirmationIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await confirm_production(db, po, payload, user.id)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/shop-floor")
async def shop_floor_entry(
    po_id: int,
    payload: ShopFloorEntryIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    entry = await record_shop_floor(db, po, payload, user.id)
    await db.commit()
    return {"id": entry.id}


@router.post("/production-orders/{po_id}/complete", response_model=ProductionOrderRead)
async def complete_po(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await complete_production_order(db, po)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.post("/production-orders/{po_id}/close", response_model=ProductionOrderRead)
async def close_po(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    po = await close_production_order(db, po, user.id)
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


# --- MRP ---


@router.post("/mrp/runs", response_model=MrpRunRead, status_code=201)
async def create_mrp_run(
    payload: MrpRunCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    run = await run_mrp(db, payload, user.id)
    await db.commit()
    run = await mfg_crud.get_mrp_run(db, run.id)
    return MrpRunRead.model_validate(run)


@router.get("/mrp/runs/{run_id}", response_model=MrpRunRead)
async def get_mrp_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    run = await mfg_crud.get_mrp_run(db, run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return MrpRunRead.model_validate(run)


@router.post("/mrp/planned-orders/{planned_id}/firm", response_model=ProductionOrderRead)
async def firm_planned(
    planned_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    planned = await db.get(MrpPlannedOrder, planned_id)
    if planned is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    try:
        po = await firm_planned_order(db, planned, user.id)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    po = await mfg_crud.get_production_order(db, po.id)
    return _po_to_read(po)  # type: ignore[arg-type]


@router.get("/mrp/forecasts", response_model=list[MrpForecastRead])
async def list_forecasts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    items = await mfg_crud.list_mrp_forecasts(db)
    return [MrpForecastRead.model_validate(i) for i in items]


@router.post("/mrp/forecasts", response_model=MrpForecastRead, status_code=201)
async def create_forecast(
    payload: MrpForecastCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    fc = await mfg_crud.create_mrp_forecast(db, payload)
    await db.commit()
    return MrpForecastRead.model_validate(fc)


@router.get("/capacity/rccp", response_model=list[CapacityLoadItem])
async def capacity_rccp(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    return await rough_cut_capacity(db)


# --- Quality ---


@router.get("/quality/plans", response_model=list[QualityPlanRead])
async def list_quality_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    items = await mfg_crud.list_quality_plans(db)
    return [QualityPlanRead.model_validate(i) for i in items]


@router.post("/quality/plans", response_model=QualityPlanRead, status_code=201)
async def create_quality_plan(
    payload: QualityPlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    plan = await mfg_crud.create_quality_plan(db, payload)
    await db.commit()
    return QualityPlanRead.model_validate(plan)


@router.post("/quality/inspections")
async def record_inspection(
    payload: InspectionResultIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
):
    result = await record_inspection_result(db, payload, user.id)
    await db.commit()
    return {"id": result.id, "passed": result.passed}


@router.post("/quality/non-conformances", status_code=201)
async def create_ncr(
    payload: NonConformanceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    ncr = await create_non_conformance(db, payload)
    await db.commit()
    return {"id": ncr.id, "reference": ncr.reference}


@router.post("/quality/coa/{plan_id}")
async def generate_coa(
    plan_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(MfgWrite)],
    production_order_id: int | None = None,
):
    doc = await generate_coa_document(
        db,
        plan_id=plan_id,
        production_order_id=production_order_id,
        user_id=user.id,
    )
    await db.commit()
    return {"document_id": doc.id, "reference": doc.reference_number}


# --- Costing & reports ---


@router.post("/costing/standard/{product_id}", response_model=StandardCostRead)
async def calc_standard_cost(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    std = await rollup_standard_cost(db, product_id)
    await db.commit()
    return StandardCostRead.model_validate(std)


@router.get("/reports/metrics", response_model=ProductionReportMetrics)
async def report_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    return await production_report_metrics(db)


@router.get("/reports/traceability/{po_id}", response_model=list[TraceabilityLine])
async def traceability(
    po_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgRead)],
):
    from sqlalchemy.orm import selectinload
    from app.models.manufacturing_ops import ProductionMaterialIssue

    po = await mfg_crud.get_production_order(db, po_id)
    if po is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    lines: list[TraceabilityLine] = []
    for issue in po.material_issues or []:
        comp = issue.component_item
        lines.append(
            TraceabilityLine(
                lot_number=issue.lot_number,
                serial_number=issue.serial_number,
                component_sku=comp.sku if comp else "",
                production_order_number=po.order_number,
                quantity=issue.quantity,
            ),
        )
    return lines


# --- BOM alternates ---


@router.post("/bom/{parent_item_id}/alternates", status_code=201)
async def add_bom_alternate(
    parent_item_id: int,
    payload: BOMAlternateIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    alt = await mfg_crud.add_bom_alternate(db, parent_item_id, payload)
    await db.commit()
    return {"id": alt.id}


@router.post("/bom/lines/{line_id}/substitutes", status_code=201)
async def add_bom_substitute(
    line_id: int,
    payload: BOMSubstituteIn,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    sub = await mfg_crud.add_bom_substitute(db, line_id, payload)
    await db.commit()
    return {"id": sub.id}


# --- Advanced ---


@router.post("/engineering-changes", status_code=201)
async def create_ecn(
    payload: EngineeringChangeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    ec = await mfg_crud.create_engineering_change(db, payload)
    await db.commit()
    return {"id": ec.id, "eco_number": ec.eco_number}


@router.post("/tooling", status_code=201)
async def create_tooling(
    payload: ToolingAssetCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    asset = await mfg_crud.create_tooling_asset(db, payload)
    await db.commit()
    return {"id": asset.id, "code": asset.code}


@router.post("/bom-configurations", status_code=201)
async def create_bom_config(
    payload: BomConfigurationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(MfgWrite)],
):
    cfg = await mfg_crud.create_bom_configuration(db, payload)
    await db.commit()
    return {"id": cfg.id, "code": cfg.code}
