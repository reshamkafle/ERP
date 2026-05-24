from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import payment as payment_crud
from app.models.customer import Customer
from app.models.enums import CreditCheckStatus, DocumentPaymentStatus, SaleOrderStatus
from app.models.sale import Sale


async def run_credit_check(
    db: AsyncSession,
    sale: Sale,
    customer: Customer | None,
    *,
    override: bool = False,
) -> CreditCheckStatus:
    if override:
        sale.credit_check_status = CreditCheckStatus.OVERRIDE
        return sale.credit_check_status
    if customer is None or customer.credit_limit is None:
        sale.credit_check_status = CreditCheckStatus.PASSED
        return sale.credit_check_status

    open_balance = payment_crud.sale_open_balance(sale)
    outstanding_result = await db.execute(
        select(func.coalesce(func.sum(Sale.total - Sale.amount_paid), 0))
        .where(
            Sale.customer_id == customer.id,
            Sale.id != sale.id,
            Sale.order_status.not_in(
                (SaleOrderStatus.DRAFT, SaleOrderStatus.CANCELLED),
            ),
            Sale.payment_status != DocumentPaymentStatus.PAID,
        ),
    )
    other_ar = Decimal(str(outstanding_result.scalar_one() or 0))
    exposure = other_ar + open_balance + sale.total
    if exposure <= customer.credit_limit:
        sale.credit_check_status = CreditCheckStatus.PASSED
    else:
        sale.credit_check_status = CreditCheckStatus.FAILED
    return sale.credit_check_status
