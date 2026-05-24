from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AbcClass,
    ApprovalStatus,
    CostValuationMethod,
    InventoryTransactionType,
    ItemLifecycleStatus,
    ItemType,
    StockQualityStatus,
    XyzClass,
)


class ProductSupplierInput(BaseModel):
    supplier_id: int
    vendor_code: str | None = Field(default=None, max_length=64)
    is_preferred: bool = False


class ProductSupplierRead(ProductSupplierInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_name: str | None = None


class TaxRateBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    rate_percent: Decimal


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class WarehouseBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str


class StorageLocationBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    warehouse_id: int


class InventoryItemBase(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    barcode: str | None = Field(default=None, max_length=64)
    qr_code: str | None = Field(default=None, max_length=128)
    rfid_tag: str | None = Field(default=None, max_length=128)
    alternate_codes: str | None = None
    category_id: int | None = None
    sub_category: str | None = Field(default=None, max_length=120)
    product_line: str | None = Field(default=None, max_length=120)
    item_type: ItemType = ItemType.TRADING
    size: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=120)
    variant: str | None = Field(default=None, max_length=120)
    template_id: int | None = None
    style_code: str | None = Field(default=None, max_length=64)
    color_value_id: int | None = None
    size_value_id: int | None = None
    serial_number_flag: bool = False
    batch_lot_flag: bool = False
    roll_tracking_enabled: bool = False
    batch_management_enabled: bool = False
    expiry_date_flag: bool = False
    shelf_life_days: int | None = Field(default=None, ge=0)
    primary_uom: str = Field(default="EA", min_length=1, max_length=32)
    secondary_uom: str | None = Field(default=None, max_length=32)
    purchase_uom: str | None = Field(default=None, max_length=32)
    sales_uom: str | None = Field(default=None, max_length=32)
    conversion_factor: Decimal | None = Field(default=None, ge=0)
    length: Decimal | None = Field(default=None, ge=0)
    width: Decimal | None = Field(default=None, ge=0)
    height: Decimal | None = Field(default=None, ge=0)
    volume: Decimal | None = Field(default=None, ge=0)
    gross_weight: Decimal | None = Field(default=None, ge=0)
    net_weight: Decimal | None = Field(default=None, ge=0)
    abc_class: AbcClass | None = None
    xyz_class: XyzClass | None = None
    lifecycle_status: ItemLifecycleStatus = ItemLifecycleStatus.ACTIVE
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    tax_code: str | None = Field(default=None, max_length=64)
    tax_rate_id: int | None = None
    hs_code: str | None = Field(default=None, max_length=32)
    country_of_origin: str | None = Field(default=None, max_length=64)
    hazardous_flag: bool = False
    perishable_flag: bool = False
    hazardous_material_class: str | None = Field(default=None, max_length=64)
    regulatory_compliance_codes: str | None = None
    price: Decimal = Field(default=Decimal("0"), ge=0)
    cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    standard_cost: Decimal | None = Field(default=None, ge=0)
    cost_valuation_method: CostValuationMethod | None = None
    low_stock_threshold: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)
    max_stock_level: int | None = Field(default=None, ge=0)
    economic_order_qty: int | None = Field(default=None, ge=0)
    lead_time_days: int | None = Field(default=None, ge=0)
    default_supplier_id: int | None = Field(default=None)
    default_warehouse_id: int | None = None
    default_location_id: int | None = None
    promotion_reorder_boost: bool = False
    reorder_point: int = Field(default=0, ge=0)
    safety_stock_level: int = Field(default=0, ge=0)
    min_order_qty: int | None = Field(default=None, ge=0)
    max_order_qty: int | None = Field(default=None, ge=0)
    procurement_lead_time_days: int | None = Field(default=None, ge=0)
    demand_forecast_notes: str | None = None
    quality_inspection_required: bool = False
    inspection_checklist: dict | list | None = None
    expiry_alert_threshold_days: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    attachments: list[dict] | None = None


