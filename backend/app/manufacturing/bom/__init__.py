"""BOM package — lazy exports for BOMService/repository to avoid ORM circular imports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.manufacturing.bom.calculators import (
    apply_quantity_to_primary_uom,
    apply_wastage,
    explode_bom,
)
from app.manufacturing.bom.enums import BOMStatus, BOMType, ConsumptionType, ItemCategory, UnitOfMeasure
from app.manufacturing.bom.exceptions import (
    BOMError,
    BOMNotFoundError,
    CycleError,
    ItemNotFoundError,
)
from app.manufacturing.bom.models import (
    BOM,
    BOMItem,
    BOMTree,
    BOMTreeNode,
    ExplosionLine,
    ExplosionResult,
    FabricSummary,
    Item,
    TrimSummary,
    ValidationResult,
)
from app.manufacturing.bom.schemas import BOMHeaderInput, BOMItemInput, SaveBOMRequest

if TYPE_CHECKING:
    from app.manufacturing.bom.repository import BOMRepository, InMemoryBOMRepository
    from app.manufacturing.bom.service import BOMService

__all__ = [
    "BOM",
    "BOMError",
    "BOMHeaderInput",
    "BOMItem",
    "BOMItemInput",
    "BOMNotFoundError",
    "BOMRepository",
    "BOMService",
    "BOMStatus",
    "BOMType",
    "BOMTree",
    "BOMTreeNode",
    "ConsumptionType",
    "CycleError",
    "ExplosionLine",
    "ExplosionResult",
    "FabricSummary",
    "InMemoryBOMRepository",
    "Item",
    "ItemCategory",
    "ItemNotFoundError",
    "SaveBOMRequest",
    "TrimSummary",
    "UnitOfMeasure",
    "ValidationResult",
    "apply_quantity_to_primary_uom",
    "apply_wastage",
    "explode_bom",
]

_LAZY_EXPORTS = {
    "BOMService": ("app.manufacturing.bom.service", "BOMService"),
    "BOMRepository": ("app.manufacturing.bom.repository", "BOMRepository"),
    "InMemoryBOMRepository": ("app.manufacturing.bom.repository", "InMemoryBOMRepository"),
}


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        module_path, attr = _LAZY_EXPORTS[name]
        import importlib

        module = importlib.import_module(module_path)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
