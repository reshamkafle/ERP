"""Integration tests for role-scoped ERP reports."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud import report as report_crud
from app.main import app
from app.services.manager_overview import build_manager_overview
from tests.test_access_users import _user_with_permissions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_sales_report_supports_month_period(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_sales_report(seeded_db, period="month")
    assert report.period == "month"
    assert report.sale_count >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_purchase_orders_report(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_purchase_orders_report(seeded_db, period="week")
    assert report.period == "week"
    assert report.po_count >= 0
    assert report.open_po_count >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_inventory_performance_report(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_inventory_performance_report(seeded_db)
    assert report.low_stock_count >= 0
    assert report.total_stock_value >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_finance_summary_report(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_finance_summary_report(seeded_db, period="week")
    assert report.period == "week"
    assert report.ap_outstanding >= 0
    assert report.ar_outstanding >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_marketing_funnel_report(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_marketing_funnel_report(seeded_db)
    assert report.total_leads >= 0
    assert report.total_customers >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_it_overview_report(seeded_db: AsyncSession) -> None:
    report = await report_crud.get_it_overview_report(seeded_db)
    assert report.api_status == "ok"
    assert report.db_status == "ok"
    assert report.active_user_count >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_manager_overview(seeded_db: AsyncSession) -> None:
    overview = await build_manager_overview(seeded_db, period="week")
    assert overview.period == "week"
    assert overview.total_revenue >= 0
    assert overview.low_stock_count >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_warehouse_user_can_access_inventory_report(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    user = await _user_with_permissions(
        seeded_db,
        email=f"warehouse-reports-{suffix}@test.local",
        permission_codes=["reports.warehouse.read"],
    )
    await seeded_db.commit()

    token = create_access_token(str(user.id), role=user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        allowed = await client.get(
            "/api/v1/reports/inventory-performance",
            headers={"Authorization": f"Bearer {token}"},
        )
        denied = await client.get(
            "/api/v1/reports/finance-summary",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert allowed.status_code == 200
    assert denied.status_code == 403


@pytest.mark.asyncio
@pytest.mark.integration
async def test_finance_user_can_access_finance_report(seeded_db: AsyncSession) -> None:
    suffix = uuid.uuid4().hex[:8]
    user = await _user_with_permissions(
        seeded_db,
        email=f"finance-reports-{suffix}@test.local",
        permission_codes=["reports.finance.read"],
    )
    await seeded_db.commit()

    token = create_access_token(str(user.id), role=user.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            "/api/v1/reports/finance-summary",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert res.status_code == 200
    body = res.json()
    assert "payments_in" in body
    assert "gross_margin_pct" in body
