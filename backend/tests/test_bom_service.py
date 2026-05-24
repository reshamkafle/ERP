"""Unit tests for multi-level garment BOM module."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.manufacturing.bom import (
    BOM,
    BOMError,
    BOMHeaderInput,
    BOMItem,
    BOMItemInput,
    BOMService,
    BOMStatus,
    ConsumptionType,
    InMemoryBOMRepository,
    ItemCategory,
    ItemNotFoundError,
    SaveBOMRequest,
    UnitOfMeasure,
)
from app.manufacturing.bom.exceptions import BOMNotFoundError
from tests.fixtures.bom_garment_sample import build_garment_bom_service


@pytest.fixture
async def garment_svc() -> BOMService:
    return await build_garment_bom_service()


@pytest.mark.asyncio
async def test_explode_multi_level_fabric(garment_svc: BOMService) -> None:
    result = await garment_svc.explode_bom("STYLE-001", order_quantity=100)
    fabric_lines = [ln for ln in result.lines if ln.sku == "FAB-RAW"]
    assert len(fabric_lines) == 1
    line = fabric_lines[0]
    assert line.gross_qty == Decimal("250")
    assert line.wastage_qty == Decimal("12.5")
    assert line.total_qty == Decimal("262.5")


@pytest.mark.asyncio
async def test_explode_single_level_trim(garment_svc: BOMService) -> None:
    result = await garment_svc.explode_bom("STYLE-001", order_quantity=10)
    trim_lines = [ln for ln in result.lines if ln.sku == "TRIM-BTN"]
    assert len(trim_lines) == 1
    line = trim_lines[0]
    assert line.gross_qty == Decimal("120")
    assert line.wastage_qty == Decimal("2.4")
    assert line.total_qty == Decimal("122.4")


@pytest.mark.asyncio
async def test_cost_rollup(garment_svc: BOMService) -> None:
    result = await garment_svc.explode_bom("STYLE-001", order_quantity=100)
    fabric_cost = Decimal("262.5") * Decimal("3.50")
    trim_cost = Decimal("1224") * Decimal("0.15")
    assert result.total_material_cost == fabric_cost + trim_cost


@pytest.mark.asyncio
async def test_calculate_material_requirements_shape(garment_svc: BOMService) -> None:
    req = await garment_svc.calculate_material_requirements("STYLE-001", order_qty=1)
    assert req["parent_sku"] == "STYLE-001"
    assert req["order_qty"] == 1
    assert "materials" in req
    assert "total_cost" in req
    skus = {m["sku"] for m in req["materials"]}
    assert skus == {"FAB-RAW", "TRIM-BTN"}


@pytest.mark.asyncio
async def test_get_full_bom_unlimited_depth(garment_svc: BOMService) -> None:
    tree = await garment_svc.get_full_bom("STYLE-001")
    assert tree.parent_sku == "STYLE-001"
    assert len(tree.root.children) == 2
    panel = next(c for c in tree.root.children if c.item.sku == "PANEL-ASM")
    assert len(panel.children) == 1
    fab_cut = panel.children[0]
    assert fab_cut.item.sku == "FAB-CUT"
    assert len(fab_cut.children) == 1
    assert fab_cut.children[0].item.sku == "FAB-RAW"


@pytest.mark.asyncio
async def test_get_full_bom_depth_limit(garment_svc: BOMService) -> None:
    tree = await garment_svc.get_full_bom("STYLE-001", depth=1)
    assert len(tree.root.children) == 2
    for child in tree.root.children:
        assert child.children == []


@pytest.mark.asyncio
async def test_fabric_consumption_summary(garment_svc: BOMService) -> None:
    summary = await garment_svc.get_fabric_consumption_summary("STYLE-001", order_qty=100)
    assert summary.parent_sku == "STYLE-001"
    assert len(summary.fabrics) == 1
    assert summary.fabrics[0].sku == "FAB-RAW"
    assert summary.total_meters == Decimal("262.5")
    assert summary.total_fabric_cost == Decimal("262.5") * Decimal("3.50")


@pytest.mark.asyncio
async def test_trim_requirements_summary(garment_svc: BOMService) -> None:
    summary = await garment_svc.get_trim_requirements("STYLE-001", order_qty=10)
    assert len(summary.trims) == 1
    assert summary.trims[0].sku == "TRIM-BTN"
    assert summary.trims[0].total_qty == Decimal("122.4")


@pytest.mark.asyncio
async def test_cycle_detection_rejects_add_bom() -> None:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await svc.create_item("A", "Item A", ItemCategory.SUB_ASSEMBLY, UnitOfMeasure.PIECE)
    await svc.create_item("B", "Item B", ItemCategory.SUB_ASSEMBLY, UnitOfMeasure.PIECE)

    await svc.add_bom("A", [BOMItemInput(component_sku="B", quantity_per_unit=Decimal("1"))])

    with pytest.raises(BOMError, match="cycle"):
        await svc.add_bom("B", [BOMItemInput(component_sku="A", quantity_per_unit=Decimal("1"))])


@pytest.mark.asyncio
async def test_validate_bom_missing_component() -> None:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    parent = await svc.create_item(
        "PARENT",
        "Parent",
        ItemCategory.FINISHED_GOOD,
        UnitOfMeasure.PIECE,
    )
    bom = BOM(
        parent_item_id=parent.id,
        parent_sku=parent.sku,
        lines=[
            BOMItem(
                parent_item_id=parent.id,
                component_item_id=99999,
                line_sequence=1,
                quantity_per_unit=Decimal("1"),
            ),
        ],
    )
    result = await svc.validate_bom(bom)
    assert not result.is_valid
    assert any("not found" in e for e in result.errors)


@pytest.mark.asyncio
async def test_item_not_found() -> None:
    svc = BOMService(InMemoryBOMRepository())
    with pytest.raises(ItemNotFoundError):
        await svc.explode_bom("MISSING", order_quantity=1)


@pytest.mark.asyncio
async def test_bom_not_found_for_tree() -> None:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await svc.create_item("ORPHAN", "Orphan", ItemCategory.FINISHED_GOOD, UnitOfMeasure.PIECE)
    with pytest.raises(BOMNotFoundError):
        await svc.get_full_bom("ORPHAN")


@pytest.mark.asyncio
async def test_apply_wastage_zero() -> None:
    from app.manufacturing.bom.calculators import apply_wastage

    gross, wastage, total = apply_wastage(Decimal("100"), Decimal("0"))
    assert gross == Decimal("100")
    assert wastage == Decimal("0")
    assert total == Decimal("100")


@pytest.mark.asyncio
async def test_save_bom_with_header_fields(garment_svc: BOMService) -> None:
    bom = await garment_svc.save_bom(
        "STYLE-001",
        SaveBOMRequest(
            header=BOMHeaderInput(
                status=BOMStatus.ACTIVE,
                eco_number="ECO-100",
            ),
            lines=[
                BOMItemInput(
                    component_sku="PANEL-ASM",
                    line_sequence=1,
                    quantity_per_unit=Decimal("1"),
                ),
                BOMItemInput(
                    component_sku="TRIM-BTN",
                    line_sequence=2,
                    quantity_per_unit=Decimal("12"),
                    consumption_type=ConsumptionType.TRIM,
                    wastage_percentage=Decimal("2"),
                ),
            ],
        ),
    )
    assert bom.eco_number == "ECO-100"
    assert bom.status == BOMStatus.ACTIVE
    assert bom.bom_number.endswith(f"-V{bom.version}")
    assert len(bom.lines) == 2
    assert bom.lines[0].line_sequence == 1


@pytest.mark.asyncio
async def test_update_bom_status(garment_svc: BOMService) -> None:
    updated = await garment_svc.update_bom_status("STYLE-001", BOMStatus.OBSOLETE)
    assert updated.status == BOMStatus.OBSOLETE
    await garment_svc.update_bom_status("STYLE-001", BOMStatus.ACTIVE)
    with pytest.raises(BOMError, match="status"):
        await garment_svc.update_bom_status("STYLE-001", BOMStatus.DRAFT)


@pytest.mark.asyncio
async def test_apply_yield_inflation() -> None:
    from app.manufacturing.bom.calculators import apply_yield

    assert apply_yield(Decimal("100"), Decimal("0")) == Decimal("100")
    assert apply_yield(Decimal("100"), Decimal("100")) == Decimal("100")
    assert apply_yield(Decimal("90"), Decimal("90")) == Decimal("100")


@pytest.mark.asyncio
async def test_yield_affects_explosion() -> None:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await svc.create_item(
        "FG",
        "Finished",
        ItemCategory.FINISHED_GOOD,
        UnitOfMeasure.PIECE,
    )
    await svc.create_item(
        "FAB",
        "Fabric",
        ItemCategory.FABRIC,
        UnitOfMeasure.METER,
        cost_per_unit=Decimal("1"),
    )
    await svc.add_bom(
        "FG",
        [
            BOMItemInput(
                component_sku="FAB",
                quantity_per_unit=Decimal("10"),
                consumption_type=ConsumptionType.FABRIC,
                yield_percentage=Decimal("90"),
                wastage_percentage=Decimal("5"),
            ),
        ],
    )
    result = await svc.explode_bom("FG", order_quantity=1)
    line = result.lines[0]
    # 10 / 0.9 = 11.111..., +5% wastage -> 11.666...
    expected_gross = Decimal("10") / Decimal("0.9")
    assert line.gross_qty == expected_gross
    assert line.total_qty == expected_gross * Decimal("1.05")


@pytest.mark.asyncio
async def test_uom_conversion_on_explosion() -> None:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await svc.create_item(
        "FG",
        "Finished",
        ItemCategory.FINISHED_GOOD,
        UnitOfMeasure.PIECE,
    )
    await svc.create_item(
        "FAB",
        "Fabric",
        ItemCategory.FABRIC,
        UnitOfMeasure.METER,
        cost_per_unit=Decimal("1"),
        secondary_uom=UnitOfMeasure.YARD,
        conversion_factor=Decimal("0.9144"),
    )
    await svc.add_bom(
        "FG",
        [
            BOMItemInput(
                component_sku="FAB",
                quantity_per_unit=Decimal("10"),
                consumption_type=ConsumptionType.FABRIC,
            ),
        ],
    )
    result = await svc.explode_bom("FG", order_quantity=1)
    line = result.lines[0]
    assert line.gross_qty == Decimal("10") * Decimal("0.9144")
