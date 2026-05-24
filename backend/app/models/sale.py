from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    AtpCheckStatus,
    BillingStatus,
    CreditCheckStatus,
    DeliveryStatus,
    DocumentPaymentStatus,
    OrderPriority,
    SaleChannel,
    SaleLineStatus,
    SaleOrderSource,
    SaleOrderStatus,
    SaleOrderType,
    SalePartnerRole,
)


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    order_status: Mapped[SaleOrderStatus] = mapped_column(
        Enum(SaleOrderStatus, name="saleorderstatus", create_constraint=False),
        nullable=False,
        default=SaleOrderStatus.DRAFT,
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    order_type: Mapped[SaleOrderType] = mapped_column(
        Enum(SaleOrderType, name="saleordertype", create_constraint=False),
        nullable=False,
        default=SaleOrderType.STANDARD,
    )
    sales_channel: Mapped[SaleChannel | None] = mapped_column(
        Enum(SaleChannel, name="salechannel", create_constraint=False),
        nullable=True,
    )
    order_source: Mapped[SaleOrderSource | None] = mapped_column(
        Enum(SaleOrderSource, name="saleordersource", create_constraint=False),
        nullable=True,
    )
    priority: Mapped[OrderPriority] = mapped_column(
        Enum(OrderPriority, name="orderpriority", create_constraint=False),
        nullable=False,
        default=OrderPriority.MEDIUM,
    )
    salesperson_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_pos_checkout: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    sales_organization: Mapped[str | None] = mapped_column(String(32), nullable=True)
    distribution_channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    division: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sales_office: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sales_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pricing_procedure: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incoterms_location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_point_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_po_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    customer_po_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    complete_delivery_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    opportunity_id: Mapped[int | None] = mapped_column(
        ForeignKey("crm_opportunities.id", ondelete="SET NULL"),
        nullable=True,
    )
    campaign_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    price_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    shipping_conditions: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transportation_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    loading_group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    header_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    gross_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    header_discount_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    freight_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    insurance_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    handling_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    payment_status: Mapped[DocumentPaymentStatus] = mapped_column(
        Enum(DocumentPaymentStatus, name="documentpaymentstatus", create_constraint=False),
        nullable=False,
        default=DocumentPaymentStatus.UNPAID,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    price_list_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payment_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_method_id: Mapped[int | None] = mapped_column(
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
    )

    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    partial_delivery_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    planned_ship_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    shipping_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incoterms: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delivery_block: Mapped[str | None] = mapped_column(String(64), nullable=True)

    credit_check_status: Mapped[CreditCheckStatus] = mapped_column(
        Enum(CreditCheckStatus, name="creditcheckstatus", create_constraint=False),
        nullable=False,
        default=CreditCheckStatus.NOT_RUN,
    )
    atp_check_status: Mapped[AtpCheckStatus] = mapped_column(
        Enum(AtpCheckStatus, name="atpcheckstatus", create_constraint=False),
        nullable=False,
        default=AtpCheckStatus.NOT_RUN,
    )
    invoice_status: Mapped[BillingStatus | None] = mapped_column(
        Enum(BillingStatus, name="billingstatus", create_constraint=False),
        nullable=True,
    )
    delivery_status: Mapped[DeliveryStatus | None] = mapped_column(
        Enum(DeliveryStatus, name="deliverystatus", create_constraint=False),
        nullable=True,
    )
    approval_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    customer_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    pricing_conditions: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    delivery_logistics: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    billing_financial: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    terms_compliance: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    references: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    attachments: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    workflow_history: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)

    customer: Mapped["Customer | None"] = relationship(back_populates="sales")
    created_by_user: Mapped["User | None"] = relationship(
        back_populates="sales",
        foreign_keys=[created_by_id],
    )
    updated_by_user: Mapped["User | None"] = relationship(foreign_keys=[updated_by_id])
    salesperson: Mapped["User | None"] = relationship(foreign_keys=[salesperson_id])
    warehouse: Mapped["Warehouse | None"] = relationship(foreign_keys=[warehouse_id])
    shipping_point: Mapped["Warehouse | None"] = relationship(foreign_keys=[shipping_point_id])
    payment_method: Mapped["PaymentMethod | None"] = relationship(foreign_keys=[payment_method_id])
    opportunity: Mapped["CrmOpportunity | None"] = relationship(foreign_keys=[opportunity_id])
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    partners: Mapped[list["SalePartner"]] = relationship(
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SalePartner(Base):
    __tablename__ = "sale_partners"
    __table_args__ = (UniqueConstraint("sale_id", "role", name="uq_sale_partners_sale_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[SalePartnerRole] = mapped_column(
        Enum(SalePartnerRole, name="salepartnerrole", create_constraint=False),
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name_override: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    sale: Mapped["Sale"] = relationship(back_populates="partners")
    customer: Mapped["Customer | None"] = relationship(foreign_keys=[customer_id])
    supplier: Mapped["Supplier | None"] = relationship(foreign_keys=[supplier_id])
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    alternate_uom: Mapped[str | None] = mapped_column(String(32), nullable=True)
    uom_conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_at_sale: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tax_rate_id: Mapped[int | None] = mapped_column(
        ForeignKey("tax_rates.id", ondelete="SET NULL"),
        nullable=True,
    )
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    requested_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    confirmed_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    confirmed_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    line_status: Mapped[SaleLineStatus] = mapped_column(
        Enum(SaleLineStatus, name="salelinestatus", create_constraint=False),
        nullable=False,
        default=SaleLineStatus.OPEN,
    )
    backorder_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    item_category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
    )
    storage_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    batch_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_block: Mapped[str | None] = mapped_column(String(64), nullable=True)
    billing_block: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(120), nullable=True)
    net_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    gross_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    substitute_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    line_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    sale: Mapped["Sale"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sale_items", foreign_keys=[product_id])
    substitute_product: Mapped["Product | None"] = relationship(foreign_keys=[substitute_product_id])
    tax_rate: Mapped["TaxRate | None"] = relationship(foreign_keys=[tax_rate_id])
    warehouse: Mapped["Warehouse | None"] = relationship(foreign_keys=[warehouse_id])
    storage_location: Mapped["StorageLocation | None"] = relationship(foreign_keys=[storage_location_id])
