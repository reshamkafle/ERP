"""Sale pricing integrity tests."""

from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import sale as sale_crud
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.sale import SaleItemLineCreate, SaleOrderCreate


@pytest.mark.asyncio
@pytest.mark.integration
async def test_price_override_rejected_without_permission(seeded_db: AsyncSession, admin_user: User) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")

    tampered = product.price - Decimal("1.00")
    if tampered < 0:
        tampered = Decimal("0.01")

    with pytest.raises(HTTPException) as exc_info:
        await sale_crud.create_sale_order(
            seeded_db,
            SaleOrderCreate(
                items=[
                    SaleItemLineCreate(
                        product_id=product.id,
                        quantity=1,
                        unit_price=tampered,
                    ),
                ],
                confirm=False,
                require_b2b_fields=False,
            ),
            created_by_id=admin_user.id,
            allow_price_override=False,
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_price_override_allowed_with_flag(seeded_db: AsyncSession, admin_user: User) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")

    custom = product.price - Decimal("0.50")
    if custom <= 0:
        custom = Decimal("1.00")

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            items=[
                SaleItemLineCreate(
                    product_id=product.id,
                    quantity=1,
                    unit_price=custom,
                ),
            ],
            confirm=False,
            require_b2b_fields=False,
        ),
        created_by_id=admin_user.id,
        allow_price_override=True,
    )
    assert sale.items[0].unit_price == custom
