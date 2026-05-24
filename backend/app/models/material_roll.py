"""Fabric and raw material roll/lot tracking."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    MaterialFinishType,
    MaterialRollAllocationStatus,
    MaterialRollMovementType,
    MaterialRollStatus,
    StockQualityStatus,
)


class MaterialRoll(Base):
    __tablename__ = "material_rolls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    roll_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    rfid_tag: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    material_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    composition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    color: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dye_lot: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    pattern: Mapped[str | None] = mapped_column(String(120), nullable=True)
    gsm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    width: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    thickness: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(32), nullable=True)
    finish_type: Mapped[MaterialFinishType | None] = mapped_column(
        Enum(MaterialFinishType, name="materialfinishtype"),
        nullable=True,
    )

    initial_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    initial_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    remaining_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    primary_uom: Mapped[str] = mapped_column(String(32), nullable=False, default="meter")
    secondary_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)

    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )
    supplier_lot_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    purchase_id: Mapped[int | None] = mapped_column(
        ForeignKey("purchases.id", ondelete="SET NULL"),
        nullable=True,
    )
    purchase_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("purchase_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    po_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grn_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    receipt_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    manufacture_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[MaterialRollStatus] = mapped_column(
        Enum(MaterialRollStatus, name="materialrollstatus"),
        nullable=False,
        default=MaterialRollStatus.IN_STOCK,
        index=True,
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    quality_status: Mapped[StockQualityStatus] = mapped_column(
        Enum(StockQualityStatus, name="stockqualitystatus", create_constraint=False),
        nullable=False,
        default=StockQualityStatus.APPROVED,
    )

    inspection_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    inspection_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    certifications: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    defect_log: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    shrinkage_test_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    reserved_for_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reserved_for_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    custom_attributes: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    attachments: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_scanned_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped["Product"] = relationship()
    supplier: Mapped["Supplier | None"] = relationship()
    warehouse: Mapped["Warehouse | None"] = relationship()
    location: Mapped["StorageLocation | None"] = relationship()
    movements: Mapped[list["MaterialRollMovement"]] = relationship(
        back_populates="material_roll",
        order_by="MaterialRollMovement.transaction_at.desc()",
    )
    inspections: Mapped[list["MaterialRollInspection"]] = relationship(
        back_populates="material_roll",
        order_by="MaterialRollInspection.inspected_at.desc()",
    )
    allocations: Mapped[list["MaterialRollAllocation"]] = relationship(
        back_populates="material_roll",
    )


class MaterialRollMovement(Base):
    __tablename__ = "material_roll_movements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_roll_id: Mapped[int] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movement_type: Mapped[MaterialRollMovementType] = mapped_column(
        Enum(MaterialRollMovementType, name="materialrollmovementtype"),
        nullable=False,
    )
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    uom: Mapped[str] = mapped_column(String(32), nullable=False)
    from_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    reference_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reference_document: Mapped[str | None] = mapped_column(String(128), nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    material_roll: Mapped[MaterialRoll] = relationship(back_populates="movements")


class MaterialRollInspection(Base):
    __tablename__ = "material_roll_inspections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_roll_id: Mapped[int] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inspector_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    inspected_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    inspected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    test_parameters: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    material_roll: Mapped[MaterialRoll] = relationship(back_populates="inspections")


class MaterialRollAllocation(Base):
    __tablename__ = "material_roll_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    material_roll_id: Mapped[int] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reference_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    allocated_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=0)
    status: Mapped[MaterialRollAllocationStatus] = mapped_column(
        Enum(MaterialRollAllocationStatus, name="materialrollallocationstatus"),
        nullable=False,
        default=MaterialRollAllocationStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    material_roll: Mapped[MaterialRoll] = relationship(back_populates="allocations")
