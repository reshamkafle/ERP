from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    gl_account_id: Mapped[int] = mapped_column(
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    gl_account: Mapped["ChartOfAccount"] = relationship(foreign_keys=[gl_account_id])
