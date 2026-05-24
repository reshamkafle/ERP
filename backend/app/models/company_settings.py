from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CompanySettings(Base):
    __tablename__ = "company_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="US")
    fiscal_year_start_month: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    mrp_order_creation_mode: Mapped[str] = mapped_column(
        String(32), nullable=False, default="manual"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
