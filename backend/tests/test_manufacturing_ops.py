"""Manufacturing operations tests."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import manufacturing_ops as mfg_crud
from app.models.enums import ProductionOrderStatus
from app.models.product import Product
from app.schemas.manufacturing import ProductionOrderCreate, WorkCenterCreate
from app.services.production_order_service import release_production_order, start_production_order
from app.services.mrp_service import run_mrp
from app.schemas.manufacturing import MrpRunCreate


@pytest.mark.asyncio
async def test_work_center_create(seeded_db: AsyncSession) -> None:
    wc = await mfg_crud.create_work_center(
        seeded_db,
        WorkCenterCreate(code="WC-T01", name="Test WC"),
    )
    await seeded_db.commit()
    assert wc.id is not None
    items = await mfg_crud.list_work_centers(seeded_db)
    assert any(i.code == "WC-T01" for i in items)


@pytest.mark.asyncio
async def test_production_order_lifecycle(seeded_db: AsyncSession) -> None:
    from sqlalchemy import select

    result = await seeded_db.execute(select(Product).limit(1))
    product = result.scalar_one_or_none()
    if product is None:
        pytest.skip("No product in seed data")

    po = await mfg_crud.create_production_order(
        seeded_db,
        ProductionOrderCreate(product_id=product.id, quantity_planned=Decimal("10")),
        created_by_id=1,
    )
    await seeded_db.commit()
    po = await mfg_crud.get_production_order(seeded_db, po.id)
    assert po is not None
    assert po.status == ProductionOrderStatus.PLANNED

    await release_production_order(seeded_db, po)
    await start_production_order(seeded_db, po)
    await seeded_db.commit()
    po = await mfg_crud.get_production_order(seeded_db, po.id)
    assert po is not None
    assert po.status == ProductionOrderStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_mrp_run_completes(seeded_db: AsyncSession) -> None:
    from sqlalchemy import select

    result = await seeded_db.execute(select(Product).limit(1))
    product = result.scalar_one_or_none()
    if product is None:
        pytest.skip("No product in seed data")

    from app.schemas.manufacturing import MrpForecastCreate

    from datetime import date

    await mfg_crud.create_mrp_forecast(
        seeded_db,
        MrpForecastCreate(
            product_id=product.id,
            forecast_date=date.today(),
            quantity=Decimal("5"),
        ),
    )
    await seeded_db.flush()

    run = await run_mrp(
        seeded_db,
        MrpRunCreate(horizon_days=30, include_sales=False, include_forecasts=True),
        user_id=1,
    )
    await seeded_db.commit()
    assert run.status.value == "COMPLETED"
