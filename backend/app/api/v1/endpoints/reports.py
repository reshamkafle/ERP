from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import report as report_crud
from app.dependencies.auth import require_roles
from app.models.user import User, UserRole
from app.schemas.report import (
    SalesReportResponse,
    StockValueReportResponse,
    TopProductsReportResponse,
)

router = APIRouter(prefix="/reports")


@router.get("/sales", response_model=SalesReportResponse)
async def sales_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
    period: Literal["today", "week"] = Query(default="today"),
) -> SalesReportResponse:
    return await report_crud.get_sales_report(db, period=period)


@router.get("/top-products", response_model=TopProductsReportResponse)
async def top_products_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
) -> TopProductsReportResponse:
    return await report_crud.get_top_products_report(db)


@router.get("/stock-value", response_model=StockValueReportResponse)
async def stock_value_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
) -> StockValueReportResponse:
    return await report_crud.get_stock_value_report(db)
