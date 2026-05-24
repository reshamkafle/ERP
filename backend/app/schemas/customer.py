from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import CustomerAddressType, CustomerSegment, CustomerStatus, CustomerType
from app.schemas.crm import CustomerContactCreate, CustomerContactRead


class BankDetails(BaseModel):
    bank_name: str | None = None
    account_number: str | None = None
    iban: str | None = None
    swift: str | None = None


class IntegrationIds(BaseModel):
    crm_id: str | None = None
    ecommerce_id: str | None = None
    legacy_id: str | None = None


class ConsentFlags(BaseModel):
    marketing: bool = False
    gdpr: bool = False
    ccpa: bool = False


class CustomFieldEntry(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    value: str | None = None


class LoyaltyData(BaseModel):
    tier: str | None = None
    points: int | None = None


class MarketingData(BaseModel):
    journey_stage: str | None = None
    last_marketing_touch: datetime | None = None
    campaign_membership: str | None = None
    email_opt_in: bool | None = None
    marketing_source: str | None = None


class AnalyticsData(BaseModel):
    churn_risk_score: Decimal | None = None
    behavior_tags: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)


class ServiceData(BaseModel):
    contract_number: str | None = None
    sla_tier: str | None = None
    last_csat: Decimal | None = None
    last_nps: int | None = None
    last_service_date: date | None = None
    warranty_info: str | None = None
    installed_base: str | None = None


class ExtendedData(BaseModel):
    integration_ids: IntegrationIds | None = None
    consent_flags: ConsentFlags | None = None
    custom_fields: list[CustomFieldEntry] = Field(default_factory=list)
    risk_rating: str | None = None
    loyalty: LoyaltyData | None = None
    marketing: MarketingData | None = None
    analytics: AnalyticsData | None = None
    service: ServiceData | None = None


class CustomerAddressBase(BaseModel):
    address_type: CustomerAddressType
    label: str | None = Field(default=None, max_length=64)
    line1: str | None = Field(default=None, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    house_no: str | None = Field(default=None, max_length=32)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default=None, max_length=64)
    is_default: bool = False
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class CustomerAddressCreate(CustomerAddressBase):
    pass


