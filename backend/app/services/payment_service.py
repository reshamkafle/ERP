from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import payment as payment_crud
from app.models.enums import (
    AllocationType,
    DocumentPaymentStatus,
    JournalEntryStatus,
    JournalSourceType,
    PartyType,
    PaymentDirection,
    PaymentStatus,
    PaymentType,
)
from app.models.journal_entry import JournalEntry
from app.models.payment import Payment, PaymentAllocation
from app.models.payment_method import PaymentMethod
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.schemas.accounting import JournalLineIn
from app.services.journal_service import post_entry
from app.schemas.payments import MakePaymentCreate, PaymentAllocationIn, ReceivePaymentCreate
from app.services.payment_posting import post_payment_journal
from app.services.tax_calculation import get_company_settings


def _update_document_payment_status(total: Decimal, amount_paid: Decimal) -> DocumentPaymentStatus:
    if amount_paid <= 0:
        return DocumentPaymentStatus.UNPAID
    if amount_paid >= total:
        return DocumentPaymentStatus.PAID
    return DocumentPaymentStatus.PARTIAL


def _validate_allocations(
    *,
    direction: PaymentDirection,
    amount: Decimal,
    allocations: list[PaymentAllocationIn],
) -> None:
    if not allocations:
        return
    total_alloc = Decimal("0")
    for alloc in allocations:
        if direction == PaymentDirection.INBOUND and alloc.allocation_type == AllocationType.DISCOUNT:
            if alloc.purchase_id is not None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Discount applies to sales only")
        if direction == PaymentDirection.OUTBOUND and alloc.allocation_type == AllocationType.DISCOUNT:
            if alloc.sale_id is not None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Discount applies to purchases only")
        if alloc.allocation_type != AllocationType.OVERPAYMENT:
            total_alloc += alloc.allocated_amount
    if total_alloc > amount:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Sum of allocations exceeds payment amount",
        )


async def _validate_sale_allocations(
    db: AsyncSession,
    *,
    customer_id: int,
    allocations: list[PaymentAllocationIn],
) -> None:
    for alloc in allocations:
        if alloc.sale_id is None or alloc.allocation_type == AllocationType.OVERPAYMENT:
            continue
        result = await db.execute(
            select(Sale).where(Sale.id == alloc.sale_id).with_for_update(),
        )
        sale = result.scalar_one_or_none()
        if sale is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Sale {alloc.sale_id} not found")
        if sale.customer_id != customer_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Sale {alloc.sale_id} does not belong to customer",
            )
        open_bal = payment_crud.sale_open_balance(sale)
        if alloc.allocation_type == AllocationType.INVOICE and alloc.allocated_amount > open_bal:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Allocation exceeds open balance for sale {alloc.sale_id}",
            )


async def _validate_purchase_allocations(
    db: AsyncSession,
    *,
    supplier_id: int,
    allocations: list[PaymentAllocationIn],
) -> None:
    for alloc in allocations:
        if alloc.purchase_id is None or alloc.allocation_type == AllocationType.OVERPAYMENT:
            continue
        result = await db.execute(
            select(Purchase).where(Purchase.id == alloc.purchase_id).with_for_update(),
        )
        purchase = result.scalar_one_or_none()
        if purchase is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Purchase {alloc.purchase_id} not found")
        if purchase.supplier_id != supplier_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase {alloc.purchase_id} does not belong to supplier",
            )
        open_bal = payment_crud.purchase_open_balance(purchase)
        if alloc.allocation_type == AllocationType.INVOICE and alloc.allocated_amount > open_bal:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f"Allocation exceeds open balance for purchase {alloc.purchase_id}",
            )


async def _create_payment_with_allocations(
    db: AsyncSession,
    *,
    direction: PaymentDirection,
    payment_type: PaymentType,
    party_type: PartyType,
    customer_id: int | None,
    supplier_id: int | None,
    payment_method_id: int,
    amount: Decimal,
    payment_date,
    currency_code: str,
    exchange_rate: Decimal | None,
    bank_account_id: int | None,
    reference: str | None,
    notes: str | None,
    erp_document_id: int | None,
    allocations: list[PaymentAllocationIn],
    created_by_id: int,
) -> Payment:
    method = await payment_crud.get_payment_method(db, payment_method_id)
    if method is None or not method.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment method not found")

    settings = await get_company_settings(db)
    rate = exchange_rate or Decimal("1")
    amount_base = (amount * rate).quantize(Decimal("0.01"))

    payment = Payment(
        payment_number=await payment_crud._next_payment_number(db),
        direction=direction,
        payment_type=payment_type,
        status=PaymentStatus.DRAFT,
        party_type=party_type,
        customer_id=customer_id,
        supplier_id=supplier_id,
        payment_method_id=payment_method_id,
        bank_account_id=bank_account_id,
        amount=amount,
        currency_code=currency_code or settings.default_currency,
        exchange_rate=exchange_rate,
        amount_base=amount_base,
        payment_date=payment_date,
        reference=reference,
        notes=notes,
        erp_document_id=erp_document_id,
        created_by_id=created_by_id,
    )
    db.add(payment)
    await db.flush()

    for alloc_in in allocations:
        db.add(
            PaymentAllocation(
                payment_id=payment.id,
                allocation_type=alloc_in.allocation_type,
                sale_id=alloc_in.sale_id,
                purchase_id=alloc_in.purchase_id,
                allocated_amount=alloc_in.allocated_amount,
                notes=alloc_in.notes,
            ),
        )

    await payment_crud.add_audit_log(
        db,
        payment_id=payment.id,
        action="CREATE",
        user_id=created_by_id,
        old_status=None,
        new_status=PaymentStatus.DRAFT.value,
    )
    await db.commit()

    loaded = await payment_crud.get_payment(db, payment.id)
    assert loaded is not None
    return loaded


