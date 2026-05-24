from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import payment as payment_crud
from app.models.enums import DocumentPaymentStatus
from app.models.sale import Sale
from app.schemas.payments import PaymentAllocationIn, ReceivePaymentCreate
from app.services import payment_service
from app.services.journal_service import post_entry
from app.models.enums import JournalSourceType
from app.schemas.accounting import JournalLineIn


@pytest.mark.asyncio
async def test_journal_balanced_guard(db_session: AsyncSession) -> None:
    from app.crud import chart_of_account as coa_crud
    from fastapi import HTTPException

    cash = await coa_crud.get_account_by_code(db_session, "1000")
    ar = await coa_crud.get_account_by_code(db_session, "1100")
    if cash is None or ar is None:
        pytest.skip("Finance COA not seeded")

    with pytest.raises(HTTPException) as exc:
        await post_entry(
            db_session,
            entry_date=date.today(),
            source_type=JournalSourceType.MANUAL,
            source_id=None,
            description="Unbalanced",
            lines=[
                JournalLineIn(account_id=cash.id, debit=Decimal("100"), credit=Decimal("0")),
                JournalLineIn(account_id=ar.id, debit=Decimal("0"), credit=Decimal("50")),
            ],
            created_by_id=None,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_receive_payment_confirm(seeded_db: AsyncSession, admin_user) -> None:
    from app.models.customer import Customer
    from app.models.product import Product
    from app.schemas.sale import PosCheckoutCreate, SaleItemLineCreate
    from app.crud import sale as sale_crud

    methods = await payment_crud.list_payment_methods(seeded_db)
    if not methods:
        pytest.skip("Payment methods not seeded")
    method = methods[0]

    customer = (
        await seeded_db.execute(select(Customer).limit(1))
    ).scalar_one_or_none()
    if customer is None:
        customer = Customer(name="Payment Test Customer", email="paytest@example.com")
        seeded_db.add(customer)
        await seeded_db.flush()

    sale = (
        await seeded_db.execute(
            select(Sale).where(Sale.customer_id == customer.id).limit(1),
        )
    ).scalar_one_or_none()
    if sale is None:
        product = (await seeded_db.execute(select(Product).limit(1))).scalar_one_or_none()
        if product is None:
            pytest.skip("No product for sale")
        sale = await sale_crud.create_sale(
            seeded_db,
            PosCheckoutCreate(
                customer_id=customer.id,
                items=[SaleItemLineCreate(product_id=product.id, quantity=1)],
                confirm=True,
            ),
            created_by_id=admin_user.id,
        )

    sale.payment_status = DocumentPaymentStatus.UNPAID
    sale.amount_paid = Decimal("0")
    if sale.total <= 0:
        sale.total = Decimal("100")
        sale.subtotal = Decimal("100")
    await seeded_db.commit()

    open_before = payment_crud.sale_open_balance(sale)
    alloc_amount = min(Decimal("10"), open_before)
    if alloc_amount <= 0:
        pytest.skip("Sale has no open balance")

    payment = await payment_service.receive_payment(
        seeded_db,
        ReceivePaymentCreate(
            customer_id=customer.id,
            payment_method_id=method.id,
            amount=alloc_amount,
            payment_date=date.today(),
            allocations=[
                PaymentAllocationIn(
                    sale_id=sale.id,
                    allocated_amount=alloc_amount,
                ),
            ],
        ),
        created_by_id=admin_user.id,
    )
    assert payment.status.value == "DRAFT"

    confirmed = await payment_service.confirm_payment(
        seeded_db,
        payment.id,
        approved_by_id=admin_user.id,
    )
    assert confirmed.status.value == "CONFIRMED"
    assert confirmed.journal_entry_id is not None

    refreshed = (
        await seeded_db.execute(select(Sale).where(Sale.id == sale.id))
    ).scalar_one()
    assert refreshed.amount_paid >= alloc_amount
