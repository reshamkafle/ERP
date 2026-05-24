from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    AbcClass,
    ApprovalStatus,
    CostValuationMethod,
    ItemLifecycleStatus,
    ItemType,
    XyzClass,
)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    qr_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rfid_tag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    alternate_codes: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    default_supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )
    default_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    default_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    tax_rate_id: Mapped[int | None] = mapped_column(
        ForeignKey("tax_rates.id", ondelete="SET NULL"),
        nullable=True,
    )
    sub_category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    product_line: Mapped[str | None] = mapped_column(String(120), nullable=True)
    item_type: Mapped[ItemType] = mapped_column(
        Enum(ItemType, name="itemtype"),
        nullable=False,
        default=ItemType.TRADING,
    )

    size: Mapped[str | None] = mapped_column(String(64), nullable=True)
    color: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    variant: Mapped[str | None] = mapped_column(String(120), nullable=True)

    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    style_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    color_value_id: Mapped[int | None] = mapped_column(
        ForeignKey("attribute_values.id", ondelete="SET NULL"),
        nullable=True,
    )
    size_value_id: Mapped[int | None] = mapped_column(
        ForeignKey("attribute_values.id", ondelete="SET NULL"),
        nullable=True,
    )

    serial_number_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    batch_lot_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    roll_tracking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    batch_management_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expiry_date_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    shelf_life_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    primary_uom: Mapped[str] = mapped_column(String(32), nullable=False, default="EA")
    secondary_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    purchase_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sales_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    length: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    gross_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    net_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    abc_class: Mapped[AbcClass | None] = mapped_column(
        Enum(AbcClass, name="abcclass"),
        nullable=True,
    )
    xyz_class: Mapped[XyzClass | None] = mapped_column(
        Enum(XyzClass, name="xyzclass"),
        nullable=True,
    )

    lifecycle_status: Mapped[ItemLifecycleStatus] = mapped_column(
        Enum(ItemLifecycleStatus, name="itemlifecyclestatus"),
        nullable=False,
        default=ItemLifecycleStatus.ACTIVE,
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approvalstatus"),
        nullable=False,
        default=ApprovalStatus.DRAFT,
    )

    tax_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hs_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hazardous_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    perishable_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hazardous_material_class: Mapped[str | None] = mapped_column(String(64), nullable=True)
    regulatory_compliance_codes: Mapped[str | None] = mapped_column(Text, nullable=True)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    standard_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cost_valuation_method: Mapped[CostValuationMethod | None] = mapped_column(
        Enum(CostValuationMethod, name="costvaluationmethod"),
        nullable=True,
    )
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_stock_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    economic_order_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    promotion_reorder_boost: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_stock_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_order_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_order_qty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    procurement_lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    demand_forecast_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    quality_inspection_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    inspection_checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    expiry_alert_threshold_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    attachments: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    category: Mapped["Category | None"] = relationship(back_populates="products")
    default_supplier: Mapped["Supplier | None"] = relationship(
        back_populates="default_products",
        foreign_keys="Product.default_supplier_id",
    )
    tax_rate: Mapped["TaxRate | None"] = relationship()
    default_warehouse: Mapped["Warehouse | None"] = relationship(
        foreign_keys="Product.default_warehouse_id",
    )
    default_location: Mapped["StorageLocation | None"] = relationship(
        foreign_keys="Product.default_location_id",
    )
    created_by: Mapped["User | None"] = relationship(foreign_keys="Product.created_by_id")
    updated_by: Mapped["User | None"] = relationship(foreign_keys="Product.updated_by_id")
    product_suppliers: Mapped[list["ProductSupplier"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    stock_balances: Mapped[list["StockBalance"]] = relationship(back_populates="product")
    inventory_transactions: Mapped[list["InventoryTransaction"]] = relationship(
        back_populates="product",
    )
    sale_items: Mapped[list["SaleItem"]] = relationship(
        back_populates="product",
        foreign_keys="SaleItem.product_id",
    )
    purchase_items: Mapped[list["PurchaseItem"]] = relationship(back_populates="product")
    template: Mapped["ProductTemplate | None"] = relationship(
        back_populates="variants",
        foreign_keys="Product.template_id",
    )
    color_value: Mapped["AttributeValue | None"] = relationship(
        foreign_keys="Product.color_value_id",
    )
    size_value: Mapped["AttributeValue | None"] = relationship(
        foreign_keys="Product.size_value_id",
    )
