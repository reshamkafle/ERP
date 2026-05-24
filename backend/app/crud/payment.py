from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PaymentDirection, PaymentStatus
from app.models.payment import Payment, PaymentAllocation, PaymentAuditLog
from app.models.payment_method import PaymentMethod
from app.models.purchase import Purchase
from app.models.sale import Sale


async def _next_payment_number(db: AsyncSession) -> str:
    year = date.today().year
    prefix = f"PAY-{year}-"
    result = await db.execute(
        select(func.count()).select_from(Payment).where(Payment.payment_number.like(f"{prefix}%")),
    )
    count = result.scalar_one() or 0
    return f"{prefix}{count + 1:06d}"


async def get_payment_method(db: AsyncSession, method_id: int) -> PaymentMethod | None:
    result = await db.execute(select(PaymentMethod).where(PaymentMethod.id == method_id))
    return result.scalar_one_or_none()


async def list_payment_methods(db: AsyncSession) -> list[PaymentMethod]:
    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.is_active.is_(True)).order_by(PaymentMethod.code),
    )
    return list(result.scalars().all())


async def get_payment(db: AsyncSession, payment_id: int) -> Payment | None:
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.allocations),
            selectinload(Payment.payment_method),
            selectinload(Payment.customer),
            selectinload(Payment.supplier),
        )
        .where(Payment.id == payment_id),
    )
    return result.scalar_one_or_none()


async def list_payments(
    db: AsyncSession,
    *,
    direction: PaymentDirection | None = None,
    status_filter: PaymentStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Payment], int]:
    stmt = select(Payment).options(
        selectinload(Payment.customer),
        selectinload(Payment.supplier),
    ).order_by(Payment.created_at.desc())
    count_stmt = select(func.count()).select_from(Payment)
    if direction is not None:
        stmt = stmt.where(Payment.direction == direction)
        count_stmt = count_stmt.where(Payment.direction == direction)
    if status_filter is not None:
        stmt = stmt.where(Payment.status == status_filter)
        count_stmt = count_stmt.where(Payment.status == status_filter)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def add_audit_log(
    db: AsyncSession,
    *,
    payment_id: int,
    action: str,
    user_id: int | None,
    old_status: str | None,
    new_status: str | None,
    snapshot: dict | None = None,
) -> None:
    db.add(
        PaymentAuditLog(
            payment_id=payment_id,
            action=action,
            user_id=user_id,
            old_status=old_status,
            new_status=new_status,
            snapshot=snapshot,
        ),
    )


def sale_open_balance(sale: Sale) -> Decimal:
    total = sale.total or Decimal("0")
    paid = sale.amount_paid or Decimal("0")
    return max(total - paid, Decimal("0"))


def purchase_open_balance(purchase: Purchase) -> Decimal:
    total = purchase.total or Decimal("0")
    paid = purchase.amount_paid or Decimal("0")
    return max(total - paid, Decimal("0"))


async def get_sale_open_balance(db: AsyncSession, sale_id: int) -> Sale | None:
    result = await db.execute(select(Sale).where(Sale.id == sale_id))
    return result.scalar_one_or_none()


async def get_purchase_open_balance(db: AsyncSession, purchase_id: int) -> Purchase | None:
    result = await db.execute(select(Purchase).where(Purchase.id == purchase_id))
    return result.scalar_one_or_none()
