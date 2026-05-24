from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


class AddressBlock(BaseModel):
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


class CustomerSnapshot(BaseModel):
    customer_id: int | None = None
    customer_code: str | None = None
    name: str | None = None
    billing_address: AddressBlock | None = None
    shipping_address: AddressBlock | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    customer_group: str | None = None
    credit_limit: Decimal | None = None
    credit_status: str | None = None
    payment_terms: str | None = None
    tax_id: str | None = None
    shipping_preference: str | None = None
    incoterms: str | None = None
    trade_name: str | None = None
    status: str | None = None
    gst_number: str | None = None
    vat_number: str | None = None
    currency_code: str | None = None


class PricingConditions(BaseModel):
    contract_ref: str | None = None
    special_pricing_agreement: str | None = None
    total_before_tax: Decimal | None = None
    total_after_tax: Decimal | None = None
    line_discount_notes: str | None = None
    pricing_date: date | None = None
    manual_price_override_reason: str | None = None
    list_price_notes: str | None = None


class DeliveryLogistics(BaseModel):
    ship_to_override: AddressBlock | None = None
    shipping_instructions: str | None = None
    route: str | None = None
    warehouse_assignment: str | None = None
    promised_date: date | None = None
    actual_date: date | None = None
    delivery_number: str | None = None
    carrier_name: str | None = None
    tracking_number: str | None = None
    transport_mode: str | None = None
    bill_of_lading: str | None = None
    packaging_details: str | None = None
    expected_shipment_date: date | None = None


class BillingFinancial(BaseModel):
    bill_to: AddressBlock | None = None
    invoice_type: str | None = None
    cost_center: str | None = None
    profit_center: str | None = None
    project_code: str | None = None
    wbs_element: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    billing_type: str | None = None
    taxable_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    total_amount: Decimal | None = None
    accounting_document_number: str | None = None
    payment_method_label: str | None = None
    payment_receipt_number: str | None = None
    amount_received: Decimal | None = None
    outstanding_amount: Decimal | None = None
    credit_debit_note_ref: str | None = None
    billing_block: str | None = None
    split_billing: bool | None = None
    bank_details: str | None = None
    card_last_four: str | None = None


class TermsCompliance(BaseModel):
    warranty_terms: str | None = None
    return_policy_ref: str | None = None
    inspection_requirements: str | None = None
    regulatory_compliance: str | None = None
    order_validity_date: date | None = None
    order_expiry_date: date | None = None
    export_license: str | None = None
    hazardous_material_info: str | None = None
    sustainability_data: str | None = None


class SaleReferences(BaseModel):
    customer_po_number: str | None = None
    customer_po_date: date | None = None
    quotation_number: str | None = None
    contract_number: str | None = None
    tender_number: str | None = None
    internal_order_number: str | None = None
    remarks: str | None = None
    internal_notes: str | None = None
    reason_code: str | None = None
    order_reason: str | None = None
    attachments_note: str | None = None
    atp_check_notes: str | None = None
    crm_opportunity_link: str | None = None
    forecast_vs_actual: str | None = None
    forecast_category: str | None = None
    closing_probability: str | None = None
    expected_revenue: str | None = None
    lead_source: str | None = None
    order_confirmation_date: date | None = None
    returns_cancellation_reason: str | None = None
    fulfillment_lead_time_days: str | None = None
    profitability_analysis: str | None = None


class AttachmentMeta(BaseModel):
    filename: str
    url: str | None = None
    content_type: str | None = None


class WorkflowEvent(BaseModel):
    at: datetime | None = None
    status: str
    user_email: str | None = None
    note: str | None = None
    approver_name: str | None = None
    approver_date: date | None = None
    credit_approval_status: str | None = None
    margin_approval_status: str | None = None
    legal_approval_status: str | None = None


class WorkflowApproval(BaseModel):
    approver_name: str | None = None
    approver_date: date | None = None
    credit_approval_status: str | None = None
    margin_approval_status: str | None = None
    legal_approval_status: str | None = None
    note: str | None = None


class SalePartnerCreate(BaseModel):
    role: SalePartnerRole
    customer_id: int | None = None
    supplier_id: int | None = None
    user_id: int | None = None
    name_override: str | None = None
    address: AddressBlock | None = None


class SalePartnerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: SalePartnerRole
    customer_id: int | None = None
    customer_name: str | None = None
    supplier_id: int | None = None
    supplier_name: str | None = None
    user_id: int | None = None
    user_email: str | None = None
    name_override: str | None = None
    address: dict[str, Any] | None = None


