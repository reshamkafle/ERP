export type SalesFieldType =
  | "text"
  | "number"
  | "date"
  | "textarea"
  | "select"
  | "checkbox"
  | "customer_select"
  | "warehouse_select"
  | "user_select"
  | "payment_method_select"

export type SalesFieldDef = {
  path: string
  label: string
  type?: SalesFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
  readOnly?: boolean
  section?: string
}

export type SalesTabDef = {
  id: string
  title: string
  description?: string
  fields: SalesFieldDef[]
  isLineItems?: boolean
  isPartners?: boolean
  isSummary?: boolean
  isAttachments?: boolean
  isWorkflowHistory?: boolean
}

const emptyOption = { value: "", label: "—" }

const orderTypeOptions = [
  { value: "STANDARD", label: "Standard" },
  { value: "RUSH", label: "Rush" },
  { value: "SAMPLE", label: "Sample" },
  { value: "RETURN", label: "Return" },
  { value: "EXPORT", label: "Export" },
]

const orderStatusLabels = [
  { value: "DRAFT", label: "Draft" },
  { value: "CREATED", label: "Created" },
  { value: "RELEASED", label: "Released / Approved" },
  { value: "IN_PROCESS", label: "In process" },
  { value: "DELIVERED", label: "Delivered / Completed" },
  { value: "INVOICED", label: "Invoiced" },
  { value: "CLOSED", label: "Closed" },
  { value: "CANCELLED", label: "Cancelled / Rejected" },
]

const channelOptions = [
  emptyOption,
  { value: "DIRECT", label: "Direct" },
  { value: "DISTRIBUTOR", label: "Distributor" },
  { value: "ECOMMERCE", label: "E-commerce" },
  { value: "RETAIL", label: "Retail" },
]

const sourceOptions = [
  emptyOption,
  { value: "PHONE", label: "Phone" },
  { value: "EMAIL", label: "Email" },
  { value: "PORTAL", label: "Portal" },
  { value: "WEBSITE", label: "Website" },
  { value: "EDI", label: "EDI" },
  { value: "MOBILE", label: "Mobile App" },
]

const priorityOptions = [
  { value: "HIGH", label: "High" },
  { value: "MEDIUM", label: "Medium" },
  { value: "LOW", label: "Low" },
]

const customerGroupOptions = [
  emptyOption,
  { value: "RETAIL", label: "Retail" },
  { value: "WHOLESALE", label: "Wholesale" },
  { value: "CORPORATE", label: "Corporate" },
  { value: "GOVERNMENT", label: "Government" },
  { value: "DISTRIBUTOR", label: "Distributor" },
]

const paymentTermsOptions = [
  emptyOption,
  { value: "NET_30", label: "Net 30" },
  { value: "NET_60", label: "Net 60" },
  { value: "NET_90", label: "Net 90" },
  { value: "ADVANCE", label: "Advance payment" },
  { value: "COD", label: "Cash on delivery" },
  { value: "DUE_ON_RECEIPT", label: "Due on receipt" },
]

const incotermsOptions = [
  emptyOption,
  { value: "EXW", label: "EXW" },
  { value: "FOB", label: "FOB" },
  { value: "CIF", label: "CIF" },
  { value: "DDP", label: "DDP" },
  { value: "DAP", label: "DAP" },
]

const billingTypeOptions = [
  emptyOption,
  { value: "STANDARD", label: "Standard invoice" },
  { value: "CREDIT_MEMO", label: "Credit memo" },
  { value: "DEBIT_MEMO", label: "Debit memo" },
  { value: "PROFORMA", label: "Proforma" },
]

const paymentMethodOptions = [
  emptyOption,
  { value: "BANK_TRANSFER", label: "Bank transfer" },
  { value: "CHECK", label: "Check" },
  { value: "CARD", label: "Card" },
  { value: "CASH", label: "Cash" },
  { value: "UPI", label: "UPI / digital wallet" },
]

const orderReasonOptions = [
  emptyOption,
  { value: "CAMPAIGN", label: "Marketing campaign" },
  { value: "TENDER", label: "Tender / RFP" },
  { value: "REPEAT", label: "Repeat business" },
  { value: "SAMPLE", label: "Sample conversion" },
  { value: "OTHER", label: "Other" },
]

