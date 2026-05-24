from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModuleRecord(Base):
    """Generic transactional record for ERP module features (MVP extensibility)."""

    __tablename__ = "module_records"
    __table_args__ = (
        Index("ix_module_records_module_feature", "module_code", "feature_code"),
        Index(
            "uq_module_records_ref",
            "module_code",
            "feature_code",
            "reference",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    feature_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reference: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    party_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    quantity: Mapped[int | None] = mapped_column(nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
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
