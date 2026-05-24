from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


async def generate_customer_code(db: AsyncSession, *, as_of: date | None = None) -> str:
    day = (as_of or date.today()).strftime("%Y%m%d")
    prefix = f"CUST-{day}-"
    result = await db.execute(
        select(func.count())
        .select_from(Customer)
        .where(Customer.customer_code.like(f"{prefix}%")),
    )
    seq = int(result.scalar_one()) + 1
    return f"{prefix}{seq:03d}"
