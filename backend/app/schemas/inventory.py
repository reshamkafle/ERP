from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ApprovalStatus, ItemLifecycleStatus, ItemType


class InventoryItemBase(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    barcode: str | None = Field(default=None, max_length=64)
    alternate_codes: str | None = None
    category_id: int | None = None
    sub_category: str | None = Field(default=None, max_length=120)
    product_line: str | None = Field(default=None, max_length=120)
    item_type: ItemType = ItemType.TRADING
    size: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=120)
    variant: str | None = Field(default=None, max_length=120)
    serial_number_flag: bool = False
    batch_lot_flag: bool = False
    expiry_date_flag: bool = False
    primary_uom: str = Field(default="EA", min_length=1, max_length=32)
    secondary_uom: str | None = Field(default=None, max_length=32)
    conversion_factor: Decimal | None = Field(default=None, ge=0)
    length: Decimal | None = Field(default=None, ge=0)
    width: Decimal | None = Field(default=None, ge=0)
    height: Decimal | None = Field(default=None, ge=0)
    volume: Decimal | None = Field(default=None, ge=0)
    gross_weight: Decimal | None = Field(default=None, ge=0)
    net_weight: Decimal | None = Field(default=None, ge=0)
    lifecycle_status: ItemLifecycleStatus = ItemLifecycleStatus.ACTIVE
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    tax_code: str | None = Field(default=None, max_length=64)
    hs_code: str | None = Field(default=None, max_length=32)
    country_of_origin: str | None = Field(default=None, max_length=64)
    hazardous_flag: bool = False
    perishable_flag: bool = False
    price: Decimal = Field(default=Decimal("0"), ge=0)
    cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    low_stock_threshold: int = Field(default=0, ge=0)

class InventoryItemCreate(InventoryItemBase):
    initial_stock: int = Field(default=0, ge=0)

    @field_validator("conversion_factor")
    @classmethod
    def conversion_requires_secondary(cls, v: Decimal | None, info):
        secondary = info.data.get("secondary_uom")
        if secondary and (v is None or v <= 0):
            raise ValueError("conversion_factor is required when secondary_uom is set")
        if v is not None and v > 0 and not secondary:
            raise ValueError("secondary_uom is required when conversion_factor is set")
        return v


class InventoryItemUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    barcode: str | None = Field(default=None, max_length=64)
    alternate_codes: str | None = None
    category_id: int | None = None
    sub_category: str | None = Field(default=None, max_length=120)
    product_line: str | None = Field(default=None, max_length=120)
    item_type: ItemType | None = None
    size: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=120)
    variant: str | None = Field(default=None, max_length=120)
    serial_number_flag: bool | None = None
    batch_lot_flag: bool | None = None
    expiry_date_flag: bool | None = None
    primary_uom: str | None = Field(default=None, min_length=1, max_length=32)
    secondary_uom: str | None = Field(default=None, max_length=32)
    conversion_factor: Decimal | None = Field(default=None, ge=0)
    length: Decimal | None = Field(default=None, ge=0)
    width: Decimal | None = Field(default=None, ge=0)
    height: Decimal | None = Field(default=None, ge=0)
    volume: Decimal | None = Field(default=None, ge=0)
    gross_weight: Decimal | None = Field(default=None, ge=0)
    net_weight: Decimal | None = Field(default=None, ge=0)
    lifecycle_status: ItemLifecycleStatus | None = None
    approval_status: ApprovalStatus | None = None
    tax_code: str | None = Field(default=None, max_length=64)
    hs_code: str | None = Field(default=None, max_length=32)
    country_of_origin: str | None = Field(default=None, max_length=64)
    hazardous_flag: bool | None = None
    perishable_flag: bool | None = None
    price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    low_stock_threshold: int | None = Field(default=None, ge=0)


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class InventoryItemRead(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock: int
    category: CategoryBrief | None = None


class InventoryListResponse(BaseModel):
    items: list[InventoryItemRead]
    total: int


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
