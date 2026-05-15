from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    notes: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    notes: str | None = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str | None
    email: str | None
    notes: str | None


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    total: int


class CustomerSaleSummary(BaseModel):
    id: int
    created_at: datetime
    item_count: int
    total: Decimal


class CustomerDetailRead(CustomerRead):
    recent_sales: list[CustomerSaleSummary]