class SaleItemLineCreate(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(ge=1)
    unit_price: Decimal | None = None
    description: str | None = None
    uom: str | None = None
    alternate_uom: str | None = None
    uom_conversion_factor: Decimal | None = None
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    tax_code: str | None = None
    tax_rate_id: int | None = None
    requested_delivery_date: date | None = None
    confirmed_delivery_date: date | None = None
    product_category: str | None = None
    item_category: str | None = None
    gross_price: Decimal | None = None
    warehouse_id: int | None = None
    storage_location_id: int | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    delivery_block: str | None = None
    billing_block: str | None = None
    rejection_reason: str | None = None
    net_weight: Decimal | None = None
    gross_weight: Decimal | None = None
    volume: Decimal | None = None
    substitute_product_id: int | None = None
    line_text: str | None = None
    line_status: SaleLineStatus | None = None


class SaleItemLineUpdate(SaleItemLineCreate):
    id: int | None = None


def _validate_b2b_fields(
    *,
    customer_id: int | None,
    customer_po_number: str | None,
    payment_terms: str | None,
    sales_organization: str | None,
    items: list[SaleItemLineCreate],
) -> None:
    missing: list[str] = []
    if not customer_id:
        missing.append("customer_id")
    if not (customer_po_number or "").strip():
        missing.append("customer_po_number")
    if not (payment_terms or "").strip():
        missing.append("payment_terms")
    if not (sales_organization or "").strip():
        missing.append("sales_organization")
    if not items:
        missing.append("items")
    else:
        for idx, line in enumerate(items):
            if line.product_id < 1:
                missing.append(f"items[{idx}].product_id")
            if line.quantity < 1:
                missing.append(f"items[{idx}].quantity")
            if line.unit_price is None:
                missing.append(f"items[{idx}].unit_price")
    if missing:
        raise ValueError(f"B2B order missing required fields: {', '.join(missing)}")


class SaleOrderBase(BaseModel):
    customer_id: int | None = None
    order_date: date | None = None
    order_type: SaleOrderType = SaleOrderType.STANDARD
    sales_channel: SaleChannel | None = None
    order_source: SaleOrderSource | None = None
    priority: OrderPriority = OrderPriority.MEDIUM
    salesperson_id: int | None = None
    currency_code: str | None = None
    price_list_code: str | None = None
    pricing_procedure: str | None = None
    payment_terms: str | None = None
    payment_due_date: date | None = None
    payment_method_id: int | None = None
    header_discount_amount: Decimal = Field(default=Decimal("0"), ge=0)
    freight_amount: Decimal = Field(default=Decimal("0"), ge=0)
    insurance_amount: Decimal = Field(default=Decimal("0"), ge=0)
    handling_amount: Decimal = Field(default=Decimal("0"), ge=0)
    warehouse_id: int | None = None
    shipping_point_id: int | None = None
    partial_delivery_allowed: bool = True
    complete_delivery_required: bool = False
    planned_ship_date: date | None = None
    requested_delivery_date: date | None = None
    shipping_method: str | None = None
    shipping_conditions: str | None = None
    transportation_group: str | None = None
    loading_group: str | None = None
    incoterms: str | None = None
    incoterms_location: str | None = None
    delivery_block: str | None = None
    sales_organization: str | None = None
    distribution_channel: str | None = None
    division: str | None = None
    sales_office: str | None = None
    sales_group: str | None = None
    customer_po_number: str | None = None
    customer_po_date: date | None = None
    opportunity_id: int | None = None
    campaign_id: str | None = None
    price_group: str | None = None
    header_text: str | None = None
    approval_status: str | None = None
    customer_snapshot: CustomerSnapshot | None = None
    pricing_conditions: PricingConditions | None = None
    delivery_logistics: DeliveryLogistics | None = None
    billing_financial: BillingFinancial | None = None
    terms_compliance: TermsCompliance | None = None
    references: SaleReferences | None = None
    attachments: list[AttachmentMeta] | None = None
    partners: list[SalePartnerCreate] | None = None
    workflow_approval: WorkflowApproval | None = None
    require_b2b_fields: bool = True


class SaleOrderCreate(SaleOrderBase):
    items: list[SaleItemLineCreate] = Field(min_length=1)
    confirm: bool = False
    order_number_override: str | None = Field(default=None, max_length=32)

    @model_validator(mode="after")
    def validate_b2b(self) -> SaleOrderCreate:
        if not self.require_b2b_fields:
            return self
        _validate_b2b_fields(
            customer_id=self.customer_id,
            customer_po_number=self.customer_po_number,
            payment_terms=self.payment_terms,
            sales_organization=self.sales_organization,
            items=self.items,
        )
        return self


class SaleOrderUpdate(SaleOrderBase):
    items: list[SaleItemLineUpdate] | None = None
    require_b2b_fields: bool = True


class SaleConfirmRequest(BaseModel):
    run_credit_check: bool = True
    run_atp_check: bool = True
    override_credit_failure: bool = False


class PosProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    barcode: str | None
    price: Decimal
    stock: int
    low_stock_threshold: int


class PosProductListResponse(BaseModel):
    items: list[PosProductRead]
    total: int


class PosCheckoutCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleItemLineCreate] = Field(min_length=1)
    confirm: bool = True


class SaleOrderSummary(BaseModel):
    total_items: int
    total_quantity: int
    total_net: Decimal
    total_tax: Decimal
    total_discount: Decimal
    freight: Decimal
    insurance: Decimal
    handling: Decimal
    grand_total: Decimal


