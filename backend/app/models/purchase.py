from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import DocumentPaymentStatus, PurchaseStatus


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    procurement_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("procurement_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="purchasestatus"),
        nullable=False,
        default=PurchaseStatus.RECEIVED,
    )
    agent_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    payment_status: Mapped[DocumentPaymentStatus] = mapped_column(
        Enum(DocumentPaymentStatus, name="documentpaymentstatus", create_constraint=False),
        nullable=False,
        default=DocumentPaymentStatus.UNPAID,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    supplier: Mapped["Supplier | None"] = relationship(back_populates="purchases")
    created_by_user: Mapped["User | None"] = relationship(back_populates="purchases")
    procurement_run: Mapped["ProcurementRun | None"] = relationship(back_populates="purchases")
    items: Mapped[list["PurchaseItem"]] = relationship(
        back_populates="purchase", cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    purchase_id: Mapped[int] = mapped_column(
        ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    rolls_expected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    receipt_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    purchase: Mapped["Purchase"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="purchase_items")
