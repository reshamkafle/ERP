from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer


class CustomerSalesArea(Base):
    __tablename__ = "customer_sales_areas"
    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "sales_org",
            "distribution_channel",
            "division",
            name="uq_customer_sales_area",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    sales_org: Mapped[str] = mapped_column(String(64), nullable=False)
    distribution_channel: Mapped[str | None] = mapped_column(String(64), nullable=True)
    division: Mapped[str | None] = mapped_column(String(64), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pricing_procedure: Mapped[str | None] = mapped_column(String(120), nullable=True)
    partner_functions: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="sales_areas")