class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    line_number: int
    product_id: int
    product_name: str
    product_sku: str
    description: str | None = None
    quantity: int
    uom: str | None = None
    alternate_uom: str | None = None
    uom_conversion_factor: Decimal | None = None
    unit_price: Decimal
    price_at_sale: Decimal
    gross_price: Decimal | None = None
    discount_percent: Decimal
    discount_amount: Decimal
    tax_code: str | None = None
    tax_rate_id: int | None = None
    tax_amount: Decimal
    net_amount: Decimal
    line_total: Decimal
    requested_delivery_date: date | None = None
    confirmed_delivery_date: date | None = None
    confirmed_quantity: int = 0
    delivered_quantity: int = 0
    line_status: SaleLineStatus
    backorder_quantity: int
    product_category: str | None = None
    item_category: str | None = None
    warehouse_id: int | None = None
    warehouse_name: str | None = None
    storage_location_id: int | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    delivery_block: str | None = None
    billing_block: str | None = None
    rejection_reason: str | None = None
    net_weight: Decimal | None = None
    gross_weight: Decimal | None = None
    volume: Decimal | None = None
    substitute_product_id: int | None = None
    substitute_product_sku: str | None = None
    line_text: str | None = None


class SaleOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    order_status: SaleOrderStatus
    order_date: date
    order_type: SaleOrderType
    sales_channel: SaleChannel | None
    order_source: SaleOrderSource | None
    priority: OrderPriority
    salesperson_id: int | None = None
    salesperson_email: str | None = None
    is_pos_checkout: bool
    customer_id: int | None
    customer_name: str | None = None
    cashier_email: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    updated_by_email: str | None = None
    items: list[SaleItemRead]
    partners: list[SalePartnerRead] = []
    summary: SaleOrderSummary | None = None
    gross_total: Decimal
    header_discount_amount: Decimal
    freight_amount: Decimal
    insurance_amount: Decimal
    handling_amount: Decimal
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    amount_paid: Decimal
    payment_status: DocumentPaymentStatus
    currency_code: str
    price_list_code: str | None = None
    pricing_procedure: str | None = None
    payment_terms: str | None = None
    payment_due_date: date | None = None
    payment_method_id: int | None = None
    warehouse_id: int | None = None
    warehouse_name: str | None = None
    shipping_point_id: int | None = None
    shipping_point_name: str | None = None
    partial_delivery_allowed: bool
    complete_delivery_required: bool = False
    planned_ship_date: date | None = None
    requested_delivery_date: date | None = None
    shipping_method: str | None = None
    shipping_conditions: str | None = None
    transportation_group: str | None = None
    loading_group: str | None = None
    incoterms: str | None = None
    incoterms_location: str | None = None
    delivery_block: str | None = None
    sales_organization: str | None = None
    distribution_channel: str | None = None
    division: str | None = None
    sales_office: str | None = None
    sales_group: str | None = None
    customer_po_number: str | None = None
    customer_po_date: date | None = None
    opportunity_id: int | None = None
    campaign_id: str | None = None
    price_group: str | None = None
    header_text: str | None = None
    credit_check_status: CreditCheckStatus
    atp_check_status: AtpCheckStatus
    invoice_status: BillingStatus | None = None
    delivery_status: DeliveryStatus | None = None
    approval_status: str | None = None
    customer_snapshot: dict[str, Any] | None = None
    pricing_conditions: dict[str, Any] | None = None
    delivery_logistics: dict[str, Any] | None = None
    billing_financial: dict[str, Any] | None = None
    terms_compliance: dict[str, Any] | None = None
    references: dict[str, Any] | None = None
    attachments: list[dict[str, Any]] | None = None
    workflow_history: list[dict[str, Any]] | None = None


class SaleListItem(BaseModel):
    id: int
    order_number: str
    order_status: SaleOrderStatus
    order_type: SaleOrderType
    customer_id: int | None
    customer_name: str | None
    cashier_email: str | None
    created_at: datetime
    order_date: date
    item_count: int
    total: Decimal
    payment_status: DocumentPaymentStatus
    currency_code: str
    delivery_status: DeliveryStatus | None = None


class SaleListResponse(BaseModel):
    items: list[SaleListItem]
    total: int


class SaleLookupCustomer(BaseModel):
    id: int
    customer_code: str | None
    name: str


class SaleLookupWarehouse(BaseModel):
    id: int
    code: str
    name: str


class SaleLookupUser(BaseModel):
    id: int
    email: str


class SaleLookupTaxRate(BaseModel):
    id: int
    code: str
    name: str
    rate_percent: Decimal


class SaleLookupPaymentMethod(BaseModel):
    id: int
    code: str
    name: str


class SaleLookupsResponse(BaseModel):
    customers: list[SaleLookupCustomer]
    warehouses: list[SaleLookupWarehouse]
    users: list[SaleLookupUser]
    tax_rates: list[SaleLookupTaxRate]
    payment_methods: list[SaleLookupPaymentMethod] = []
