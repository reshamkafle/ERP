"""Idempotent seed for garment production planning demo data."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import garment_planning as gp_crud
from app.models.enums import ProductionContractType
from app.models.garment_planning import ProductionContract, SewingLine
from app.models.manufacturing import ManufacturingItem
from app.schemas.garment_planning import CmtMaterialSupplyIn, ProductionContractCreate, SewingLineCreate


async def seed_garment_planning_demo(db: AsyncSession) -> None:
    existing = await db.execute(select(SewingLine).where(SewingLine.code == "SL-01"))
    if existing.scalar_one_or_none() is not None:
        return

    await gp_crud.create_sewing_line(
        db,
        SewingLineCreate(
            code="SL-01",
            name="Sewing Line 1",
            operators_count=5,
            minutes_per_shift=Decimal("480"),
            efficiency_pct=Decimal("85"),
        ),
    )

    mfg_result = await db.execute(
        select(ManufacturingItem).where(ManufacturingItem.sku.like("RM-FABRIC%")).limit(1),
    )
    fabric = mfg_result.scalar_one_or_none()
    if fabric is None:
        mfg_result = await db.execute(select(ManufacturingItem).limit(1))
        fabric = mfg_result.scalar_one_or_none()

    if fabric is not None:
        existing_contract = await db.execute(
            select(ProductionContract).where(ProductionContract.contract_number == "PC-DEMO-CMT"),
        )
        if existing_contract.scalar_one_or_none() is None:
            await gp_crud.create_contract(
                db,
                ProductionContractCreate(
                    contract_number="PC-DEMO-CMT",
                    contract_type=ProductionContractType.CMT,
                    buyer_name="Demo Brand",
                    material_supplies=[
                        CmtMaterialSupplyIn(
                            manufacturing_item_id=fabric.id,
                            quantity_received=Decimal("5000"),
                            uom="M",
                        ),
                    ],
                ),
            )

    await db.flush()
