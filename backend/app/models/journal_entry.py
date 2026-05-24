from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import JournalEntryStatus, JournalSourceType


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entry_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_type: Mapped[JournalSourceType] = mapped_column(
        Enum(JournalSourceType, name="journalsourcetype"),
        nullable=False,
    )
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[JournalEntryStatus] = mapped_column(
        Enum(JournalEntryStatus, name="journalentrystatus"),
        nullable=False,
        default=JournalEntryStatus.DRAFT,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reversal_of_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lines: Mapped[list["JournalLine"]] = relationship(
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
    reversal_of: Mapped["JournalEntry | None"] = relationship(
        remote_side="JournalEntry.id",
        foreign_keys=[reversal_of_id],
    )
    created_by_user: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("chart_of_accounts.id"),
        nullable=False,
    )
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)

    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="lines")
    account: Mapped["ChartOfAccount"] = relationship(foreign_keys=[account_id])
