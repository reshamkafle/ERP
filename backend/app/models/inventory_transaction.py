from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import InventoryTransactionType


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[InventoryTransactionType] = mapped_column(
        Enum(InventoryTransactionType, name="inventorytransactiontype"),
        nullable=False,
    )
    transaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    reference_document: Mapped[str | None] = mapped_column(String(128), nullable=True)
    from_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    from_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_decimal: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    material_roll_id: Mapped[int | None] = mapped_column(
        ForeignKey("material_rolls.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lot_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    reason_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    product: Mapped["Product"] = relationship(back_populates="inventory_transactions")
    user: Mapped["User | None"] = relationship()
