from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import AtpCheckStatus, SaleLineStatus
from app.models.product import Product
from app.models.sale import Sale, SaleItem


async def run_atp_check(db: AsyncSession, sale: Sale) -> AtpCheckStatus:
    result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.items).selectinload(SaleItem.product))
        .where(Sale.id == sale.id),
    )
    loaded = result.scalar_one()
    all_ok = True
    any_ok = False
    for item in loaded.items:
        product = item.product
        available = product.stock if product else 0
        if available >= item.quantity:
            any_ok = True
            item.backorder_quantity = 0
            item.confirmed_quantity = item.quantity
            item.line_status = SaleLineStatus.ALLOCATED
        elif available > 0:
            all_ok = False
            any_ok = True
            item.backorder_quantity = item.quantity - available
            item.confirmed_quantity = available
            item.line_status = SaleLineStatus.PARTIAL
        else:
            all_ok = False
            item.backorder_quantity = item.quantity
            item.line_status = SaleLineStatus.OPEN

    if all_ok and any_ok:
        loaded.atp_check_status = AtpCheckStatus.AVAILABLE
    elif any_ok:
        loaded.atp_check_status = AtpCheckStatus.PARTIAL
    else:
        loaded.atp_check_status = AtpCheckStatus.UNAVAILABLE
    sale.atp_check_status = loaded.atp_check_status
    return sale.atp_check_status
