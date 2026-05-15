from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.models.sale import Sale
from app.schemas.customer import CustomerCreate, CustomerUpdate


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


async def list_customers(
    db: AsyncSession,
    *,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Customer], int]:
    stmt = select(Customer)
    count_stmt = select(func.count()).select_from(Customer)

    if search:
        pattern = f"%{search.strip()}%"
        filter_expr = or_(
            Customer.name.ilike(pattern),
            Customer.phone.ilike(pattern),
            Customer.email.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Customer.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_customer(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalar_one_or_none()


async def get_customer_with_recent_sales(
    db: AsyncSession,
    customer_id: int,
    *,
    sales_limit: int = 10,
) -> tuple[Customer | None, list[tuple[Sale, int, Decimal]]]:
    customer = await get_customer(db, customer_id)
    if customer is None:
        return None, []

    sales_result = await db.execute(
        select(Sale)
        .options(selectinload(Sale.items))
        .where(Sale.customer_id == customer_id)
        .order_by(Sale.created_at.desc())
        .limit(sales_limit),
    )
    sales = list(sales_result.scalars().all())
    summaries: list[tuple[Sale, int, Decimal]] = []
    for sale in sales:
        item_count = len(sale.items)
        total = sum(item.price_at_sale * item.quantity for item in sale.items)
        summaries.append((sale, item_count, total))
    return customer, summaries


async def create_customer(db: AsyncSession, payload: CustomerCreate) -> Customer:
    customer = Customer(
        name=payload.name.strip(),
        phone=_normalize_optional(payload.phone),
        email=_normalize_optional(str(payload.email) if payload.email else None),
        notes=_normalize_optional(payload.notes),
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


async def update_customer(
    db: AsyncSession,
    customer: Customer,
    payload: CustomerUpdate,
) -> Customer:
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    if "phone" in data:
        data["phone"] = _normalize_optional(data["phone"])
    if "email" in data:
        email = data["email"]
        data["email"] = _normalize_optional(str(email) if email else None)
    if "notes" in data:
        data["notes"] = _normalize_optional(data["notes"])
    for key, value in data.items():
        setattr(customer, key, value)
    await db.commit()
    await db.refresh(customer)
    return customer


async def delete_customer(db: AsyncSession, customer: Customer) -> None:
    await db.delete(customer)
    await db.commit()


async def count_customer_sales(db: AsyncSession, customer_id: int) -> int:
    result = await db.execute(
        select(func.count()).select_from(Sale).where(Sale.customer_id == customer_id),
    )
    return result.scalar_one()