class InventoryItemCreate(InventoryItemBase):
    initial_stock: int = Field(default=0, ge=0)
    manufacturing_item_sku: str | None = Field(default=None, max_length=64)
    product_suppliers: list[ProductSupplierInput] = []

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
    qr_code: str | None = Field(default=None, max_length=128)
    rfid_tag: str | None = Field(default=None, max_length=128)
    alternate_codes: str | None = None
    category_id: int | None = None
    sub_category: str | None = Field(default=None, max_length=120)
    product_line: str | None = Field(default=None, max_length=120)
    item_type: ItemType | None = None
    size: str | None = Field(default=None, max_length=64)
    color: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=120)
    variant: str | None = Field(default=None, max_length=120)
    template_id: int | None = None
    style_code: str | None = Field(default=None, max_length=64)
    color_value_id: int | None = None
    size_value_id: int | None = None
    serial_number_flag: bool | None = None
    batch_lot_flag: bool | None = None
    roll_tracking_enabled: bool | None = None
    batch_management_enabled: bool | None = None
    expiry_date_flag: bool | None = None
    shelf_life_days: int | None = Field(default=None, ge=0)
    primary_uom: str | None = Field(default=None, min_length=1, max_length=32)
    secondary_uom: str | None = Field(default=None, max_length=32)
    purchase_uom: str | None = Field(default=None, max_length=32)
    sales_uom: str | None = Field(default=None, max_length=32)
    conversion_factor: Decimal | None = Field(default=None, ge=0)
    length: Decimal | None = Field(default=None, ge=0)
    width: Decimal | None = Field(default=None, ge=0)
    height: Decimal | None = Field(default=None, ge=0)
    volume: Decimal | None = Field(default=None, ge=0)
    gross_weight: Decimal | None = Field(default=None, ge=0)
    net_weight: Decimal | None = Field(default=None, ge=0)
    abc_class: AbcClass | None = None
    xyz_class: XyzClass | None = None
    lifecycle_status: ItemLifecycleStatus | None = None
    approval_status: ApprovalStatus | None = None
    tax_code: str | None = Field(default=None, max_length=64)
    tax_rate_id: int | None = None
    hs_code: str | None = Field(default=None, max_length=32)
    country_of_origin: str | None = Field(default=None, max_length=64)
    hazardous_flag: bool | None = None
    perishable_flag: bool | None = None
    hazardous_material_class: str | None = Field(default=None, max_length=64)
    regulatory_compliance_codes: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    standard_cost: Decimal | None = Field(default=None, ge=0)
    cost_valuation_method: CostValuationMethod | None = None
    low_stock_threshold: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    max_stock_level: int | None = Field(default=None, ge=0)
    economic_order_qty: int | None = Field(default=None, ge=0)
    lead_time_days: int | None = Field(default=None, ge=0)
    default_supplier_id: int | None = None
    default_warehouse_id: int | None = None
    default_location_id: int | None = None
    promotion_reorder_boost: bool | None = None
    reorder_point: int | None = Field(default=None, ge=0)
    safety_stock_level: int | None = Field(default=None, ge=0)
    min_order_qty: int | None = Field(default=None, ge=0)
    max_order_qty: int | None = Field(default=None, ge=0)
    procurement_lead_time_days: int | None = Field(default=None, ge=0)
    demand_forecast_notes: str | None = None
    quality_inspection_required: bool | None = None
    inspection_checklist: dict | list | None = None
    expiry_alert_threshold_days: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=512)
    attachments: list[dict] | None = None
    product_suppliers: list[ProductSupplierInput] | None = None
    manufacturing_item_sku: str | None = Field(default=None, max_length=64)


class CategoryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SupplierBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class StockBalanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    warehouse_id: int
    warehouse_code: str | None = None
    warehouse_name: str | None = None
    location_id: int | None = None
    location_code: str | None = None
    on_hand: int
    available: int
    reserved: int
    in_transit: int
    quality_status: StockQualityStatus
    valuation_method: CostValuationMethod | None = None
    last_transaction_at: datetime | None = None
    expiry_date: str | None = None
    lot_number: str | None = None


class InventoryTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_type: InventoryTransactionType
    transaction_at: datetime
    reference_document: str | None = None
    from_warehouse_id: int | None = None
    from_location_id: int | None = None
    to_warehouse_id: int | None = None
    to_location_id: int | None = None
    quantity: int
    lot_number: str | None = None
    serial_number: str | None = None
    unit_cost: Decimal | None = None
    reason_code: str | None = None
    user_id: int | None = None
    user_email: str | None = None
    remarks: str | None = None


class InventoryAnalyticsRead(BaseModel):
    turnover_ratio: Decimal = Decimal("0")
    inventory_accuracy_pct: Decimal = Decimal("100")
    stock_value: Decimal = Decimal("0")
    dead_stock_value: Decimal = Decimal("0")
    inventory_holding_cost: Decimal = Decimal("0")


class InventorySalesDailyPoint(BaseModel):
    date: str
    quantity_sold: int = 0
    revenue: Decimal = Decimal("0")


class InventorySalesInsight(BaseModel):
    lookback_days: int = 30
    quantity_sold: int = 0
    revenue: Decimal = Decimal("0")
    top_buyer_name: str | None = None
    top_seller_name: str | None = None
    daily_chart: list[InventorySalesDailyPoint] = []


class ProductTemplateBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    style_code: str
    name: str


class InventoryItemRead(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock: int
    template: ProductTemplateBrief | None = None
    created_at: datetime
    updated_at: datetime
    category: CategoryBrief | None = None
    default_supplier: SupplierBrief | None = None
    tax_rate: TaxRateBrief | None = None
    default_warehouse: WarehouseBrief | None = None
    default_location: StorageLocationBrief | None = None
    created_by: UserBrief | None = None
    updated_by: UserBrief | None = None
    product_supplier_links: list[ProductSupplierRead] = []
    manufacturing_item_sku: str | None = None
    bom_parent_count: int = 0
    has_bom_shortage: bool = False
    sales_insight: InventorySalesInsight | None = None
    stock_balances: list[StockBalanceRead] = []
    analytics: InventoryAnalyticsRead | None = None


class InventoryBomUsageRead(BaseModel):
    parent_sku: str
    parent_name: str
    parent_category: str
    required_qty: Decimal
    on_hand_stock: int
    is_short: bool


class InventoryBomUsageListResponse(BaseModel):
    usages: list[InventoryBomUsageRead]


class InventoryListResponse(BaseModel):
    items: list[InventoryItemRead]
    total: int


class InventoryTransactionListResponse(BaseModel):
    items: list[InventoryTransactionRead]
    total: int


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
