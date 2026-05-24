from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CustomerSegment, CustomerStatus, CustomerType

if TYPE_CHECKING:
    from app.models.chart_of_account import ChartOfAccount
    from app.models.crm import CrmActivity, CrmLead, CrmOpportunity, CustomerContact
    from app.models.customer_address import CustomerAddress
    from app.models.customer_sales_area import CustomerSalesArea
    from app.models.sale import Sale


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_code: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trade_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    search_terms: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[CustomerStatus | None] = mapped_column(
        Enum(CustomerStatus, name="customerstatus", create_constraint=False),
        nullable=True,
    )
    customer_type: Mapped[CustomerType | None] = mapped_column(
        Enum(CustomerType, name="customertype", create_constraint=False),
        nullable=True,
    )
    parent_customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mobile_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(64), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)

    billing_address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    billing_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    billing_postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    billing_country: Mapped[str | None] = mapped_column(String(64), nullable=True)

    shipping_address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipping_address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    shipping_country: Mapped[str | None] = mapped_column(String(64), nullable=True)

    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(64), nullable=True)
    annual_revenue: Mapped[Decimal | None] = mapped_column(Numeric(16, 2), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    segment: Mapped[CustomerSegment | None] = mapped_column(
        Enum(CustomerSegment, name="customersegment", create_constraint=False),
        nullable=True,
    )
    customer_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    credit_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reconciliation_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("chart_of_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    tax_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tax_registration_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tax_classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tax_exempt: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    gst_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vat_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    billing_preference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bank_details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    dunning_procedure: Mapped[str | None] = mapped_column(String(120), nullable=True)
    withholding_tax: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incoterms: Mapped[str | None] = mapped_column(String(32), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    sales_rep: Mapped[str | None] = mapped_column(String(120), nullable=True)
    price_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shipping_conditions: Mapped[str | None] = mapped_column(String(120), nullable=True)
    delivering_plant: Mapped[str | None] = mapped_column(String(120), nullable=True)
    order_probability: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    lead_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year_founded: Mapped[int | None] = mapped_column(nullable=True)
    ownership_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    territory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(nullable=True)
    account_owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipping_preference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    preferred_carrier: Mapped[str | None] = mapped_column(String(120), nullable=True)
    receiving_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    freight_terms: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transport_zone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extended_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    parent_customer: Mapped[Customer | None] = relationship(
        remote_side="Customer.id",
        foreign_keys=[parent_customer_id],
    )
    reconciliation_account: Mapped[ChartOfAccount | None] = relationship(
        foreign_keys=[reconciliation_account_id],
    )
    sales: Mapped[list[Sale]] = relationship(back_populates="customer")
    contacts: Mapped[list[CustomerContact]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    addresses: Mapped[list[CustomerAddress]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    sales_areas: Mapped[list[CustomerSalesArea]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list[CrmActivity]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    leads: Mapped[list[CrmLead]] = relationship(back_populates="customer")
    opportunities: Mapped[list[CrmOpportunity]] = relationship(back_populates="customer")
