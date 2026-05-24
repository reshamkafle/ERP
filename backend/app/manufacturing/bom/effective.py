"""BOM effectivity helpers (status + date window)."""

from __future__ import annotations

from datetime import date

from app.manufacturing.bom.enums import BOMStatus
from app.manufacturing.bom.models import BOM


def bom_is_effective(bom: BOM, *, as_of: date | None = None) -> bool:
    """True when BOM is active for explosion/tree and within effective dates."""
    if bom.status != BOMStatus.ACTIVE:
        return False
    today = as_of or date.today()
    if bom.effective_start_date is not None and today < bom.effective_start_date:
        return False
    if bom.effective_end_date is not None and today > bom.effective_end_date:
        return False
    return True
