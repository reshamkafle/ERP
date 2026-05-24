from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    AllocationType,
    PartyType,
    PaymentDirection,
    PaymentStatus,
    PaymentType,
)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    direction: Mapped[PaymentDirection] = mapped_column(
        Enum(PaymentDirection, name="paymentdirection"),
        nullable=False,
    )
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType, name="paymenttype"),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="paymentstatus"),
        nullable=False,
        default=PaymentStatus.DRAFT,
    )
    party_type: Mapped[PartyType] = mapped_column(
        Enum(PartyType, name="partytype"),
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    party_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"),
        nullable=False,
    )
    bank_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    exchange_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    amount_base: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    erp_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("erp_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    journal_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    customer: Mapped["Customer | None"] = relationship(foreign_keys=[customer_id])
    supplier: Mapped["Supplier | None"] = relationship(foreign_keys=[supplier_id])
    payment_method: Mapped["PaymentMethod"] = relationship(foreign_keys=[payment_method_id])
    bank_account: Mapped["BankAccount | None"] = relationship(foreign_keys=[bank_account_id])
    erp_document: Mapped["ErpDocument | None"] = relationship(foreign_keys=[erp_document_id])
    journal_entry: Mapped["JournalEntry | None"] = relationship(foreign_keys=[journal_entry_id])
    created_by_user: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])
    approved_by_user: Mapped["User | None"] = relationship(foreign_keys=[approved_by_id])
    allocations: Mapped[list["PaymentAllocation"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list["PaymentAuditLog"]] = relationship(
        back_populates="payment",
        cascade="all, delete-orphan",
    )


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    allocation_type: Mapped[AllocationType] = mapped_column(
        Enum(AllocationType, name="allocationtype"),
        nullable=False,
        default=AllocationType.INVOICE,
    )
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id", ondelete="RESTRICT"), nullable=True)
    purchase_id: Mapped[int | None] = mapped_column(
        ForeignKey("purchases.id", ondelete="RESTRICT"),
        nullable=True,
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    payment: Mapped["Payment"] = relationship(back_populates="allocations")
    sale: Mapped["Sale | None"] = relationship(foreign_keys=[sale_id])
    purchase: Mapped["Purchase | None"] = relationship(foreign_keys=[purchase_id])


class PaymentAuditLog(Base):
    __tablename__ = "payment_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    old_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    payment: Mapped["Payment"] = relationship(back_populates="audit_logs")
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])
