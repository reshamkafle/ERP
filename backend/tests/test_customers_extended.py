import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import customer as customer_crud
from app.models.customer import Customer
from app.models.enums import CustomerAddressType, CustomerStatus, CustomerType
from app.schemas.crm import CustomerContactCreate
from app.schemas.customer import (
    CustomerAddressCreate,
    CustomerCreate,
    CustomerListItem,
    CustomerUpdate,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_customer_item_does_not_lazy_load_relations(seeded_db: AsyncSession) -> None:
    """List serialization must not touch unloaded ORM relationships (async MissingGreenlet)."""
    result = await seeded_db.execute(select(Customer).limit(1))
    customer = result.scalar_one_or_none()
    if customer is None:
        pytest.skip("No customers in seed data")
    item = CustomerListItem.model_validate(customer)
    assert item.id == customer.id
    assert item.name == customer.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_customer_with_commercial_fields(seeded_db: AsyncSession) -> None:
    customer = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(
            name="Acme Retail",
            customer_code="ACME-001",
            customer_group="Wholesale",
            payment_terms="Net 30",
            tax_id="TAX-123",
            credit_limit="50000",
            billing_address_line1="1 Main St",
            billing_city="Boston",
            billing_country="US",
            currency_code="USD",
        ),
    )
    assert customer.customer_code == "ACME-001"
    assert customer.payment_terms == "Net 30"
    assert customer.credit_limit == 50000

    updated = await customer_crud.update_customer(
        seeded_db,
        customer,
        CustomerUpdate(credit_status="GOOD", shipping_preference="Truck"),
    )
    assert updated.credit_status == "GOOD"
    assert updated.shipping_preference == "Truck"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_customer_phase1_fields_and_auto_code(seeded_db: AsyncSession) -> None:
    parent = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(name="Parent Corp", customer_code="PARENT-01", status=CustomerStatus.ACTIVE),
    )
    child = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(
            name="Child Unit",
            customer_type=CustomerType.COMPANY,
            trade_name="Child DBA",
            search_terms="CHILD",
            status=CustomerStatus.PROSPECT,
            parent_customer_id=parent.id,
            bank_details={
                "bank_name": "First National",
                "account_number": "12345",
                "iban": "US00TEST",
                "swift": "FNBKUS",
            },
            extended_data={"risk_rating": "A", "consent_flags": {"marketing": True}},
        ),
    )
    assert child.customer_code.startswith("CUST-")
    assert child.trade_name == "Child DBA"
    assert child.parent_customer_id == parent.id
    assert child.bank_details["bank_name"] == "First National"
    assert child.extended_data["risk_rating"] == "A"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_customer_crm_account_fields(seeded_db: AsyncSession) -> None:
    customer = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(
            name="CRM Account Fields Ltd",
            customer_code="CRM-ACC-01",
            year_founded=2005,
            ownership_type="PRIVATE",
            territory="EMEA",
            employee_count=250,
            extended_data={
                "marketing": {"journey_stage": "Consideration", "email_opt_in": True},
                "analytics": {"churn_risk_score": 0.15, "behavior_tags": ["bulk"], "labels": ["VIP"]},
                "service": {"sla_tier": "Gold", "contract_number": "SVC-100"},
            },
        ),
    )
    assert customer.year_founded == 2005
    assert customer.territory == "EMEA"
    assert customer.extended_data["marketing"]["journey_stage"] == "Consideration"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_customer_with_contacts_and_addresses(seeded_db: AsyncSession) -> None:
    customer = await customer_crud.create_customer(
        seeded_db,
        CustomerCreate(
            name="Multi Contact Co",
            customer_code="MULTI-01",
            contacts=[
                CustomerContactCreate(
                    name="Jane Buyer",
                    title="Purchasing",
                    department="Procurement",
                    email="jane@example.com",
                    is_primary=True,
                ),
            ],
            addresses=[
                CustomerAddressCreate(
                    address_type=CustomerAddressType.BILLING,
                    line1="100 Bill St",
                    city="NYC",
                    country="US",
                    is_default=True,
                ),
                CustomerAddressCreate(
                    address_type=CustomerAddressType.SHIPPING,
                    line1="200 Ship Ave",
                    city="NYC",
                    country="US",
                    is_default=True,
                ),
            ],
        ),
    )
    assert len(customer.contacts) == 1
    assert customer.contacts[0].name == "Jane Buyer"
    assert customer.contact_name == "Jane Buyer"
    assert len(customer.addresses) == 2
    assert customer.billing_address_line1 == "100 Bill St"
    assert customer.shipping_address_line1 == "200 Ship Ave"
