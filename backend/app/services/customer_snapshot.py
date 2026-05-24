from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.models.customer import Customer
from app.schemas.sale import AddressBlock, CustomerSnapshot


def _address(
    line1: str | None,
    line2: str | None,
    city: str | None,
    state: str | None,
    postal: str | None,
    country: str | None,
) -> AddressBlock | None:
    if not any((line1, line2, city, state, postal, country)):
        return None
    return AddressBlock(
        line1=line1,
        line2=line2,
        city=city,
        state=state,
        postal_code=postal,
        country=country,
    )


def snapshot_from_customer(customer: Customer) -> CustomerSnapshot:
    return CustomerSnapshot(
        customer_id=customer.id,
        customer_code=customer.customer_code,
        name=customer.name,
        billing_address=_address(
            customer.billing_address_line1,
            customer.billing_address_line2,
            customer.billing_city,
            customer.billing_state,
            customer.billing_postal_code,
            customer.billing_country,
        ),
        shipping_address=_address(
            customer.shipping_address_line1,
            customer.shipping_address_line2,
            customer.shipping_city,
            customer.shipping_state,
            customer.shipping_postal_code,
            customer.shipping_country,
        ),
        contact_name=customer.contact_name,
        contact_phone=customer.contact_phone or customer.phone,
        contact_email=customer.contact_email or customer.email,
        customer_group=customer.customer_group,
        credit_limit=customer.credit_limit,
        credit_status=customer.credit_status,
        payment_terms=customer.payment_terms,
        tax_id=customer.tax_id,
        shipping_preference=customer.shipping_preference,
        incoterms=customer.incoterms,
        trade_name=customer.trade_name,
        status=customer.status.value if customer.status else None,
        gst_number=customer.gst_number,
        vat_number=customer.vat_number,
        currency_code=customer.currency_code,
    )


def snapshot_to_json(snapshot: CustomerSnapshot | None) -> dict[str, Any] | None:
    if snapshot is None:
        return None
    return snapshot.model_dump(mode="json", exclude_none=True)


def json_to_dict(model: Any) -> dict[str, Any] | None:
    if model is None:
        return None
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json", exclude_none=True)
    return model
