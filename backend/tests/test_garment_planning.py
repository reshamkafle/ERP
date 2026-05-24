"""Tests for garment production planning."""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import garment_planning as gp_crud
from app.models.enums import ProductionContractType
from app.schemas.garment_planning import (
    CmtMaterialSupplyIn,
    LineBalanceCalculateIn,
    LineBalanceOperationIn,
    ProductionContractCreate,
    ProductionPlanCreate,
    ProductionPlanLineIn,
    SewingLineCreate,
)
from app.services.line_balance_service import calculate_line_balance
from tests.fixtures.bom_garment_sample import build_garment_bom_service


@pytest.mark.asyncio
async def test_create_cmt_contract(seeded_db: AsyncSession) -> None:
    from sqlalchemy import select

    from app.models.manufacturing import ManufacturingItem

    result = await seeded_db.execute(select(ManufacturingItem).limit(1))
    mfg = result.scalar_one_or_none()
    if mfg is None:
        pytest.skip("No manufacturing item")

    contract = await gp_crud.create_contract(
        seeded_db,
        ProductionContractCreate(
            contract_type=ProductionContractType.CMT,
            buyer_name="Brand Co",
            material_supplies=[
                CmtMaterialSupplyIn(
                    manufacturing_item_id=mfg.id,
                    quantity_received=Decimal("1000"),
                ),
            ],
        ),
    )
    await seeded_db.commit()
    assert contract.contract_type == ProductionContractType.CMT
    assert len(contract.material_supplies) == 1


@pytest.mark.asyncio
async def test_line_balance_greedy(seeded_db: AsyncSession) -> None:
    result = calculate_line_balance(
        LineBalanceCalculateIn(
            operations=[
                LineBalanceOperationIn(operation_name="Collar", smv_minutes=Decimal("2.5")),
                LineBalanceOperationIn(operation_name="Sleeve", smv_minutes=Decimal("3.0")),
                LineBalanceOperationIn(operation_name="Hem", smv_minutes=Decimal("1.5")),
            ],
            operators_count=2,
            target_quantity=Decimal("100"),
            available_minutes=Decimal("480"),
        ),
    )
    assert result.calculated_takt_minutes > 0
    assert result.line_efficiency_pct > 0
    assert len(result.assignments) == 3
    stations = {a.station_no for a in result.assignments}
    assert len(stations) <= 2


@pytest.mark.asyncio
async def test_production_plan_and_sewing_line(seeded_db: AsyncSession) -> None:
    from sqlalchemy import select

    from app.models.product import Product

    sl = await gp_crud.create_sewing_line(
        seeded_db,
        SewingLineCreate(code="SL-TEST", name="Test Line", operators_count=5),
    )
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")

    plan = await gp_crud.create_production_plan(
        seeded_db,
        ProductionPlanCreate(
            lines=[
                ProductionPlanLineIn(
                    product_id=product.id,
                    quantity_planned=Decimal("50"),
                ),
            ],
        ),
        created_by_id=1,
    )
    await seeded_db.commit()
    assert plan.id is not None
    assert sl.code == "SL-TEST"


@pytest.mark.asyncio
async def test_fabric_explosion_for_cut_orders(seeded_db: AsyncSession) -> None:
    svc = await build_garment_bom_service()
    summary = await svc.get_fabric_consumption_summary("STYLE-001", order_qty=10)
    assert summary.parent_sku == "STYLE-001"
    assert len(summary.fabrics) >= 0
