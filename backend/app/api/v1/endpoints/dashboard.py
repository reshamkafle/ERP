from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_permission
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DocumentFlowMetricsResponse, ManagerOverviewResponse
from app.services.dashboard_flow_metrics import build_document_flow_metrics
from app.services.manager_overview import build_manager_overview
from app.services.permission_service import get_user_permissions

router = APIRouter(prefix="/dashboard")


@router.get("/summary")
async def dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("reports.dashboard.read"))],
) -> dict[str, str | int]:
    low_stock_count = (
        await db.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.stock < Product.low_stock_threshold),
        )
    ).scalar_one()
    return {
        "heading": "Today at a glance",
        "low_stock_count": low_stock_count,
        "open_pos_sessions": 0,
    }


@router.get("/document-flow-metrics", response_model=DocumentFlowMetricsResponse)
async def document_flow_metrics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("reports.dashboard.read"))],
    period: str = Query("week", pattern="^(today|week)$"),
    new_days: int = Query(30, ge=1, le=365),
) -> DocumentFlowMetricsResponse:
    user_codes = await get_user_permissions(db, current)
    return await build_document_flow_metrics(
        db,
        user_codes=user_codes,
        period=period,
        new_days=new_days,
    )


@router.get("/manager-overview", response_model=ManagerOverviewResponse)
async def manager_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("reports.manager.read", "reports.dashboard.read"))],
    period: Literal["today", "week", "month"] = Query(default="week"),
) -> ManagerOverviewResponse:
    return await build_manager_overview(db, period=period)
