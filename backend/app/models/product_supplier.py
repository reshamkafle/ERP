from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductSupplier(Base):
    __tablename__ = "product_suppliers"
    __table_args__ = (
        UniqueConstraint("product_id", "supplier_id", name="uq_product_suppliers_product_supplier"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product: Mapped["Product"] = relationship(back_populates="product_suppliers")
    supplier: Mapped["Supplier"] = relationship(back_populates="product_supplier_links")
