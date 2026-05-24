from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import StorageLocationStatus, StorageLocationType, WarehouseStatus, WarehouseType


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    warehouse_type: Mapped[WarehouseType] = mapped_column(
        Enum(WarehouseType, name="warehousetype"),
        nullable=False,
        default=WarehouseType.MAIN,
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    capacity_weight: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    capacity_volume: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    capacity_pallets: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[WarehouseStatus] = mapped_column(
        Enum(WarehouseStatus, name="warehousestatus"),
        nullable=False,
        default=WarehouseStatus.ACTIVE,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    wave_picking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cross_docking_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cycle_count_frequency: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cycle_count_class: Mapped[str | None] = mapped_column(String(32), nullable=True)
    packing_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    locations: Mapped[list["StorageLocation"]] = relationship(back_populates="warehouse")
    stock_balances: Mapped[list["StockBalance"]] = relationship(back_populates="warehouse")


class StorageLocation(Base):
    __tablename__ = "storage_locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    aisle: Mapped[str | None] = mapped_column(String(32), nullable=True)
    row: Mapped[str | None] = mapped_column(String(32), nullable=True)
    column: Mapped[str | None] = mapped_column(String(32), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    location_type: Mapped[StorageLocationType] = mapped_column(
        Enum(StorageLocationType, name="storagelocationtype"),
        nullable=False,
        default=StorageLocationType.BULK,
    )
    capacity: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    putaway_strategy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    picking_strategy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[StorageLocationStatus] = mapped_column(
        Enum(StorageLocationStatus, name="storagelocationstatus"),
        nullable=False,
        default=StorageLocationStatus.AVAILABLE,
    )
    zone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    warehouse: Mapped["Warehouse"] = relationship(back_populates="locations")
    stock_balances: Mapped[list["StockBalance"]] = relationship(back_populates="location")