async def receive_payment(
    db: AsyncSession,
    payload: ReceivePaymentCreate,
    *,
    created_by_id: int,
) -> Payment:
    _validate_allocations(
        direction=PaymentDirection.INBOUND,
        amount=payload.amount,
        allocations=payload.allocations,
    )
    await _validate_sale_allocations(db, customer_id=payload.customer_id, allocations=payload.allocations)
    return await _create_payment_with_allocations(
        db,
        direction=PaymentDirection.INBOUND,
        payment_type=PaymentType.CUSTOMER_RECEIPT,
        party_type=PartyType.CUSTOMER,
        customer_id=payload.customer_id,
        supplier_id=None,
        payment_method_id=payload.payment_method_id,
        amount=payload.amount,
        payment_date=payload.payment_date,
        currency_code=payload.currency_code,
        exchange_rate=payload.exchange_rate,
        bank_account_id=payload.bank_account_id,
        reference=payload.reference,
        notes=payload.notes,
        erp_document_id=payload.erp_document_id,
        allocations=payload.allocations,
        created_by_id=created_by_id,
    )


async def make_payment(
    db: AsyncSession,
    payload: MakePaymentCreate,
    *,
    created_by_id: int,
) -> Payment:
    _validate_allocations(
        direction=PaymentDirection.OUTBOUND,
        amount=payload.amount,
        allocations=payload.allocations,
    )
    await _validate_purchase_allocations(
        db,
        supplier_id=payload.supplier_id,
        allocations=payload.allocations,
    )
    return await _create_payment_with_allocations(
        db,
        direction=PaymentDirection.OUTBOUND,
        payment_type=PaymentType.SUPPLIER_PAYMENT,
        party_type=PartyType.SUPPLIER,
        customer_id=None,
        supplier_id=payload.supplier_id,
        payment_method_id=payload.payment_method_id,
        amount=payload.amount,
        payment_date=payload.payment_date,
        currency_code=payload.currency_code,
        exchange_rate=payload.exchange_rate,
        bank_account_id=payload.bank_account_id,
        reference=payload.reference,
        notes=payload.notes,
        erp_document_id=payload.erp_document_id,
        allocations=payload.allocations,
        created_by_id=created_by_id,
    )


async def submit_for_approval(
    db: AsyncSession,
    payment_id: int,
    *,
    user_id: int,
) -> Payment:
    payment = await payment_crud.get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.status != PaymentStatus.DRAFT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Only draft payments can be submitted")
    old = payment.status.value
    payment.status = PaymentStatus.PENDING_APPROVAL
    await payment_crud.add_audit_log(
        db,
        payment_id=payment.id,
        action="SUBMIT",
        user_id=user_id,
        old_status=old,
        new_status=payment.status.value,
    )
    await db.commit()
    loaded = await payment_crud.get_payment(db, payment.id)
    assert loaded is not None
    return loaded


async def _apply_allocations_to_documents(db: AsyncSession, payment: Payment) -> None:
    for alloc in payment.allocations:
        if alloc.sale_id is not None and alloc.allocation_type in (
            AllocationType.INVOICE,
            AllocationType.DISCOUNT,
        ):
            result = await db.execute(select(Sale).where(Sale.id == alloc.sale_id).with_for_update())
            sale = result.scalar_one()
            sale.amount_paid = (sale.amount_paid or Decimal("0")) + alloc.allocated_amount
            sale.payment_status = _update_document_payment_status(sale.total, sale.amount_paid)
        elif alloc.purchase_id is not None and alloc.allocation_type in (
            AllocationType.INVOICE,
            AllocationType.DISCOUNT,
        ):
            result = await db.execute(
                select(Purchase).where(Purchase.id == alloc.purchase_id).with_for_update(),
            )
            purchase = result.scalar_one()
            purchase.amount_paid = (purchase.amount_paid or Decimal("0")) + alloc.allocated_amount
            purchase.payment_status = _update_document_payment_status(
                purchase.total,
                purchase.amount_paid,
            )


