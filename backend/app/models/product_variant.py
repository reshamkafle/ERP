from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ItemType


class ProductAttribute(Base):
    """Normalized attribute dimension (e.g. COLOR, SIZE)."""

    __tablename__ = "product_attributes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    values: Mapped[list["AttributeValue"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
        order_by="AttributeValue.sort_order",
    )


class AttributeValue(Base):
    """Controlled value for a product attribute."""

    __tablename__ = "attribute_values"
    __table_args__ = (
        UniqueConstraint("attribute_id", "code", name="uq_attribute_value_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attribute_id: Mapped[int] = mapped_column(
        ForeignKey("product_attributes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    attribute: Mapped["ProductAttribute"] = relationship(back_populates="values")


class ProductTemplate(Base):
    """Style master for Style-Color-Size variant matrix."""

    __tablename__ = "product_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    style_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sku_prefix: Mapped[str] = mapped_column(String(48), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    item_type: Mapped[ItemType] = mapped_column(
        Enum(ItemType, name="itemtype"),
        nullable=False,
        default=ItemType.FINISHED,
    )
    product_line: Mapped[str | None] = mapped_column(String(120), nullable=True)
    primary_uom: Mapped[str] = mapped_column(String(32), nullable=False, default="EA")
    default_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    default_cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    manufacturing_item_sku: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category | None"] = relationship()
    variants: Mapped[list["Product"]] = relationship(
        back_populates="template",
        foreign_keys="Product.template_id",
    )
