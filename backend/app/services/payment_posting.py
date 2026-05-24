from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import chart_of_account as coa_crud
from app.models.enums import (
    AllocationType,
    JournalSourceType,
    PaymentDirection,
)
from app.models.payment import Payment
from app.schemas.accounting import JournalLineIn
from app.services.journal_service import post_entry


async def post_payment_journal(
    db: AsyncSession,
    payment: Payment,
    *,
    created_by_id: int | None,
) -> int:
    """Create balanced journal entry for a confirmed payment. Returns journal_entry_id."""
    cash_account = payment.payment_method.gl_account
    ar = await coa_crud.get_account_by_code(db, "1100")
    ap = await coa_crud.get_account_by_code(db, "2000")
    customer_deposits = await coa_crud.get_account_by_code(db, "2200")
    sales_discounts = await coa_crud.get_account_by_code(db, "5100")
    purchase_discounts = await coa_crud.get_account_by_code(db, "5200")

    if ar is None or ap is None or customer_deposits is None:
        raise ValueError("Required GL accounts missing; run finance migration")

    lines: list[JournalLineIn] = []
    currency = payment.currency_code

    invoice_total = Decimal("0")
    discount_total = Decimal("0")
    for alloc in payment.allocations:
        if alloc.allocation_type == AllocationType.DISCOUNT:
            discount_total += alloc.allocated_amount
        elif alloc.allocation_type == AllocationType.INVOICE:
            invoice_total += alloc.allocated_amount

    overpayment = payment.amount - invoice_total - discount_total
    if overpayment < 0:
        overpayment = Decimal("0")

    ar_credit = invoice_total + discount_total

    if payment.direction == PaymentDirection.INBOUND:
        lines.append(
            JournalLineIn(
                account_id=cash_account.id,
                debit=payment.amount,
                credit=Decimal("0"),
                currency_code=currency,
                memo=f"Receipt {payment.payment_number}",
            ),
        )
        if discount_total > 0 and sales_discounts:
            lines.append(
                JournalLineIn(
                    account_id=sales_discounts.id,
                    debit=discount_total,
                    credit=Decimal("0"),
                    currency_code=currency,
                    memo="Sales discount",
                ),
            )
        if ar_credit > 0:
            lines.append(
                JournalLineIn(
                    account_id=ar.id,
                    debit=Decimal("0"),
                    credit=ar_credit,
                    currency_code=currency,
                    memo="AR settlement",
                ),
            )
        if overpayment > 0:
            lines.append(
                JournalLineIn(
                    account_id=customer_deposits.id,
                    debit=Decimal("0"),
                    credit=overpayment,
                    currency_code=currency,
                    memo="Customer overpayment",
                ),
            )
    else:
        ap_debit = invoice_total + discount_total
        lines.append(
            JournalLineIn(
                account_id=cash_account.id,
                debit=Decimal("0"),
                credit=payment.amount,
                currency_code=currency,
                memo=f"Disbursement {payment.payment_number}",
            ),
        )
        if ap_debit > 0:
            lines.append(
                JournalLineIn(
                    account_id=ap.id,
                    debit=ap_debit,
                    credit=Decimal("0"),
                    currency_code=currency,
                    memo="AP settlement",
                ),
            )
        if discount_total > 0 and purchase_discounts:
            lines.append(
                JournalLineIn(
                    account_id=purchase_discounts.id,
                    debit=Decimal("0"),
                    credit=discount_total,
                    currency_code=currency,
                    memo="Purchase discount",
                ),
            )
        if overpayment > 0:
            lines.append(
                JournalLineIn(
                    account_id=customer_deposits.id,
                    debit=overpayment,
                    credit=Decimal("0"),
                    currency_code=currency,
                    memo="Unallocated disbursement",
                ),
            )

    entry = await post_entry(
        db,
        entry_date=payment.payment_date,
        source_type=JournalSourceType.PAYMENT,
        source_id=payment.id,
        description=f"Payment {payment.payment_number}",
        lines=lines,
        created_by_id=created_by_id,
    )
    return entry.id