async def _reverse_allocations(db: AsyncSession, payment: Payment) -> None:
    for alloc in payment.allocations:
        if alloc.sale_id is not None and alloc.allocation_type in (
            AllocationType.INVOICE,
            AllocationType.DISCOUNT,
        ):
            result = await db.execute(select(Sale).where(Sale.id == alloc.sale_id).with_for_update())
            sale = result.scalar_one()
            sale.amount_paid = max(
                (sale.amount_paid or Decimal("0")) - alloc.allocated_amount,
                Decimal("0"),
            )
            sale.payment_status = _update_document_payment_status(sale.total, sale.amount_paid)
        elif alloc.purchase_id is not None and alloc.allocation_type in (
            AllocationType.INVOICE,
            AllocationType.DISCOUNT,
        ):
            result = await db.execute(
                select(Purchase).where(Purchase.id == alloc.purchase_id).with_for_update(),
            )
            purchase = result.scalar_one()
            purchase.amount_paid = max(
                (purchase.amount_paid or Decimal("0")) - alloc.allocated_amount,
                Decimal("0"),
            )
            purchase.payment_status = _update_document_payment_status(
                purchase.total,
                purchase.amount_paid,
            )


async def confirm_payment(
    db: AsyncSession,
    payment_id: int,
    *,
    approved_by_id: int,
) -> Payment:
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.allocations),
            selectinload(Payment.payment_method).selectinload(PaymentMethod.gl_account),
        )
        .where(Payment.id == payment_id)
        .with_for_update(),
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.status not in (PaymentStatus.DRAFT, PaymentStatus.PENDING_APPROVAL):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment cannot be confirmed")
    if payment.journal_entry_id is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment already posted")
    if payment.created_by_id is not None and payment.created_by_id == approved_by_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Payment approval must be performed by a different user than the creator",
        )

    old = payment.status.value
    await _apply_allocations_to_documents(db, payment)
    journal_id = await post_payment_journal(db, payment, created_by_id=approved_by_id)
    payment.journal_entry_id = journal_id
    payment.status = PaymentStatus.CONFIRMED
    payment.approved_by_id = approved_by_id
    payment.confirmed_at = datetime.now(timezone.utc)

    await payment_crud.add_audit_log(
        db,
        payment_id=payment.id,
        action="CONFIRM",
        user_id=approved_by_id,
        old_status=old,
        new_status=payment.status.value,
    )
    await db.commit()

    loaded = await payment_crud.get_payment(db, payment.id)
    assert loaded is not None
    return loaded


async def cancel_payment(
    db: AsyncSession,
    payment_id: int,
    *,
    user_id: int,
) -> Payment:
    result = await db.execute(
        select(Payment)
        .options(selectinload(Payment.allocations))
        .where(Payment.id == payment_id)
        .with_for_update(),
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.status == PaymentStatus.CANCELLED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Payment already cancelled")

    old = payment.status.value
    if payment.status == PaymentStatus.CONFIRMED:
        await _reverse_allocations(db, payment)
        if payment.journal_entry_id:
            je_result = await db.execute(
                select(JournalEntry)
                .options(selectinload(JournalEntry.lines))
                .where(JournalEntry.id == payment.journal_entry_id),
            )
            original_entry = je_result.scalar_one_or_none()
            if original_entry:
                rev_lines = [
                    JournalLineIn(
                        account_id=line.account_id,
                        debit=line.credit,
                        credit=line.debit,
                        currency_code=line.currency_code,
                        memo=f"Reversal: {line.memo or ''}",
                    )
                    for line in original_entry.lines
                ]
                rev = await post_entry(
                    db,
                    entry_date=payment.payment_date,
                    source_type=JournalSourceType.PAYMENT,
                    source_id=payment.id,
                    description=f"Reversal of {payment.payment_number}",
                    lines=rev_lines,
                    created_by_id=user_id,
                    reversal_of_id=original_entry.id,
                )
                original_entry.status = JournalEntryStatus.REVERSED
                payment.journal_entry_id = rev.id

    payment.status = PaymentStatus.CANCELLED
    await payment_crud.add_audit_log(
        db,
        payment_id=payment.id,
        action="CANCEL",
        user_id=user_id,
        old_status=old,
        new_status=payment.status.value,
    )
    await db.commit()

    loaded = await payment_crud.get_payment(db, payment.id)
    assert loaded is not None
    return loaded
