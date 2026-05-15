from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    barcode: str | None
    cost_price: Decimal
    stock: int


class PurchaseProductListResponse(BaseModel):
    items: list[PurchaseProductRead]
    total: int


class PurchaseItemLineCreate(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)
    unit_cost: Decimal = Field(ge=0)


class PurchaseCreate(BaseModel):
    supplier_id: int = Field(ge=1)
    items: list[PurchaseItemLineCreate] = Field(min_length=1)


class PurchaseItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_cost: Decimal
    line_total: Decimal


class PurchaseRead(BaseModel):
    id: int
    supplier_id: int
    supplier_name: str
    created_at: datetime
    items: list[PurchaseItemRead]
    total: Decimal


class PurchaseListItem(BaseModel):
    id: int
    supplier_id: int
    supplier_name: str
    created_at: datetime
    item_count: int
    total: Decimal


class PurchaseListResponse(BaseModel):
    items: list[PurchaseListItem]
    total: int
