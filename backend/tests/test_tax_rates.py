from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tax_rate as tax_rate_crud
from app.schemas.tax import TaxRateCreate
from app.services.tax_calculation import get_company_settings


@pytest.mark.asyncio
async def test_create_and_resolve_tax_rate(db_session: AsyncSession) -> None:
    await get_company_settings(db_session)
    await db_session.commit()

    import uuid

    code = f"VAT-13-{uuid.uuid4().hex[:6]}"
    row = await tax_rate_crud.create_tax_rate(
        db_session,
        TaxRateCreate(
            code=code,
            name="VAT 13%",
            rate_percent=Decimal("13"),
            country_code="US",
            effective_from=date(2020, 1, 1),
        ),
    )
    assert row.code == code

    active = await tax_rate_crud.get_active_tax_rate(
        db_session,
        code=code,
        country_code="US",
        as_of=date.today(),
    )
    assert active is not None
    assert active.rate_percent == Decimal("13")
