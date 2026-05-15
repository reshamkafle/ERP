from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PosProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    barcode: str | None
    price: Decimal
    stock: int
    low_stock_threshold: int


class PosProductListResponse(BaseModel):
    items: list[PosProductRead]
    total: int


class SaleItemLineCreate(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)


class SaleCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleItemLineCreate] = Field(min_length=1)


class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    price_at_sale: Decimal
    line_total: Decimal


class SaleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int | None
    customer_name: str | None = None
    cashier_email: str | None = None
    created_at: datetime
    items: list[SaleItemRead]
    subtotal: Decimal
    tax: Decimal
    total: Decimal


class SaleListItem(BaseModel):
    id: int
    customer_id: int | None
    customer_name: str | None
    cashier_email: str | None
    created_at: datetime
    item_count: int
    total: Decimal


class SaleListResponse(BaseModel):
    items: list[SaleListItem]
    total: int
