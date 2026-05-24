from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import customer as customer_crud
from app.schemas.customer import CustomerCreate
from app.services.customer_overview import build_customer_overview


@pytest.mark.asyncio
@pytest.mark.integration
async def test_customer_overview_extended_metrics(seeded_db: AsyncSession) -> None:
    customer = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(
            name="Overview Metrics Co",
            customer_code="OVW-001",
            year_founded=2010,
            territory="West",
            employee_count=120,
        ),
    )
    overview = await build_customer_overview(seeded_db, customer.id)
    assert overview.customer_id == customer.id
    assert overview.lifetime_value == overview.total_revenue
    assert overview.sale_count >= 0
    assert overview.average_order_value >= Decimal("0")
    assert overview.purchase_frequency_per_year >= Decimal("0")
