"""Seed demo garment BOM (style → panel → fabric + trims)."""

from __future__ import annotations

from decimal import Decimal

from app.manufacturing.bom.enums import BOMStatus, ConsumptionType, ItemCategory, UnitOfMeasure
from app.manufacturing.bom.repository import InMemoryBOMRepository
from app.manufacturing.bom.schemas import BOMItemInput
from app.manufacturing.bom.service import BOMService


async def seed_garment_demo(svc: BOMService) -> None:
    existing = await svc._repo.get_item_by_sku("STYLE-001")
    if existing is not None:
        return

    await svc.create_item(
        "STYLE-001",
        "Classic Shirt Style",
        ItemCategory.FINISHED_GOOD,
        UnitOfMeasure.PIECE,
        cost_per_unit=Decimal("0"),
    )
    await svc.create_item(
        "PANEL-ASM",
        "Front Panel Assembly",
        ItemCategory.SUB_ASSEMBLY,
        UnitOfMeasure.PIECE,
        cost_per_unit=Decimal("0"),
    )
    await svc.create_item(
        "FAB-CUT",
        "Fabric Cut Piece",
        ItemCategory.SUB_ASSEMBLY,
        UnitOfMeasure.PIECE,
        cost_per_unit=Decimal("0"),
    )
    await svc.create_item(
        "FAB-RAW",
        "Cotton Shirting",
        ItemCategory.FABRIC,
        UnitOfMeasure.METER,
        cost_per_unit=Decimal("3.50"),
    )
    await svc.create_item(
        "TRIM-BTN",
        "Polyester Button",
        ItemCategory.TRIM,
        UnitOfMeasure.PIECE,
        cost_per_unit=Decimal("0.15"),
    )

    await svc.add_bom(
        "FAB-CUT",
        [
            BOMItemInput(
                component_sku="FAB-RAW",
                quantity_per_unit=Decimal("2.5"),
                consumption_type=ConsumptionType.FABRIC,
                wastage_percentage=Decimal("5"),
            ),
        ],
    )
    await svc.add_bom(
        "PANEL-ASM",
        [
            BOMItemInput(
                component_sku="FAB-CUT",
                quantity_per_unit=Decimal("1"),
                consumption_type=ConsumptionType.OTHER,
            ),
        ],
    )
    from app.manufacturing.bom.schemas import BOMHeaderInput, SaveBOMRequest

    await svc.save_bom(
        "STYLE-001",
        SaveBOMRequest(
            header=BOMHeaderInput(status=BOMStatus.ACTIVE, eco_number="ECO-DEMO-001"),
            lines=[
                BOMItemInput(
                    component_sku="PANEL-ASM",
                    line_sequence=1,
                    quantity_per_unit=Decimal("1"),
                    consumption_type=ConsumptionType.OTHER,
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


async def create_demo_bom_service() -> BOMService:
    repo = InMemoryBOMRepository()
    svc = BOMService(repo)
    await seed_garment_demo(svc)
    return svc
