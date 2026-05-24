from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ItemLifecycleStatus, ItemType


class AttributeValueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attribute_id: int
    code: str
    label: str
    sort_order: int
    is_active: bool


class ProductAttributeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    sort_order: int
    is_active: bool
    values: list[AttributeValueRead] = []


class AttributeValueCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    label: str = Field(min_length=1, max_length=120)
    sort_order: int = 0
    is_active: bool = True


class ProductAttributeCreate(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = 0
    is_active: bool = True


class ProductTemplateBase(BaseModel):
    style_code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sku_prefix: str = Field(min_length=1, max_length=48)
    category_id: int | None = None
    item_type: ItemType = ItemType.FINISHED
    product_line: str | None = Field(default=None, max_length=120)
    primary_uom: str = Field(default="EA", min_length=1, max_length=32)
    default_price: Decimal = Field(default=Decimal("0"), ge=0)
    default_cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    manufacturing_item_sku: str | None = Field(default=None, max_length=64)
    is_active: bool = True


class ProductTemplateCreate(ProductTemplateBase):
    pass


class ProductTemplateUpdate(BaseModel):
    style_code: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    sku_prefix: str | None = Field(default=None, min_length=1, max_length=48)
    category_id: int | None = None
    item_type: ItemType | None = None
    product_line: str | None = Field(default=None, max_length=120)
    primary_uom: str | None = Field(default=None, min_length=1, max_length=32)
    default_price: Decimal | None = Field(default=None, ge=0)
    default_cost_price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    manufacturing_item_sku: str | None = Field(default=None, max_length=64)
    is_active: bool | None = None


class ProductTemplateRead(ProductTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    variant_count: int = 0
    total_stock: int = 0


class ProductTemplateListResponse(BaseModel):
    items: list[ProductTemplateRead]
    total: int


class VariantBriefRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    color: str | None = None
    size: str | None = None
    color_value_id: int | None = None
    size_value_id: int | None = None
    stock: int
    lifecycle_status: ItemLifecycleStatus
    price: Decimal


class TemplateVariantsResponse(BaseModel):
    template: ProductTemplateRead
    variants: list[VariantBriefRead]


class MatrixGenerateRequest(BaseModel):
    color_value_ids: list[int] = Field(min_length=1)
    size_value_ids: list[int] = Field(min_length=1)
    skip_existing: bool = True
    initial_stock: int = Field(default=0, ge=0)
    lifecycle_status: ItemLifecycleStatus = ItemLifecycleStatus.ACTIVE


class MatrixGenerateResult(BaseModel):
    created: list[VariantBriefRead]
    skipped: list[str]
    errors: list[str]