class CustomerAddressRead(CustomerAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    created_at: datetime


class CustomerSalesAreaBase(BaseModel):
    sales_org: str = Field(min_length=1, max_length=64)
    distribution_channel: str | None = Field(default=None, max_length=64)
    division: str | None = Field(default=None, max_length=64)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    payment_terms: str | None = Field(default=None, max_length=120)
    pricing_procedure: str | None = Field(default=None, max_length=120)
    partner_functions: dict[str, Any] | None = None


class CustomerSalesAreaCreate(CustomerSalesAreaBase):
    pass


class CustomerSalesAreaRead(CustomerSalesAreaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    customer_code: str | None = Field(default=None, max_length=32)
    legal_name: str | None = Field(default=None, max_length=255)
    trade_name: str | None = Field(default=None, max_length=255)
    search_terms: str | None = Field(default=None, max_length=255)
    status: CustomerStatus | None = None
    customer_type: CustomerType | None = None
    parent_customer_id: int | None = None
    phone: str | None = Field(default=None, max_length=64)
    mobile_phone: str | None = Field(default=None, max_length=64)
    fax: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=64)
    contact_email: EmailStr | None = None
    timezone: str | None = Field(default=None, max_length=64)
    language: str | None = Field(default=None, max_length=64)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    billing_address_line1: str | None = Field(default=None, max_length=255)
    billing_address_line2: str | None = Field(default=None, max_length=255)
    billing_city: str | None = Field(default=None, max_length=120)
    billing_state: str | None = Field(default=None, max_length=120)
    billing_postal_code: str | None = Field(default=None, max_length=32)
    billing_country: str | None = Field(default=None, max_length=64)
    shipping_address_line1: str | None = Field(default=None, max_length=255)
    shipping_address_line2: str | None = Field(default=None, max_length=255)
    shipping_city: str | None = Field(default=None, max_length=120)
    shipping_state: str | None = Field(default=None, max_length=120)
    shipping_postal_code: str | None = Field(default=None, max_length=32)
    shipping_country: str | None = Field(default=None, max_length=64)
    industry: str | None = Field(default=None, max_length=120)
    company_size: str | None = Field(default=None, max_length=64)
    annual_revenue: Decimal | None = Field(default=None, ge=0)
    website: str | None = Field(default=None, max_length=255)
    segment: CustomerSegment | None = None
    customer_group: str | None = Field(default=None, max_length=64)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    credit_status: str | None = Field(default=None, max_length=32)
    payment_terms: str | None = Field(default=None, max_length=120)
    reconciliation_account_id: int | None = None
    tax_id: str | None = Field(default=None, max_length=64)
    tax_registration_type: str | None = Field(default=None, max_length=64)
    tax_classification: str | None = Field(default=None, max_length=64)
    tax_exempt: bool | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    vat_number: str | None = Field(default=None, max_length=64)
    billing_preference: str | None = Field(default=None, max_length=64)
    bank_details: BankDetails | dict[str, Any] | None = None
    dunning_procedure: str | None = Field(default=None, max_length=120)
    withholding_tax: str | None = Field(default=None, max_length=64)
    incoterms: str | None = Field(default=None, max_length=32)
    currency_code: str = Field(default="USD", max_length=3)
    sales_rep: str | None = Field(default=None, max_length=120)
    price_group: str | None = Field(default=None, max_length=64)
    shipping_conditions: str | None = Field(default=None, max_length=120)
    delivering_plant: str | None = Field(default=None, max_length=120)
    order_probability: Decimal | None = Field(default=None, ge=0, le=100)
    lead_source: str | None = Field(default=None, max_length=120)
    year_founded: int | None = Field(default=None, ge=1800, le=2100)
    ownership_type: str | None = Field(default=None, max_length=64)
    territory: str | None = Field(default=None, max_length=120)
    employee_count: int | None = Field(default=None, ge=0)
    account_owner_id: int | None = None
    shipping_preference: str | None = Field(default=None, max_length=120)
    preferred_carrier: str | None = Field(default=None, max_length=120)
    receiving_hours: str | None = Field(default=None, max_length=255)
    freight_terms: str | None = Field(default=None, max_length=120)
    transport_zone: str | None = Field(default=None, max_length=64)
    extended_data: ExtendedData | dict[str, Any] | None = None
    notes: str | None = None


class CustomerCreate(CustomerBase):
    contacts: list[CustomerContactCreate] = Field(default_factory=list)
    addresses: list[CustomerAddressCreate] = Field(default_factory=list)
    sales_areas: list[CustomerSalesAreaCreate] = Field(default_factory=list)


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_code: str | None = Field(default=None, max_length=32)
    legal_name: str | None = Field(default=None, max_length=255)
    trade_name: str | None = Field(default=None, max_length=255)
    search_terms: str | None = Field(default=None, max_length=255)
    status: CustomerStatus | None = None
    customer_type: CustomerType | None = None
    parent_customer_id: int | None = None
    phone: str | None = Field(default=None, max_length=64)
    mobile_phone: str | None = Field(default=None, max_length=64)
    fax: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=64)
    contact_email: EmailStr | None = None
    timezone: str | None = Field(default=None, max_length=64)
    language: str | None = Field(default=None, max_length=64)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    billing_address_line1: str | None = Field(default=None, max_length=255)
    billing_address_line2: str | None = Field(default=None, max_length=255)
    billing_city: str | None = Field(default=None, max_length=120)
    billing_state: str | None = Field(default=None, max_length=120)
    billing_postal_code: str | None = Field(default=None, max_length=32)
    billing_country: str | None = Field(default=None, max_length=64)
    shipping_address_line1: str | None = Field(default=None, max_length=255)
    shipping_address_line2: str | None = Field(default=None, max_length=255)
    shipping_city: str | None = Field(default=None, max_length=120)
    shipping_state: str | None = Field(default=None, max_length=120)
    shipping_postal_code: str | None = Field(default=None, max_length=32)
    shipping_country: str | None = Field(default=None, max_length=64)
    industry: str | None = Field(default=None, max_length=120)
    company_size: str | None = Field(default=None, max_length=64)
    annual_revenue: Decimal | None = Field(default=None, ge=0)
    website: str | None = Field(default=None, max_length=255)
    segment: CustomerSegment | None = None
    customer_group: str | None = Field(default=None, max_length=64)
    credit_limit: Decimal | None = Field(default=None, ge=0)
    credit_status: str | None = Field(default=None, max_length=32)
    payment_terms: str | None = Field(default=None, max_length=120)
    reconciliation_account_id: int | None = None
    tax_id: str | None = Field(default=None, max_length=64)
    tax_registration_type: str | None = Field(default=None, max_length=64)
    tax_classification: str | None = Field(default=None, max_length=64)
    tax_exempt: bool | None = None
    gst_number: str | None = Field(default=None, max_length=64)
    vat_number: str | None = Field(default=None, max_length=64)
    billing_preference: str | None = Field(default=None, max_length=64)
    bank_details: BankDetails | dict[str, Any] | None = None
    dunning_procedure: str | None = Field(default=None, max_length=120)
    withholding_tax: str | None = Field(default=None, max_length=64)
    incoterms: str | None = Field(default=None, max_length=32)
    currency_code: str | None = Field(default=None, max_length=3)
    sales_rep: str | None = Field(default=None, max_length=120)
    price_group: str | None = Field(default=None, max_length=64)
    shipping_conditions: str | None = Field(default=None, max_length=120)
    delivering_plant: str | None = Field(default=None, max_length=120)
    order_probability: Decimal | None = Field(default=None, ge=0, le=100)
    lead_source: str | None = Field(default=None, max_length=120)
    year_founded: int | None = Field(default=None, ge=1800, le=2100)
    ownership_type: str | None = Field(default=None, max_length=64)
    territory: str | None = Field(default=None, max_length=120)
    employee_count: int | None = Field(default=None, ge=0)
    account_owner_id: int | None = None
    shipping_preference: str | None = Field(default=None, max_length=120)
    preferred_carrier: str | None = Field(default=None, max_length=120)
    receiving_hours: str | None = Field(default=None, max_length=255)
    freight_terms: str | None = Field(default=None, max_length=120)
    transport_zone: str | None = Field(default=None, max_length=64)
    extended_data: ExtendedData | dict[str, Any] | None = None
    notes: str | None = None
    contacts: list[CustomerContactCreate] | None = None
    addresses: list[CustomerAddressCreate] | None = None
    sales_areas: list[CustomerSalesAreaCreate] | None = None


