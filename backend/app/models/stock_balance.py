from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CostValuationMethod, StockQualityStatus


class StockBalance(Base):
    __tablename__ = "stock_balances"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            "location_id",
            "lot_number",
            name="uq_stock_balances_product_wh_loc_lot",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    in_transit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quality_status: Mapped[StockQualityStatus] = mapped_column(
        Enum(StockQualityStatus, name="stockqualitystatus"),
        nullable=False,
        default=StockQualityStatus.APPROVED,
    )
    valuation_method: Mapped[CostValuationMethod | None] = mapped_column(
        Enum(CostValuationMethod, name="costvaluationmethod"),
        nullable=True,
    )
    last_transaction_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lot_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="stock_balances")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="stock_balances")
    location: Mapped["StorageLocation | None"] = relationship(back_populates="stock_balances")
