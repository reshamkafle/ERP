"""CMT (Cut-Make-Trim) contract rules and material supply checks."""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import garment_planning as gp_crud
from app.models.enums import ProductionContractType
from app.models.garment_planning import ProductionContract
from app.models.manufacturing import ManufacturingItem


async def is_cmt_contract(db: AsyncSession, contract_id: int | None) -> bool:
    if contract_id is None:
        return False
    contract = await gp_crud.get_contract(db, contract_id)
    return contract is not None and contract.contract_type == ProductionContractType.CMT


async def validate_cmt_material_issue(
    db: AsyncSession,
    contract_id: int,
    component_item_id: int,
    quantity: Decimal,
) -> None:
    """CMT orders may only issue buyer-supplied materials within received qty."""
    contract = await gp_crud.get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Production contract not found")
    if contract.contract_type != ProductionContractType.CMT:
        return

    supply = await gp_crud.get_cmt_supply_for_item(db, contract_id, component_item_id)
    if supply is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Component is not on buyer-supplied material list for this CMT contract",
        )
    available = supply.quantity_received - supply.quantity_consumed
    if quantity > available:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient buyer-supplied qty (available: {available})",
        )


async def record_cmt_consumption(
    db: AsyncSession,
    contract_id: int,
    component_item_id: int,
    quantity: Decimal,
) -> None:
    supply = await gp_crud.get_cmt_supply_for_item(db, contract_id, component_item_id)
    if supply is not None:
        supply.quantity_consumed += quantity
        await db.flush()


async def is_cmt_fabric_item(db: AsyncSession, contract_id: int, manufacturing_item_id: int) -> bool:
    """True if item is buyer-supplied under CMT — skip MRP BUY suggestions."""
    if contract_id:
        contract = await gp_crud.get_contract(db, contract_id)
        if contract is None or contract.contract_type != ProductionContractType.CMT:
            return False
        supply = await gp_crud.get_cmt_supply_for_item(db, contract_id, manufacturing_item_id)
        return supply is not None
    return await is_buyer_supplied_item(db, manufacturing_item_id)


async def is_buyer_supplied_item(db: AsyncSession, manufacturing_item_id: int) -> bool:
    """True if any active CMT contract lists this item as buyer-supplied."""
    from sqlalchemy import select

    from app.models.garment_planning import CmtMaterialSupply, ProductionContract

    result = await db.execute(
        select(CmtMaterialSupply.id)
        .join(ProductionContract, ProductionContract.id == CmtMaterialSupply.contract_id)
        .where(
            ProductionContract.contract_type == ProductionContractType.CMT,
            ProductionContract.is_active.is_(True),
            CmtMaterialSupply.manufacturing_item_id == manufacturing_item_id,
        )
        .limit(1),
    )
    return result.scalar_one_or_none() is not None


async def mfg_item_id_for_product(db: AsyncSession, product_id: int) -> int | None:
    from sqlalchemy import select

    result = await db.execute(
        select(ManufacturingItem.id).where(ManufacturingItem.product_id == product_id),
    )
    row = result.scalar_one_or_none()
    return row
