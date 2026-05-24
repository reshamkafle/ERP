from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ErpDocumentStatus, ErpDocumentType


class ErpDocument(Base):
    __tablename__ = "erp_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    document_type: Mapped[ErpDocumentType] = mapped_column(
        Enum(ErpDocumentType, name="erpdocumenttype"),
        nullable=False,
        index=True,
    )
    journey_step: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[ErpDocumentStatus] = mapped_column(
        Enum(ErpDocumentStatus, name="erpdocumentstatus"),
        nullable=False,
        default=ErpDocumentStatus.DRAFT,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    purchase_id: Mapped[int | None] = mapped_column(ForeignKey("purchases.id"), nullable=True)
    sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="SET NULL"),
        nullable=True,
    )
    related_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("erp_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    supplier: Mapped["Supplier | None"] = relationship(foreign_keys=[supplier_id])
    customer: Mapped["Customer | None"] = relationship(foreign_keys=[customer_id])
    purchase: Mapped["Purchase | None"] = relationship(foreign_keys=[purchase_id])
    related_document: Mapped["ErpDocument | None"] = relationship(
        remote_side="ErpDocument.id",
        foreign_keys=[related_document_id],
    )
    created_by_user: Mapped["User | None"] = relationship(foreign_keys=[created_by_id])
