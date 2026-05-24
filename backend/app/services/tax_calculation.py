from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tax_rate as tax_rate_crud
from app.models.company_settings import CompanySettings
from app.models.product import Product
from sqlalchemy import select


async def get_company_settings(db: AsyncSession) -> CompanySettings:
    result = await db.execute(select(CompanySettings).limit(1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = CompanySettings()
        db.add(settings)
        await db.flush()
    return settings


async def line_tax_amount(
    db: AsyncSession,
    *,
    product: Product,
    line_subtotal: Decimal,
    as_of: date | None = None,
) -> Decimal:
    if not product.tax_code:
        return Decimal("0")
    settings = await get_company_settings(db)
    rate_row = await tax_rate_crud.get_active_tax_rate(
        db,
        code=product.tax_code,
        country_code=settings.country_code,
        as_of=as_of or date.today(),
    )
    if rate_row is None:
        return Decimal("0")
    return (line_subtotal * rate_row.rate_percent / Decimal("100")).quantize(Decimal("0.01"))


async def compute_sale_totals(
    db: AsyncSession,
    *,
    line_subtotals: list[tuple[Product, Decimal]],
    as_of: date | None = None,
) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for product, line_sub in line_subtotals:
        subtotal += line_sub
        tax_total += await line_tax_amount(db, product=product, line_subtotal=line_sub, as_of=as_of)
    total = subtotal + tax_total
    return subtotal, tax_total, total
