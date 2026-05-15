from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ApprovalStatus, ItemLifecycleStatus, ItemType


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    alternate_codes: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
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

    serial_number_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    batch_lot_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expiry_date_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    primary_uom: Mapped[str] = mapped_column(String(32), nullable=False, default="EA")
    secondary_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    length: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    gross_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    net_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

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

    # POS / stock (unchanged by inventory CRUD except initial values on create)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    category: Mapped["Category | None"] = relationship(back_populates="products")
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="product")
    purchase_items: Mapped[list["PurchaseItem"]] = relationship(back_populates="product")
