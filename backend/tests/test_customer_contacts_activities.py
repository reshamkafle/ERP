from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crm as crm_crud
from app.crud import customer as customer_crud
from app.models.enums import CrmActivityType
from app.schemas.crm import CrmActivityCreate, CustomerContactCreate
from app.schemas.customer import CustomerCreate


@pytest.mark.asyncio
async def test_contacts_timeline_order(db_session: AsyncSession) -> None:
    from app.core.database import init_db

    await init_db()

    customer = await customer_crud.create_customer(
        db_session,
        CustomerCreate(name="Timeline Customer"),
    )

    await crm_crud.create_activity(
        db_session,
        customer.id,
        CrmActivityCreate(
            activity_type=CrmActivityType.NOTE,
            subject="Older note",
            occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
    )
    await crm_crud.create_activity(
        db_session,
        customer.id,
        CrmActivityCreate(
            activity_type=CrmActivityType.EMAIL,
            subject="Newer email",
            occurred_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
        ),
    )

    activities = await crm_crud.list_activities_for_customer(db_session, customer.id)
    assert len(activities) == 2
    assert activities[0].subject == "Newer email"

    contact = await crm_crud.create_contact(
        db_session,
        customer.id,
        CustomerContactCreate(name="Primary", is_primary=True),
    )
    contacts = await crm_crud.list_contacts_for_customer(db_session, customer.id)
    assert contacts[0].id == contact.id
    assert contacts[0].is_primary is True

    named = await crm_crud.create_contact(
        db_session,
        customer.id,
        CustomerContactCreate(
            salutation="Ms",
            first_name="Alex",
            last_name="Rivera",
            email="alex@example.com",
            phone_secondary="+15551234",
        ),
    )
    assert named.name == "Ms Alex Rivera"

    await crm_crud.create_activity(
        db_session,
        customer.id,
        CrmActivityCreate(
            activity_type=CrmActivityType.CALL,
            subject="Discovery call",
            occurred_at=datetime(2026, 5, 2, tzinfo=timezone.utc),
            duration_minutes=30,
            outcome="Positive",
        ),
    )
    latest = await crm_crud.list_activities_for_customer(db_session, customer.id)
    assert latest[0].duration_minutes == 30
