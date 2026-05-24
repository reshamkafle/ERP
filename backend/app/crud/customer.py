from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm import CustomerContact, build_contact_display_name
from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_sales_area import CustomerSalesArea
from app.models.enums import CustomerAddressType
from app.models.sale import Sale
from app.schemas.crm import CustomerContactCreate
from app.schemas.customer import (
    CustomerAddressCreate,
    CustomerCreate,
    CustomerSalesAreaCreate,
    CustomerUpdate,
)
from app.services.customer_address_sync import (
    sync_flat_addresses_from_rows,
    sync_primary_contact_from_rows,
)
from app.services.customer_audit import log_customer_changes
from app.services.customer_number import generate_customer_code


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _json_field(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, dict):
        return value
    return None


def _customer_scalar_data(
    payload: CustomerCreate | CustomerUpdate,
    *,
    exclude_unset: bool,
) -> dict[str, Any]:
    nested = {"contacts", "addresses", "sales_areas"}
    data = payload.model_dump(exclude_unset=exclude_unset, exclude=nested)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    str_keys = (
        "phone",
        "notes",
        "customer_code",
        "legal_name",
        "trade_name",
        "search_terms",
        "contact_name",
        "contact_phone",
        "mobile_phone",
        "fax",
        "timezone",
        "language",
        "industry",
        "company_size",
        "website",
        "customer_group",
        "credit_status",
        "payment_terms",
        "tax_id",
        "tax_registration_type",
        "tax_classification",
        "gst_number",
        "vat_number",
        "billing_preference",
        "incoterms",
        "shipping_preference",
        "dunning_procedure",
        "withholding_tax",
        "sales_rep",
        "price_group",
        "shipping_conditions",
        "delivering_plant",
        "lead_source",
        "preferred_carrier",
        "receiving_hours",
        "freight_terms",
        "transport_zone",
        "ownership_type",
        "territory",
    )
    for key in str_keys:
        if key in data:
            data[key] = _normalize_optional(data[key])
    for key in ("email", "contact_email"):
        if key in data:
            val = data[key]
            data[key] = _normalize_optional(str(val) if val else None)
    if "bank_details" in data:
        data["bank_details"] = _json_field(data["bank_details"])
    if "extended_data" in data:
        data["extended_data"] = _json_field(data["extended_data"])
    return data


def _apply_contacts(customer: Customer, contacts: list[CustomerContactCreate]) -> list[CustomerContact]:
    customer.contacts.clear()
    rows: list[CustomerContact] = []
    for item in contacts:
        row_data = item.model_dump()
        if row_data.get("email"):
            row_data["email"] = str(row_data["email"])
        if row_data.get("email_secondary"):
            row_data["email_secondary"] = str(row_data["email_secondary"])
        for key in (
            "phone",
            "phone_secondary",
            "role",
            "title",
            "department",
            "notes",
            "relationship_strength",
            "contact_code",
            "salutation",
            "first_name",
            "middle_name",
            "last_name",
            "linkedin_url",
            "preferred_language",
        ):
            if key in row_data and isinstance(row_data[key], str):
                row_data[key] = _normalize_optional(row_data[key])
        row_data["name"] = build_contact_display_name(
            salutation=row_data.get("salutation"),
            first_name=row_data.get("first_name"),
            middle_name=row_data.get("middle_name"),
            last_name=row_data.get("last_name"),
            fallback=row_data.get("name") or "Contact",
        )
        row = CustomerContact(customer_id=customer.id, **row_data)
        customer.contacts.append(row)
        rows.append(row)
    return rows


def _apply_addresses(customer: Customer, addresses: list[CustomerAddressCreate]) -> list[CustomerAddress]:
    customer.addresses.clear()
    rows: list[CustomerAddress] = []
    for item in addresses:
        row = CustomerAddress(customer_id=customer.id, **item.model_dump())
        customer.addresses.append(row)
        rows.append(row)
    return rows


def _apply_sales_areas(
    customer: Customer,
    areas: list[CustomerSalesAreaCreate],
) -> list[CustomerSalesArea]:
    customer.sales_areas.clear()
    rows: list[CustomerSalesArea] = []
    for item in areas:
        data = item.model_dump()
        if data.get("partner_functions") is not None and hasattr(
            data["partner_functions"],
            "model_dump",
        ):
            data["partner_functions"] = data["partner_functions"].model_dump(mode="json")
        row = CustomerSalesArea(customer_id=customer.id, **data)
        customer.sales_areas.append(row)
        rows.append(row)
    return rows


