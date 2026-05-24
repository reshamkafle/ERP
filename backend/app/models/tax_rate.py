from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import TaxType


class TaxRate(Base):
    __tablename__ = "tax_rates"
    __table_args__ = (
        Index("ix_tax_rates_code_country", "code", "country_code"),
        Index("ix_tax_rates_effective", "effective_from", "effective_to"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rate_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    tax_type: Mapped[TaxType] = mapped_column(
        Enum(TaxType, name="taxtype"),
        nullable=False,
        default=TaxType.OTHER,
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
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
