from decimal import Decimal

from sqlalchemy import Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dba: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(120), nullable=True)
    incoterms: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    vendor_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    vendor_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    performance_rating: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    moq: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    pricing_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    documents: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="supplier")
    default_products: Mapped[list["Product"]] = relationship(
        back_populates="default_supplier",
        foreign_keys="Product.default_supplier_id",
    )
    product_supplier_links: Mapped[list["ProductSupplier"]] = relationship(
        back_populates="supplier",
    )
