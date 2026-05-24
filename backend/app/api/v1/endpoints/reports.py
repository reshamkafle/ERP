from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import report as report_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.report import (
    FinanceSummaryReportResponse,
    InventoryPerformanceReportResponse,
    ItOverviewReportResponse,
    MarketingFunnelReportResponse,
    PurchaseOrdersReportResponse,
    SalesReportResponse,
    StockValueReportResponse,
    TopProductsReportResponse,
)

router = APIRouter(prefix="/reports")

_REPORT_READ = (
    "reports.reports.read",
    "reports.manager.read",
)
_MERCH_READ = ("reports.merchandiser.read", *_REPORT_READ)
_FINANCE_READ = ("reports.finance.read", *_REPORT_READ)
_MARKETING_READ = ("reports.marketing.read", *_REPORT_READ)
_WAREHOUSE_READ = ("reports.warehouse.read", *_REPORT_READ)
_IT_READ = ("reports.it.read", *_REPORT_READ)


@router.get("/sales", response_model=SalesReportResponse)
async def sales_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_MERCH_READ))],
    period: Literal["today", "week", "month"] = Query(default="today"),
) -> SalesReportResponse:
    return await report_crud.get_sales_report(db, period=period)


@router.get("/top-products", response_model=TopProductsReportResponse)
async def top_products_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_MERCH_READ))],
) -> TopProductsReportResponse:
    return await report_crud.get_top_products_report(db)


@router.get("/stock-value", response_model=StockValueReportResponse)
async def stock_value_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_WAREHOUSE_READ, "reports.merchandiser.read"))],
) -> StockValueReportResponse:
    return await report_crud.get_stock_value_report(db)


@router.get("/purchase-orders", response_model=PurchaseOrdersReportResponse)
async def purchase_orders_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_MERCH_READ))],
    period: Literal["today", "week", "month"] = Query(default="week"),
) -> PurchaseOrdersReportResponse:
    return await report_crud.get_purchase_orders_report(db, period=period)


@router.get("/inventory-performance", response_model=InventoryPerformanceReportResponse)
async def inventory_performance_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_WAREHOUSE_READ, "reports.merchandiser.read"))],
) -> InventoryPerformanceReportResponse:
    return await report_crud.get_inventory_performance_report(db)


@router.get("/finance-summary", response_model=FinanceSummaryReportResponse)
async def finance_summary_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_FINANCE_READ))],
    period: Literal["week", "month"] = Query(default="week"),
) -> FinanceSummaryReportResponse:
    return await report_crud.get_finance_summary_report(db, period=period)


@router.get("/marketing-funnel", response_model=MarketingFunnelReportResponse)
async def marketing_funnel_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_MARKETING_READ))],
) -> MarketingFunnelReportResponse:
    return await report_crud.get_marketing_funnel_report(db)


@router.get("/it-overview", response_model=ItOverviewReportResponse)
async def it_overview_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission(*_IT_READ))],
) -> ItOverviewReportResponse:
    return await report_crud.get_it_overview_report(db)
