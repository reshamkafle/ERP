from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    notes: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    notes: str | None = None


class SupplierRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str | None
    email: str | None
    notes: str | None


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
