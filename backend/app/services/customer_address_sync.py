from __future__ import annotations

from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.enums import CustomerAddressType


def sync_flat_addresses_from_rows(customer: Customer, addresses: list[CustomerAddress]) -> None:
    billing = next(
        (a for a in addresses if a.address_type == CustomerAddressType.BILLING and a.is_default),
        next((a for a in addresses if a.address_type == CustomerAddressType.BILLING), None),
    )
    shipping = next(
        (a for a in addresses if a.address_type == CustomerAddressType.SHIPPING and a.is_default),
        next((a for a in addresses if a.address_type == CustomerAddressType.SHIPPING), None),
    )
    if billing:
        customer.billing_address_line1 = billing.line1
        customer.billing_address_line2 = billing.line2
        customer.billing_city = billing.city
        customer.billing_state = billing.state
        customer.billing_postal_code = billing.postal_code
        customer.billing_country = billing.country
    if shipping:
        customer.shipping_address_line1 = shipping.line1
        customer.shipping_address_line2 = shipping.line2
        customer.shipping_city = shipping.city
        customer.shipping_state = shipping.state
        customer.shipping_postal_code = shipping.postal_code
        customer.shipping_country = shipping.country


def sync_primary_contact_from_rows(customer: Customer, contacts: list) -> None:
    primary = next((c for c in contacts if c.is_primary), contacts[0] if contacts else None)
    if primary is None:
        return
    customer.contact_name = primary.name
    customer.contact_phone = primary.phone
    customer.contact_email = primary.email