class CustomerReadBase(BaseModel):
    """Scalar customer fields — safe for list endpoints without eager-loaded relations."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_code: str | None
    name: str
    legal_name: str | None
    trade_name: str | None
    search_terms: str | None
    status: CustomerStatus | None
    customer_type: CustomerType | None
    parent_customer_id: int | None
    phone: str | None
    mobile_phone: str | None
    fax: str | None
    email: str | None
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    timezone: str | None
    language: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    billing_address_line1: str | None
    billing_address_line2: str | None
    billing_city: str | None
    billing_state: str | None
    billing_postal_code: str | None
    billing_country: str | None
    shipping_address_line1: str | None
    shipping_address_line2: str | None
    shipping_city: str | None
    shipping_state: str | None
    shipping_postal_code: str | None
    shipping_country: str | None
    industry: str | None
    company_size: str | None
    annual_revenue: Decimal | None
    website: str | None
    segment: CustomerSegment | None
    customer_group: str | None
    credit_limit: Decimal | None
    credit_status: str | None
    payment_terms: str | None
    reconciliation_account_id: int | None
    tax_id: str | None
    tax_registration_type: str | None
    tax_classification: str | None
    tax_exempt: bool | None
    gst_number: str | None
    vat_number: str | None
    billing_preference: str | None
    bank_details: dict[str, Any] | None
    dunning_procedure: str | None
    withholding_tax: str | None
    incoterms: str | None
    currency_code: str
    sales_rep: str | None
    price_group: str | None
    shipping_conditions: str | None
    delivering_plant: str | None
    order_probability: Decimal | None
    lead_source: str | None
    shipping_preference: str | None
    preferred_carrier: str | None
    receiving_hours: str | None
    freight_terms: str | None
    transport_zone: str | None
    year_founded: int | None
    ownership_type: str | None
    territory: str | None
    employee_count: int | None
    account_owner_id: int | None
    extended_data: dict[str, Any] | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CustomerRead(CustomerReadBase):
    contacts: list[CustomerContactRead] = Field(default_factory=list)
    addresses: list[CustomerAddressRead] = Field(default_factory=list)
    sales_areas: list[CustomerSalesAreaRead] = Field(default_factory=list)


CustomerListItem = CustomerReadBase


class CustomerListResponse(BaseModel):
    items: list[CustomerListItem]
    total: int


class CustomerSaleSummary(BaseModel):
    id: int
    order_number: str
    created_at: datetime
    item_count: int
    total: Decimal
    order_status: str


class CustomerDetailRead(CustomerRead):
    recent_sales: list[CustomerSaleSummary]


class CustomerOverviewRead(BaseModel):
    customer_id: int
    total_revenue: Decimal
    lifetime_value: Decimal
    revenue_ytd: Decimal
    revenue_last_year: Decimal
    open_balance: Decimal
    open_receivables: Decimal
    sale_count: int
    last_purchase_date: datetime | None
    average_order_value: Decimal
    purchase_frequency_per_year: Decimal
    open_opportunity_count: int
    open_opportunity_value: Decimal
    activity_count: int
    contact_count: int
    document_count: int
    payment_count: int


class CustomerAuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    user_id: int | None
    field_name: str
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    change_summary: str | None
    created_at: datetime
