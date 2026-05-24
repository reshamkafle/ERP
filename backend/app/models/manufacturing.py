from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.manufacturing.bom.enums import (
    BOMStatus,
    BOMType,
    ConsumptionType,
    ItemCategory,
    UnitOfMeasure,
)
from app.models.base import Base

_enum_values = lambda enum_cls: [member.value for member in enum_cls]


class ManufacturingItem(Base):
    __tablename__ = "manufacturing_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ItemCategory] = mapped_column(
        Enum(ItemCategory, name="manufacturingitemcategory", values_callable=_enum_values),
        nullable=False,
    )
    unit: Mapped[UnitOfMeasure] = mapped_column(
        Enum(UnitOfMeasure, name="manufacturingunitofmeasure", values_callable=_enum_values),
        nullable=False,
    )
    cost_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    secondary_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    product: Mapped["Product | None"] = relationship(foreign_keys=[product_id])
    parent_bom_lines: Mapped[list["BOMLine"]] = relationship(
        back_populates="parent_item",
        foreign_keys="BOMLine.parent_item_id",
    )
    component_bom_lines: Mapped[list["BOMLine"]] = relationship(
        back_populates="component_item",
        foreign_keys="BOMLine.component_item_id",
    )
    bom_header: Mapped["BOMHeader | None"] = relationship(
        back_populates="parent_item",
        uselist=False,
    )


class BOMHeader(Base):
    __tablename__ = "bom_headers"

    parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bom_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[BOMStatus] = mapped_column(
        Enum(BOMStatus, name="bomstatus", values_callable=_enum_values),
        nullable=False,
        default=BOMStatus.DRAFT,
    )
    bom_type: Mapped[BOMType] = mapped_column(
        Enum(BOMType, name="bomtype", values_callable=_enum_values),
        nullable=False,
        default=BOMType.MANUFACTURING,
    )
    effective_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    eco_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent_item: Mapped[ManufacturingItem] = relationship(back_populates="bom_header")
    approved_by: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])
    created_by: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])
    updated_by: Mapped["User | None"] = relationship(foreign_keys=[updated_by_id])
    lines: Mapped[list["BOMLine"]] = relationship(
        "BOMLine",
        primaryjoin="BOMHeader.parent_item_id == BOMLine.parent_item_id",
        foreign_keys="BOMLine.parent_item_id",
        viewonly=True,
    )


class BOMLine(Base):
    __tablename__ = "bom_lines"
    __table_args__ = (
        UniqueConstraint("parent_item_id", "component_item_id", name="uq_bom_parent_component"),
        UniqueConstraint("parent_item_id", "line_sequence", name="uq_bom_lines_parent_sequence"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    component_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    consumption_type: Mapped[ConsumptionType] = mapped_column(
        Enum(ConsumptionType, name="consumptiontype", values_callable=_enum_values),
        nullable=False,
        default=ConsumptionType.OTHER,
    )
    wastage_percentage: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    yield_percentage: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    is_phantom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lead_time_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_item: Mapped[ManufacturingItem] = relationship(
        back_populates="parent_bom_lines",
        foreign_keys=[parent_item_id],
    )
    component_item: Mapped[ManufacturingItem] = relationship(
        back_populates="component_bom_lines",
        foreign_keys=[component_item_id],
    )
    substitutes: Mapped[list["BOMSubstitute"]] = relationship(back_populates="bom_line")


class BOMAlternate(Base):
    """Alternate BOM header for same parent item (priority within alternate_group)."""

    __tablename__ = "bom_alternates"
    __table_args__ = (
        UniqueConstraint(
            "parent_item_id",
            "alternate_group",
            "priority",
            name="uq_bom_alt_parent_group_priority",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alternate_parent_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    alternate_group: Mapped[str] = mapped_column(String(32), nullable=False, default="DEFAULT")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_item: Mapped[ManufacturingItem] = relationship(foreign_keys=[parent_item_id])
    alternate_parent_item: Mapped[ManufacturingItem] = relationship(
        foreign_keys=[alternate_parent_item_id],
    )


class BOMSubstitute(Base):
    """Substitute component for a BOM line."""

    __tablename__ = "bom_substitutes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bom_line_id: Mapped[int] = mapped_column(
        ForeignKey("bom_lines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    substitute_item_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    substitute_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    bom_line: Mapped[BOMLine] = relationship(back_populates="substitutes")
    substitute_item: Mapped[ManufacturingItem] = relationship(foreign_keys=[substitute_item_id])
