from __future__ import annotations

from typing import Any

from app.models.customer import Customer
from app.models.enums import SalePartnerRole
from app.models.sale import Sale, SalePartner
from app.schemas.sale import AddressBlock, SalePartnerCreate
from app.services.customer_snapshot import snapshot_from_customer


def _address_to_json(address: AddressBlock | None) -> dict[str, Any] | None:
    if address is None:
        return None
    return address.model_dump(mode="json", exclude_none=True)


def default_partners_from_customer(customer: Customer) -> list[SalePartnerCreate]:
    snapshot = snapshot_from_customer(customer)
    billing = snapshot.billing_address
    shipping = snapshot.shipping_address
    return [
        SalePartnerCreate(role=SalePartnerRole.SOLD_TO, customer_id=customer.id),
        SalePartnerCreate(
            role=SalePartnerRole.BILL_TO,
            customer_id=customer.id,
            address=billing,
        ),
        SalePartnerCreate(
            role=SalePartnerRole.SHIP_TO,
            customer_id=customer.id,
            address=shipping,
        ),
        SalePartnerCreate(role=SalePartnerRole.PAYER, customer_id=customer.id),
    ]


def apply_partners_to_sale(
    sale: Sale,
    partners: list[SalePartnerCreate] | None,
    *,
    customer: Customer | None,
) -> None:
    for existing in list(sale.partners):
        sale.partners.remove(existing)

    rows = list(partners) if partners else []
    if customer is not None:
        if not rows:
            rows = default_partners_from_customer(customer)
        elif not any(r.role == SalePartnerRole.SOLD_TO for r in rows):
            rows.insert(0, SalePartnerCreate(role=SalePartnerRole.SOLD_TO, customer_id=customer.id))

    if not rows:
        return

    for row in rows:
        sale.partners.append(
            SalePartner(
                role=row.role,
                customer_id=row.customer_id,
                supplier_id=row.supplier_id,
                user_id=row.user_id,
                name_override=row.name_override,
                address=_address_to_json(row.address),
            ),
        )

    if sale.salesperson_id:
        has_sales_employee = any(p.role == SalePartnerRole.SALES_EMPLOYEE for p in sale.partners)
        if not has_sales_employee:
            sale.partners.append(
                SalePartner(
                    role=SalePartnerRole.SALES_EMPLOYEE,
                    user_id=sale.salesperson_id,
                ),
            )
