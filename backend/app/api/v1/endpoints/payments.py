from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import payment as payment_crud
from app.dependencies.auth import require_permission
from app.models.enums import PaymentDirection, PaymentStatus
from app.models.user import User
from app.schemas.accounting import JournalEntryRead, JournalLineRead
from app.schemas.payments import (
    MakePaymentCreate,
    OpenBalanceRead,
    PaymentAllocationRead,
    PaymentListItem,
    PaymentListResponse,
    PaymentRead,
    ReceivePaymentCreate,
)
from app.services import journal_service, payment_service

router = APIRouter(prefix="/payments")

PaymentReadPerm = require_permission("finance.payments.read", "finance.records.read")
PaymentWritePerm = require_permission("finance.payments.write", "finance.records.write")
PaymentApprovePerm = require_permission(
    "finance.payments.approve",
    "finance.payments.write",
    "finance.records.write",
)


def _party_name(payment) -> str | None:
    if payment.customer:
        return payment.customer.name
    if payment.supplier:
        return payment.supplier.name
    return payment.party_name


def _payment_to_read(payment) -> PaymentRead:
    return PaymentRead(
        id=payment.id,
        payment_number=payment.payment_number,
        direction=payment.direction,
        payment_type=payment.payment_type,
        status=payment.status,
        party_type=payment.party_type,
        customer_id=payment.customer_id,
        supplier_id=payment.supplier_id,
        party_name=_party_name(payment),
        payment_method_id=payment.payment_method_id,
        bank_account_id=payment.bank_account_id,
        amount=payment.amount,
        currency_code=payment.currency_code,
        exchange_rate=payment.exchange_rate,
        amount_base=payment.amount_base,
        payment_date=payment.payment_date,
        reference=payment.reference,
        notes=payment.notes,
        journal_entry_id=payment.journal_entry_id,
        allocations=[PaymentAllocationRead.model_validate(a) for a in payment.allocations],
        created_at=payment.created_at,
        confirmed_at=payment.confirmed_at,
    )


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PaymentReadPerm)],
    direction: PaymentDirection | None = None,
    status_filter: PaymentStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> PaymentListResponse:
    items, total = await payment_crud.list_payments(
        db,
        direction=direction,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )
    return PaymentListResponse(
        items=[
            PaymentListItem(
                id=p.id,
                payment_number=p.payment_number,
                direction=p.direction,
                payment_type=p.payment_type,
                status=p.status,
                amount=p.amount,
                currency_code=p.currency_code,
                payment_date=p.payment_date,
                party_name=_party_name(p),
            )
            for p in items
        ],
        total=total,
    )


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PaymentReadPerm)],
) -> PaymentRead:
    payment = await payment_crud.get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return _payment_to_read(payment)


@router.post("/receive", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def receive_payment(
    body: ReceivePaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PaymentWritePerm)],
) -> PaymentRead:
    payment = await payment_service.receive_payment(db, body, created_by_id=user.id)
    return _payment_to_read(payment)


@router.post("/disburse", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def make_payment(
    body: MakePaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PaymentWritePerm)],
) -> PaymentRead:
    payment = await payment_service.make_payment(db, body, created_by_id=user.id)
    return _payment_to_read(payment)


@router.post("/{payment_id}/submit", response_model=PaymentRead)
async def submit_payment(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PaymentWritePerm)],
) -> PaymentRead:
    payment = await payment_service.submit_for_approval(db, payment_id, user_id=user.id)
    return _payment_to_read(payment)


@router.post("/{payment_id}/confirm", response_model=PaymentRead)
async def confirm_payment(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PaymentApprovePerm)],
) -> PaymentRead:
    payment = await payment_service.confirm_payment(db, payment_id, approved_by_id=user.id)
    return _payment_to_read(payment)


@router.post("/{payment_id}/cancel", response_model=PaymentRead)
async def cancel_payment(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PaymentApprovePerm)],
) -> PaymentRead:
    payment = await payment_service.cancel_payment(db, payment_id, user_id=user.id)
    return _payment_to_read(payment)


@router.get("/{payment_id}/journal", response_model=JournalEntryRead)
async def get_payment_journal(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PaymentReadPerm)],
) -> JournalEntryRead:
    from app.models.enums import JournalSourceType

    payment = await payment_crud.get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.journal_entry_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No journal entry for this payment")
    entry = await journal_service.get_journal_for_source(
        db,
        source_type=JournalSourceType.PAYMENT,
        source_id=payment.id,
    )
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    return JournalEntryRead(
        id=entry.id,
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        source_type=entry.source_type,
        source_id=entry.source_id,
        status=entry.status,
        description=entry.description,
        lines=[
            JournalLineRead(
                id=line.id,
                account_id=line.account_id,
                account_code=line.account.code,
                account_name=line.account.name,
                debit=line.debit,
                credit=line.credit,
                currency_code=line.currency_code,
                memo=line.memo,
            )
            for line in entry.lines
        ],
        created_at=entry.created_at,
    )