def _addresses_from_flat_data(data: dict[str, Any]) -> list[CustomerAddressCreate]:
    rows: list[CustomerAddressCreate] = []
    if any((data.get("billing_address_line1"), data.get("billing_city"), data.get("billing_country"))):
        rows.append(
            CustomerAddressCreate(
                address_type=CustomerAddressType.BILLING,
                line1=data.get("billing_address_line1"),
                line2=data.get("billing_address_line2"),
                city=data.get("billing_city"),
                state=data.get("billing_state"),
                postal_code=data.get("billing_postal_code"),
                country=data.get("billing_country"),
                is_default=True,
            ),
        )
    if any(
        (data.get("shipping_address_line1"), data.get("shipping_city"), data.get("shipping_country")),
    ):
        rows.append(
            CustomerAddressCreate(
                address_type=CustomerAddressType.SHIPPING,
                line1=data.get("shipping_address_line1"),
                line2=data.get("shipping_address_line2"),
                city=data.get("shipping_city"),
                state=data.get("shipping_state"),
                postal_code=data.get("shipping_postal_code"),
                country=data.get("shipping_country"),
                is_default=True,
            ),
        )
    return rows


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
            Customer.customer_code.ilike(pattern),
            Customer.legal_name.ilike(pattern),
            Customer.trade_name.ilike(pattern),
            Customer.search_terms.ilike(pattern),
            Customer.tax_id.ilike(pattern),
            Customer.gst_number.ilike(pattern),
            Customer.vat_number.ilike(pattern),
        )
        stmt = stmt.where(filter_expr)
        count_stmt = count_stmt.where(filter_expr)

    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(stmt.order_by(Customer.name).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def get_customer(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(
        select(Customer)
        .options(
            selectinload(Customer.contacts),
            selectinload(Customer.addresses),
            selectinload(Customer.sales_areas),
        )
        .where(Customer.id == customer_id),
    )
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
    data = _customer_scalar_data(payload, exclude_unset=False)
    if not data.get("customer_code"):
        data["customer_code"] = await generate_customer_code(db)

    contacts = payload.contacts
    addresses = payload.addresses if payload.addresses else _addresses_from_flat_data(data)
    sales_areas = payload.sales_areas

    customer = Customer(**data)
    db.add(customer)
    await db.flush()

    contact_rows = _apply_contacts(customer, contacts) if contacts else []
    address_rows = _apply_addresses(customer, addresses) if addresses else []
    if sales_areas:
        _apply_sales_areas(customer, sales_areas)
    if address_rows:
        sync_flat_addresses_from_rows(customer, address_rows)
    if contact_rows:
        sync_primary_contact_from_rows(customer, contact_rows)

    await db.commit()
    await db.refresh(customer)
    return await get_customer(db, customer.id) or customer


async def update_customer(
    db: AsyncSession,
    customer: Customer,
    payload: CustomerUpdate,
    *,
    user_id: int | None = None,
) -> Customer:
    old_snapshot = {
        k: getattr(customer, k)
        for k in customer.__table__.columns.keys()
        if k not in ("created_at", "updated_at")
    }

    data = _customer_scalar_data(payload, exclude_unset=True)
    for key, value in data.items():
        setattr(customer, key, value)

    if payload.contacts is not None:
        contact_rows = _apply_contacts(customer, payload.contacts)
        sync_primary_contact_from_rows(customer, contact_rows)
    if payload.addresses is not None:
        address_rows = _apply_addresses(customer, payload.addresses)
        sync_flat_addresses_from_rows(customer, address_rows)
    if payload.sales_areas is not None:
        _apply_sales_areas(customer, payload.sales_areas)

    new_snapshot = {
        k: getattr(customer, k)
        for k in customer.__table__.columns.keys()
        if k not in ("created_at", "updated_at")
    }
    await log_customer_changes(db, customer, old_snapshot, new_snapshot, user_id=user_id)

    await db.commit()
    refreshed = await get_customer(db, customer.id)
    return refreshed or customer


async def delete_customer(db: AsyncSession, customer: Customer) -> None:
    await db.delete(customer)
    await db.commit()


async def count_customer_sales(db: AsyncSession, customer_id: int) -> int:
    result = await db.execute(
        select(func.count()).select_from(Sale).where(Sale.customer_id == customer_id),
    )
    return result.scalar_one()
