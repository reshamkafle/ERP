from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ProcurementRunStatus


class ProcurementRun(Base):
    __tablename__ = "procurement_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[ProcurementRunStatus] = mapped_column(
        Enum(ProcurementRunStatus, name="procurementrunstatus"),
        nullable=False,
    )
    summary_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by_user: Mapped["User | None"] = relationship(back_populates="procurement_runs")
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="procurement_run")
