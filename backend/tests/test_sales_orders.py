from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import sale as sale_crud
from app.models.customer import Customer
from app.models.enums import DocumentPaymentStatus, SaleOrderStatus, SalePartnerRole
from app.models.product import Product
from app.models.sale import Sale
from app.schemas.sale import (
    PosCheckoutCreate,
    SaleConfirmRequest,
    SaleItemLineCreate,
    SaleOrderCreate,
    SalePartnerCreate,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_draft_sale_order(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")
    original_stock = product.stock

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
            confirm=False,
            require_b2b_fields=False,
        ),
        created_by_id=admin_user.id,
    )
    assert sale.order_status == SaleOrderStatus.DRAFT
    assert sale.order_number.startswith("SO-")
    assert sale.payment_status == DocumentPaymentStatus.UNPAID

    await seeded_db.refresh(product)
    assert product.stock == original_stock


@pytest.mark.asyncio
@pytest.mark.integration
async def test_confirm_draft_issues_stock(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")
    if product.stock < 2:
        pytest.skip("Insufficient stock for test")

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
            confirm=False,
            require_b2b_fields=False,
        ),
        created_by_id=admin_user.id,
    )
    stock_before = product.stock
    confirmed = await sale_crud.confirm_sale_order(
        seeded_db,
        sale,
        SaleConfirmRequest(run_credit_check=False, run_atp_check=False),
        user_id=admin_user.id,
    )
    assert confirmed.order_status == SaleOrderStatus.RELEASED
    await seeded_db.refresh(product)
    assert product.stock == stock_before - 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pos_checkout_paid(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None or product.stock < 1:
        pytest.skip("No stock")

    sale = await sale_crud.create_sale(
        seeded_db,
        PosCheckoutCreate(
            items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
            confirm=True,
        ),
        created_by_id=admin_user.id,
    )
    assert sale.is_pos_checkout is True
    assert sale.order_status == SaleOrderStatus.RELEASED
    assert sale.payment_status == DocumentPaymentStatus.PAID
    assert sale.amount_paid == sale.total


@pytest.mark.asyncio
@pytest.mark.integration
async def test_credit_check_blocks_confirm(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None or product.stock < 1:
        pytest.skip("No stock")

    customer = Customer(
        name="Low Credit Co",
        credit_limit=Decimal("1"),
        email="low@example.com",
    )
    seeded_db.add(customer)
    await seeded_db.flush()

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            customer_id=customer.id,
            sales_organization="1000",
            customer_po_number="PO-TEST",
            payment_terms="NET_30",
            items=[SaleItemLineCreate(product_id=product.id, quantity=2, unit_price=Decimal("100"))],
            confirm=False,
        ),
        created_by_id=admin_user.id,
    )
    if sale.total <= Decimal("1"):
        pytest.skip("Sale total too low for credit test")

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await sale_crud.confirm_sale_order(
            seeded_db,
            sale,
            SaleConfirmRequest(run_credit_check=True, run_atp_check=False),
            user_id=admin_user.id,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cancel_draft(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
            confirm=False,
            require_b2b_fields=False,
        ),
        created_by_id=admin_user.id,
    )
    cancelled = await sale_crud.cancel_sale_order(seeded_db, sale, user_id=admin_user.id)
    assert cancelled.order_status == SaleOrderStatus.CANCELLED


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_sale_order_full_erp_fields(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    customer = (await seeded_db.execute(select(Customer).limit(1))).scalar_one_or_none()
    if product is None or customer is None:
        pytest.skip("Missing seed data")

    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            customer_id=customer.id,
            order_date=date.today(),
            sales_organization="1000",
            distribution_channel="10",
            division="00",
            customer_po_number="PO-ERP-001",
            customer_po_date=date.today(),
            payment_terms="NET_30",
            campaign_id="CAMP-2026",
            price_group="WHOLESALE",
            items=[
                SaleItemLineCreate(
                    product_id=product.id,
                    quantity=2,
                    unit_price=product.price,
                    batch_number="BATCH-01",
                    serial_number="SN-001",
                    item_category="STANDARD",
                    alternate_uom="CS",
                    uom_conversion_factor=Decimal("12"),
                ),
            ],
            partners=[
                SalePartnerCreate(role=SalePartnerRole.BILL_TO, customer_id=customer.id),
                SalePartnerCreate(role=SalePartnerRole.PAYER, customer_id=customer.id),
            ],
            confirm=False,
        ),
        created_by_id=admin_user.id,
    )
    assert sale.sales_organization == "1000"
    assert sale.customer_po_number == "PO-ERP-001"
    assert sale.campaign_id == "CAMP-2026"
    assert len(sale.items) == 1
    line = sale.items[0]
    assert line.batch_number == "BATCH-01"
    assert line.item_category == "STANDARD"

    partner_roles = {p.role for p in sale.partners}
    assert SalePartnerRole.BILL_TO in partner_roles
    assert SalePartnerRole.PAYER in partner_roles
    assert SalePartnerRole.SOLD_TO in partner_roles
    assert line.alternate_uom == "CS"
    assert line.uom_conversion_factor == Decimal("12")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_b2b_validation_rejects_incomplete_order(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    if product is None:
        pytest.skip("No product")

    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        SaleOrderCreate(
            items=[SaleItemLineCreate(product_id=product.id, quantity=1, unit_price=product.price)],
            confirm=False,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_manual_order_number_override(seeded_db: AsyncSession, admin_user) -> None:
    product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
    customer = (await seeded_db.execute(select(Customer).limit(1))).scalar_one_or_none()
    if product is None or customer is None:
        pytest.skip("Missing seed data")

    manual_number = f"SO-MANUAL-{admin_user.id}-{product.id}"
    sale = await sale_crud.create_sale_order(
        seeded_db,
        SaleOrderCreate(
            order_number_override=manual_number,
            customer_id=customer.id,
            sales_organization="1000",
            customer_po_number="PO-MANUAL",
            payment_terms="NET_30",
            items=[SaleItemLineCreate(product_id=product.id, quantity=1, unit_price=product.price)],
            confirm=False,
        ),
        created_by_id=admin_user.id,
    )
    assert sale.order_number == manual_number