const approvalStatusOptions = [
  emptyOption,
  { value: "PENDING", label: "Pending" },
  { value: "APPROVED", label: "Approved" },
  { value: "BLOCKED", label: "Blocked" },
  { value: "REJECTED", label: "Rejected" },
]

const creditApprovalOptions = [
  emptyOption,
  { value: "NOT_RUN", label: "Not run" },
  { value: "PASSED", label: "Passed" },
  { value: "FAILED", label: "Failed" },
  { value: "OVERRIDE", label: "Override" },
]

export const PARTNER_ROLE_LABELS: Record<string, string> = {
  SOLD_TO: "Sold-To Party",
  SHIP_TO: "Ship-To Party",
  BILL_TO: "Bill-To Party",
  PAYER: "Payer / Payment Party",
  FORWARDING_AGENT: "Forwarding Agent / Carrier",
  SALES_EMPLOYEE: "Sales Employee / Agent",
}

/** Ten ERP field groups aligned to SD order entry */
export const SALES_ORDER_TABS: SalesTabDef[] = [
  {
    id: "header",
    title: "Order header",
    description: "Order number, type, dates, organization, references, and status.",
    fields: [
      { path: "order_number_override", label: "Order number (manual override)", placeholder: "Leave blank for auto SO-YYYY-#####", section: "Order identification" },
      { path: "_display.order_number", label: "Sales order number (saved)", readOnly: true, section: "Order identification" },
      { path: "order_date", label: "Order date", type: "date", section: "Order identification" },
      { path: "_display.order_time", label: "Order time (from created timestamp)", readOnly: true, section: "Order identification" },
      { path: "order_type", label: "Order type", type: "select", options: orderTypeOptions, section: "Order identification" },
      { path: "sales_organization", label: "Sales organization", section: "Sales structure" },
      { path: "distribution_channel", label: "Distribution channel", section: "Sales structure" },
      { path: "division", label: "Division", section: "Sales structure" },
      { path: "sales_office", label: "Sales office", section: "Sales structure" },
      { path: "sales_group", label: "Sales group", section: "Sales structure" },
      { path: "currency_code", label: "Currency", section: "Commercial" },
      { path: "customer_po_number", label: "Customer PO number", section: "References" },
      { path: "customer_po_date", label: "Customer PO date", type: "date", section: "References" },
      { path: "references.quotation_number", label: "Quotation reference", section: "References" },
      { path: "references.contract_number", label: "Contract reference", section: "References" },
      { path: "references.tender_number", label: "Tender number", section: "References" },
      { path: "salesperson_id", label: "Sales employee / agent", type: "user_select", section: "Sales team" },
      { path: "sales_channel", label: "Sales channel", type: "select", options: channelOptions, section: "Sales team" },
      { path: "order_source", label: "Order source", type: "select", options: sourceOptions, section: "Sales team" },
      { path: "priority", label: "Delivery priority", type: "select", options: priorityOptions, section: "Sales team" },
      { path: "payment_terms", label: "Payment terms", type: "select", options: paymentTermsOptions, section: "Commercial" },
      { path: "incoterms", label: "Incoterms", type: "select", options: incotermsOptions, section: "Commercial" },
      { path: "incoterms_location", label: "Incoterms location", section: "Commercial" },
      { path: "warehouse_id", label: "Shipping point / plant", type: "warehouse_select", section: "Logistics" },
      { path: "order_status", label: "Order status", type: "select", options: orderStatusLabels, readOnly: true, section: "Status" },
      { path: "approval_status", label: "Approval status", type: "select", options: approvalStatusOptions, section: "Status" },
      { path: "delivery_block", label: "Delivery block", section: "Status" },
      { path: "delivery_status", label: "Delivery status", readOnly: true, section: "Status" },
      { path: "invoice_status", label: "Billing status", readOnly: true, section: "Status" },
      { path: "credit_check_status", label: "Credit check", readOnly: true, section: "Status" },
      { path: "atp_check_status", label: "ATP check", readOnly: true, section: "Status" },
      { path: "_display.created_by", label: "Created by", readOnly: true, section: "Audit trail" },
      { path: "_display.created_at", label: "Created at", readOnly: true, section: "Audit trail" },
      { path: "_display.updated_by", label: "Changed by", readOnly: true, section: "Audit trail" },
      { path: "_display.updated_at", label: "Changed at", readOnly: true, section: "Audit trail" },
    ],
  },
  {
    id: "customer",
    title: "Customer",
    description: "Customer master data — code, contacts, credit, tax, and addresses.",
    fields: [
      { path: "customer_id", label: "Customer (Sold-To)", type: "customer_select", section: "Identification" },
      { path: "customer_snapshot.customer_code", label: "Customer code / ID", readOnly: true, section: "Identification" },
      { path: "customer_snapshot.name", label: "Customer name", colSpan: 2, section: "Identification" },
      { path: "customer_snapshot.customer_group", label: "Customer group / category", type: "select", options: customerGroupOptions, section: "Identification" },
      { path: "customer_snapshot.contact_name", label: "Contact person", section: "Contact" },
      { path: "customer_snapshot.contact_phone", label: "Contact phone", section: "Contact" },
      { path: "customer_snapshot.contact_email", label: "Contact email", section: "Contact" },
      { path: "customer_snapshot.credit_limit", label: "Credit limit", section: "Credit & terms" },
      { path: "customer_snapshot.credit_status", label: "Credit status", section: "Credit & terms" },
      { path: "customer_snapshot.payment_terms", label: "Customer payment terms", type: "select", options: paymentTermsOptions, section: "Credit & terms" },
      { path: "customer_snapshot.tax_id", label: "Tax ID", section: "Tax registration" },
      { path: "customer_snapshot.gst_number", label: "GST number", section: "Tax registration" },
      { path: "customer_snapshot.vat_number", label: "VAT number", section: "Tax registration" },
      { path: "header_text", label: "Special instructions from customer", type: "textarea", colSpan: 2, section: "Instructions" },
      { path: "customer_snapshot.billing_address.line1", label: "Bill-To address line 1", colSpan: 2, section: "Bill-To address" },
      { path: "customer_snapshot.billing_address.line2", label: "Bill-To address line 2", colSpan: 2, section: "Bill-To address" },
      { path: "customer_snapshot.billing_address.city", label: "Bill-To city", section: "Bill-To address" },
      { path: "customer_snapshot.billing_address.state", label: "Bill-To state / province", section: "Bill-To address" },
      { path: "customer_snapshot.billing_address.postal_code", label: "Bill-To postal code", section: "Bill-To address" },
      { path: "customer_snapshot.billing_address.country", label: "Bill-To country", section: "Bill-To address" },
      { path: "customer_snapshot.shipping_address.line1", label: "Ship-To address line 1", colSpan: 2, section: "Ship-To address" },
      { path: "customer_snapshot.shipping_address.line2", label: "Ship-To address line 2", colSpan: 2, section: "Ship-To address" },
      { path: "customer_snapshot.shipping_address.city", label: "Ship-To city", section: "Ship-To address" },
      { path: "customer_snapshot.shipping_address.state", label: "Ship-To state / province", section: "Ship-To address" },
      { path: "customer_snapshot.shipping_address.postal_code", label: "Ship-To postal code", section: "Ship-To address" },
      { path: "customer_snapshot.shipping_address.country", label: "Ship-To country", section: "Ship-To address" },
    ],
  },
  {
    id: "lines",
    title: "Line items",
    description: "Material, quantity, plant, delivery dates, weights, and line status.",
    isLineItems: true,
    fields: [],
  },
  {
    id: "pricing",
    title: "Pricing",
    description: "List price, discounts, taxes, freight, pricing procedure, and overrides.",
    fields: [
      { path: "price_list_code", label: "Price list / list price code", section: "Commercial" },
      { path: "pricing_procedure", label: "Pricing procedure", section: "Commercial" },
      { path: "pricing_conditions.pricing_date", label: "Pricing date", type: "date", section: "Commercial" },
      { path: "pricing_conditions.special_pricing_agreement", label: "Special / promotional pricing", section: "Commercial" },
      { path: "pricing_conditions.contract_ref", label: "Contract reference (pricing)", section: "Commercial" },
      { path: "pricing_conditions.line_discount_notes", label: "Pricing condition records / discount notes", type: "textarea", colSpan: 2, section: "Commercial" },
      { path: "pricing_conditions.manual_price_override_reason", label: "Manual price override reason", type: "textarea", colSpan: 2, section: "Commercial" },
      { path: "pricing_conditions.list_price_notes", label: "List price notes", section: "Commercial" },
      { path: "header_discount_amount", label: "Header discount amount", type: "number", section: "Charges" },
      { path: "freight_amount", label: "Freight / shipping charges", type: "number", section: "Charges" },
      { path: "insurance_amount", label: "Insurance charges", type: "number", section: "Charges" },
      { path: "handling_amount", label: "Handling charges", type: "number", section: "Charges" },
      { path: "_display.subtotal", label: "Net value (saved)", readOnly: true, section: "Totals (read-only after save)" },
      { path: "_display.tax_amount", label: "Tax value (saved)", readOnly: true, section: "Totals (read-only after save)" },
      { path: "_display.gross_total", label: "Gross value (saved)", readOnly: true, section: "Totals (read-only after save)" },
    ],
  },
  {
    id: "delivery",
    title: "Shipping & logistics",
    description: "Delivery, carrier, route, partners, packaging, and shipping instructions.",
    isPartners: true,
    fields: [
      { path: "delivery_logistics.delivery_number", label: "Delivery number", section: "Delivery document" },
      { path: "requested_delivery_date", label: "Requested delivery date", type: "date", section: "Delivery document" },
      { path: "delivery_logistics.promised_date", label: "Promised / commitment date", type: "date", section: "Delivery document" },
      { path: "delivery_logistics.expected_shipment_date", label: "Expected shipment date", type: "date", section: "Delivery document" },
      { path: "planned_ship_date", label: "Planned ship date", type: "date", section: "Delivery document" },
      { path: "delivery_logistics.actual_date", label: "Actual delivery date", type: "date", section: "Delivery document" },
      { path: "shipping_method", label: "Shipping method / carrier", section: "Carrier & transport" },
      { path: "delivery_logistics.carrier_name", label: "Carrier name", section: "Carrier & transport" },
      { path: "delivery_logistics.tracking_number", label: "Tracking number", section: "Carrier & transport" },
      { path: "delivery_logistics.transport_mode", label: "Mode of transport", section: "Carrier & transport" },
      { path: "delivery_logistics.route", label: "Route determination / route code", section: "Carrier & transport" },
      { path: "delivery_logistics.bill_of_lading", label: "Bill of lading / airway bill", section: "Carrier & transport" },
      { path: "transportation_group", label: "Transportation group", section: "Carrier & transport" },
      { path: "loading_group", label: "Loading group", section: "Carrier & transport" },
      { path: "shipping_conditions", label: "Shipping conditions", section: "Terms" },
      { path: "shipping_point_id", label: "Shipping point / storage location", type: "warehouse_select", section: "Plant" },
      { path: "delivery_logistics.warehouse_assignment", label: "Warehouse assignment notes", section: "Plant" },
      { path: "partial_delivery_allowed", label: "Partial delivery allowed", type: "checkbox", section: "Delivery control" },
      { path: "complete_delivery_required", label: "Complete delivery required", type: "checkbox", section: "Delivery control" },
      { path: "delivery_block", label: "Delivery block", section: "Delivery control" },
      { path: "delivery_logistics.packaging_details", label: "Packaging details", type: "textarea", colSpan: 2, section: "Packaging" },
      { path: "delivery_logistics.shipping_instructions", label: "Shipping instructions", type: "textarea", colSpan: 2, section: "Alternate ship-to" },
      { path: "delivery_logistics.ship_to_override.line1", label: "Alternate delivery address line 1", colSpan: 2, section: "Alternate ship-to" },
      { path: "delivery_logistics.ship_to_override.city", label: "Alternate delivery city", section: "Alternate ship-to" },
      { path: "delivery_logistics.ship_to_override.state", label: "Alternate delivery state", section: "Alternate ship-to" },
      { path: "delivery_logistics.ship_to_override.postal_code", label: "Alternate delivery postal code", section: "Alternate ship-to" },
      { path: "delivery_logistics.ship_to_override.country", label: "Alternate delivery country", section: "Alternate ship-to" },
    ],
  },
  {
    id: "billing",
    title: "Billing & payment",
    description: "Invoice, billing block, payment terms, method, and finance links.",
    fields: [
      { path: "billing_financial.invoice_number", label: "Invoice number", section: "Invoice" },
      { path: "billing_financial.invoice_date", label: "Billing / invoice date", type: "date", section: "Invoice" },
      { path: "billing_financial.billing_type", label: "Invoice type", type: "select", options: billingTypeOptions, section: "Invoice" },
      { path: "billing_financial.billing_block", label: "Billing block", section: "Invoice" },
      { path: "billing_financial.split_billing", label: "Split billing required", type: "checkbox", section: "Invoice" },
      { path: "payment_due_date", label: "Payment due date", type: "date", section: "Invoice" },
      { path: "payment_method_id", label: "Payment method", type: "payment_method_select", section: "Payment" },
      { path: "billing_financial.payment_method_label", label: "Payment method (label)", type: "select", options: paymentMethodOptions, section: "Payment" },
      { path: "billing_financial.bank_details", label: "Bank details", type: "textarea", colSpan: 2, section: "Payment" },
      { path: "billing_financial.card_last_four", label: "Card last four digits", section: "Payment" },
      { path: "billing_financial.taxable_amount", label: "Invoice taxable amount", type: "number", section: "Invoice breakdown" },
      { path: "billing_financial.tax_amount", label: "Invoice tax amount", type: "number", section: "Invoice breakdown" },
      { path: "billing_financial.total_amount", label: "Invoice total amount", type: "number", section: "Invoice breakdown" },
      { path: "billing_financial.accounting_document_number", label: "Accounting document number (FI link)", section: "Finance" },
      { path: "billing_financial.cost_center", label: "Cost center", section: "Finance" },
      { path: "billing_financial.profit_center", label: "Profit center", section: "Finance" },
      { path: "billing_financial.project_code", label: "Project code", section: "Finance" },
      { path: "billing_financial.wbs_element", label: "WBS element", section: "Finance" },
      { path: "billing_financial.payment_receipt_number", label: "Payment receipt number", section: "Collection" },
      { path: "billing_financial.amount_received", label: "Amount received", type: "number", section: "Collection" },
      { path: "billing_financial.outstanding_amount", label: "Outstanding amount", type: "number", section: "Collection" },
      { path: "billing_financial.credit_debit_note_ref", label: "Credit / debit note reference", section: "Collection" },
      { path: "payment_status", label: "Payment status", readOnly: true, section: "Collection" },
      { path: "_display.amount_paid", label: "Amount paid (system)", readOnly: true, section: "Collection" },
    ],
  },
  {
    id: "compliance",
    title: "Terms & compliance",
    description: "Warranty, returns, inspection, export license, and sustainability.",
    fields: [
      { path: "terms_compliance.warranty_terms", label: "Warranty terms", type: "textarea", colSpan: 2, section: "Terms" },
      { path: "terms_compliance.return_policy_ref", label: "Return policy reference", section: "Terms" },
      { path: "terms_compliance.inspection_requirements", label: "Quality inspection requirements", type: "textarea", colSpan: 2, section: "Compliance" },
      { path: "terms_compliance.regulatory_compliance", label: "Regulatory compliance", type: "textarea", colSpan: 2, section: "Compliance" },
      { path: "terms_compliance.export_license", label: "Export license / compliance data", type: "textarea", colSpan: 2, section: "Compliance" },
      { path: "terms_compliance.hazardous_material_info", label: "Hazardous material info", type: "textarea", colSpan: 2, section: "Compliance" },
      { path: "terms_compliance.sustainability_data", label: "Environmental / sustainability data", type: "textarea", colSpan: 2, section: "Compliance" },
      { path: "terms_compliance.order_validity_date", label: "Order validity date", type: "date", section: "Validity" },
      { path: "terms_compliance.order_expiry_date", label: "Order expiry date", type: "date", section: "Validity" },
    ],
  },
  {
    id: "approvals",
    title: "Approvals & workflow",
    description: "Approval status, credit/margin/legal approval, and workflow history.",
    isWorkflowHistory: true,
    fields: [
      { path: "workflow_approval.approver_name", label: "Approver name", section: "Approval" },
      { path: "workflow_approval.approver_date", label: "Approver date", type: "date", section: "Approval" },
      { path: "workflow_approval.credit_approval_status", label: "Credit approval status", type: "select", options: creditApprovalOptions, section: "Approval" },
      { path: "workflow_approval.margin_approval_status", label: "Margin approval (low margin)", type: "select", options: approvalStatusOptions, section: "Approval" },
      { path: "workflow_approval.legal_approval_status", label: "Legal / contract approval", type: "select", options: approvalStatusOptions, section: "Approval" },
      { path: "workflow_approval.note", label: "Approval notes", type: "textarea", colSpan: 2, section: "Approval" },
      { path: "approval_status", label: "Overall approval workflow stage", type: "select", options: approvalStatusOptions, section: "Approval" },
    ],
  },
  {
    id: "additional",
    title: "Additional",
    description: "Project codes, internal order, remarks, ATP notes, and attachments.",
    isAttachments: true,
    fields: [
      { path: "references.internal_order_number", label: "Internal order number", section: "Project" },
      { path: "references.order_reason", label: "Reason for order", type: "select", options: orderReasonOptions, section: "References" },
      { path: "references.remarks", label: "Remarks / notes (external)", type: "textarea", colSpan: 2, section: "Remarks" },
      { path: "references.internal_notes", label: "Internal notes", type: "textarea", colSpan: 2, section: "Remarks" },
      { path: "references.atp_check_notes", label: "ATP check results", type: "textarea", colSpan: 2, section: "Fulfillment" },
      { path: "references.attachments_note", label: "Attachments note (PO copy, drawings)", type: "textarea", colSpan: 2, section: "Attachments" },
    ],
  },
  {
    id: "analytics",
    title: "Analytics & tracking",
    description: "Order source, campaign, forecast, probability, and expected revenue.",
    fields: [
      { path: "order_source", label: "Order source", type: "select", options: sourceOptions, section: "Source" },
      { path: "references.lead_source", label: "Campaign / lead source", section: "Source" },
      { path: "campaign_id", label: "Campaign ID", section: "Source" },
      { path: "opportunity_id", label: "CRM opportunity ID", type: "number", section: "CRM" },
      { path: "references.crm_opportunity_link", label: "Opportunity URL / reference", section: "CRM" },
      { path: "references.forecast_category", label: "Forecast category", section: "Forecast" },
      { path: "references.closing_probability", label: "Probability of closing (%)", section: "Forecast" },
      { path: "references.expected_revenue", label: "Expected revenue", type: "number", section: "Forecast" },
      { path: "references.forecast_vs_actual", label: "Forecast vs actual order", section: "Forecast" },
      { path: "references.order_confirmation_date", label: "Order confirmation date", type: "date", section: "Analytics" },
      { path: "references.fulfillment_lead_time_days", label: "Fulfillment lead time (days)", type: "number", section: "Analytics" },
      { path: "references.returns_cancellation_reason", label: "Returns / cancellation reason", type: "textarea", colSpan: 2, section: "Analytics" },
      { path: "references.profitability_analysis", label: "Profitability analysis (CO-PA notes)", type: "textarea", colSpan: 2, section: "Analytics" },
      { path: "price_group", label: "Customer / price group", section: "Analytics" },
    ],
  },
  {
    id: "summary",
    title: "Summary",
    description: "Estimated totals from line items and header charges.",
    isSummary: true,
    fields: [],
  },
]

/** Map form field paths to tab ids for inline validation highlighting */
export const SALES_FIELD_TAB_MAP: Record<string, string> = (() => {
  const map: Record<string, string> = {
    customer_id: "customer",
    customer_po_number: "header",
    payment_terms: "header",
    sales_organization: "header",
    items: "lines",
    order_number_override: "header",
  }
  for (const tab of SALES_ORDER_TABS) {
    for (const field of tab.fields) {
      if (!field.path.startsWith("_display.")) {
        map[field.path] = tab.id
      }
    }
  }
  return map
})()
