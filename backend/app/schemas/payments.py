from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import (
    AllocationType,
    PartyType,
    PaymentDirection,
    PaymentStatus,
    PaymentType,
)


class PaymentMethodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    gl_account_id: int
    is_active: bool


class PaymentMethodListResponse(BaseModel):
    items: list[PaymentMethodRead]


class PaymentAllocationIn(BaseModel):
    allocation_type: AllocationType = AllocationType.INVOICE
    sale_id: int | None = Field(default=None, ge=1)
    purchase_id: int | None = Field(default=None, ge=1)
    allocated_amount: Decimal = Field(gt=0)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "PaymentAllocationIn":
        if self.allocation_type == AllocationType.OVERPAYMENT:
            return self
        has_sale = self.sale_id is not None
        has_purchase = self.purchase_id is not None
        if has_sale == has_purchase:
            raise ValueError("Exactly one of sale_id or purchase_id must be set")
        return self


class PaymentAllocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    allocation_type: AllocationType
    sale_id: int | None
    purchase_id: int | None
    allocated_amount: Decimal
    notes: str | None


class ReceivePaymentCreate(BaseModel):
    customer_id: int = Field(ge=1)
    payment_method_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0)
    payment_date: date
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    exchange_rate: Decimal | None = Field(default=None, gt=0)
    bank_account_id: int | None = Field(default=None, ge=1)
    reference: str | None = Field(default=None, max_length=128)
    notes: str | None = None
    erp_document_id: int | None = Field(default=None, ge=1)
    allocations: list[PaymentAllocationIn] = Field(default_factory=list)


class MakePaymentCreate(BaseModel):
    supplier_id: int = Field(ge=1)
    payment_method_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0)
    payment_date: date
    currency_code: str = Field(default="USD", min_length=3, max_length=3)
    exchange_rate: Decimal | None = Field(default=None, gt=0)
    bank_account_id: int | None = Field(default=None, ge=1)
    reference: str | None = Field(default=None, max_length=128)
    notes: str | None = None
    erp_document_id: int | None = Field(default=None, ge=1)
    allocations: list[PaymentAllocationIn] = Field(default_factory=list)


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_number: str
    direction: PaymentDirection
    payment_type: PaymentType
    status: PaymentStatus
    party_type: PartyType
    customer_id: int | None
    supplier_id: int | None
    party_name: str | None
    payment_method_id: int
    bank_account_id: int | None
    amount: Decimal
    currency_code: str
    exchange_rate: Decimal | None
    amount_base: Decimal | None
    payment_date: date
    reference: str | None
    notes: str | None
    journal_entry_id: int | None
    allocations: list[PaymentAllocationRead] = Field(default_factory=list)
    created_at: datetime
    confirmed_at: datetime | None


class PaymentListItem(BaseModel):
    id: int
    payment_number: str
    direction: PaymentDirection
    payment_type: PaymentType
    status: PaymentStatus
    amount: Decimal
    currency_code: str
    payment_date: date
    party_name: str | None


class PaymentListResponse(BaseModel):
    items: list[PaymentListItem]
    total: int


class OpenBalanceRead(BaseModel):
    document_id: int
    total: Decimal
    amount_paid: Decimal
    open_balance: Decimal
    payment_status: str
    currency_code: str
