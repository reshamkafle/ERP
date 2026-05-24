from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AccountType


class ChartOfAccount(Base):
    __tablename__ = "chart_of_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="accounttype"),
        nullable=False,
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("chart_of_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_postable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent: Mapped["ChartOfAccount | None"] = relationship(
        remote_side="ChartOfAccount.id",
        foreign_keys=[parent_id],
    )
