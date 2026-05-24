from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class BankDetailsSchema(BaseModel):
    account_number: str | None = None
    ifsc: str | None = None
    swift: str | None = None
    beneficiary_name: str | None = None


class VendorDocumentsSchema(BaseModel):
    w9: str | None = None
    certificate_of_incorporation: str | None = None
    insurance: str | None = None
    other: str | None = None


class SupplierBase(BaseModel):
    vendor_code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    dba: str | None = Field(default=None, max_length=255)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    payment_terms: str | None = Field(default=None, max_length=120)
    incoterms: str | None = Field(default=None, max_length=32)
    bank_details: BankDetailsSchema | dict[str, Any] | None = None
    vendor_category: str | None = Field(default=None, max_length=64)
    vendor_type: str | None = Field(default=None, max_length=64)
    approval_status: str | None = Field(default=None, max_length=32)
    performance_rating: Decimal | None = Field(default=None, ge=0, le=100)
    lead_time_days: int | None = Field(default=None, ge=0)
    moq: Decimal | None = Field(default=None, ge=0)
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    pricing_currency: str | None = Field(default=None, min_length=3, max_length=3)
    documents: VendorDocumentsSchema | dict[str, Any] | None = None

    @field_validator("vendor_code")
    @classmethod
    def normalize_vendor_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("currency_code", "pricing_currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    vendor_code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    dba: str | None = Field(default=None, max_length=255)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=32)
    country: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    payment_terms: str | None = Field(default=None, max_length=120)
    incoterms: str | None = Field(default=None, max_length=32)
    bank_details: BankDetailsSchema | dict[str, Any] | None = None
    vendor_category: str | None = Field(default=None, max_length=64)
    vendor_type: str | None = Field(default=None, max_length=64)
    approval_status: str | None = Field(default=None, max_length=32)
    performance_rating: Decimal | None = Field(default=None, ge=0, le=100)
    lead_time_days: int | None = Field(default=None, ge=0)
    moq: Decimal | None = Field(default=None, ge=0)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)
    pricing_currency: str | None = Field(default=None, min_length=3, max_length=3)
    documents: VendorDocumentsSchema | dict[str, Any] | None = None

    @field_validator("vendor_code")
    @classmethod
    def normalize_vendor_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("currency_code", "pricing_currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_code: str
    name: str
    legal_name: str | None
    dba: str | None
    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None
    phone: str | None
    email: str | None
    website: str | None
    tax_id: str | None
    payment_terms: str | None
    incoterms: str | None
    bank_details: dict[str, Any] | None
    vendor_category: str | None
    vendor_type: str | None
    approval_status: str | None
    performance_rating: Decimal | None
    lead_time_days: int | None
    moq: Decimal | None
    currency_code: str
    pricing_currency: str | None
    documents: dict[str, Any] | None


class SupplierListItem(SupplierRead):
    total_spent: Decimal
    purchase_count: int


class SupplierListResponse(BaseModel):
    items: list[SupplierListItem]
    total: int


class SupplierPurchaseSummary(BaseModel):
    id: int
    created_at: datetime
    item_count: int
    total: Decimal


class SupplierDetailRead(SupplierRead):
    total_spent: Decimal
    purchase_count: int
    recent_purchases: list[SupplierPurchaseSummary]
