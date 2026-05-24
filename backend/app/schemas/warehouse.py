from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    StorageLocationStatus,
    StorageLocationType,
    WarehouseStatus,
    WarehouseType,
)


class WarehouseBase(BaseModel):
    code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    warehouse_type: WarehouseType = WarehouseType.MAIN
    address: str | None = None
    capacity_weight: Decimal | None = Field(default=None, ge=0)
    capacity_volume: Decimal | None = Field(default=None, ge=0)
    capacity_pallets: int | None = Field(default=None, ge=0)
    status: WarehouseStatus = WarehouseStatus.ACTIVE
    is_default: bool = False
    wave_picking_enabled: bool = False
    cross_docking_enabled: bool = False
    cycle_count_frequency: str | None = Field(default=None, max_length=64)
    cycle_count_class: str | None = Field(default=None, max_length=32)
    packing_rules: dict | None = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    warehouse_type: WarehouseType | None = None
    address: str | None = None
    capacity_weight: Decimal | None = Field(default=None, ge=0)
    capacity_volume: Decimal | None = Field(default=None, ge=0)
    capacity_pallets: int | None = Field(default=None, ge=0)
    status: WarehouseStatus | None = None
    is_default: bool | None = None
    wave_picking_enabled: bool | None = None
    cross_docking_enabled: bool | None = None
    cycle_count_frequency: str | None = None
    cycle_count_class: str | None = None
    packing_rules: dict | None = None


class WarehouseRead(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class WarehouseListResponse(BaseModel):
    items: list[WarehouseRead]
    total: int


class StorageLocationBase(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    warehouse_id: int
    aisle: str | None = Field(default=None, max_length=32)
    row: str | None = Field(default=None, max_length=32)
    column: str | None = Field(default=None, max_length=32)
    level: str | None = Field(default=None, max_length=32)
    location_type: StorageLocationType = StorageLocationType.BULK
    capacity: Decimal | None = Field(default=None, ge=0)
    putaway_strategy: str | None = Field(default=None, max_length=64)
    picking_strategy: str | None = Field(default=None, max_length=64)
    status: StorageLocationStatus = StorageLocationStatus.AVAILABLE
    zone: str | None = Field(default=None, max_length=64)


class StorageLocationCreate(StorageLocationBase):
    pass


class StorageLocationUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=64)
    warehouse_id: int | None = None
    aisle: str | None = None
    row: str | None = None
    column: str | None = None
    level: str | None = None
    location_type: StorageLocationType | None = None
    capacity: Decimal | None = Field(default=None, ge=0)
    putaway_strategy: str | None = None
    picking_strategy: str | None = None
    status: StorageLocationStatus | None = None
    zone: str | None = None


class StorageLocationRead(StorageLocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StorageLocationListResponse(BaseModel):
    items: list[StorageLocationRead]
    total: int
