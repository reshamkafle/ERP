export type ProcurementFieldType = "text" | "number" | "date" | "textarea" | "select"

export type ProcurementFieldDef = {
  path: string
  label: string
  type?: ProcurementFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type ProcurementSectionDef = {
  id: string
  title: string
  description?: string
  fields: ProcurementFieldDef[]
  isLineItems?: boolean
}

const statusOptions = [
  { value: "DRAFT", label: "Draft" },
  { value: "PENDING", label: "Pending approval" },
  { value: "APPROVED", label: "Approved" },
  { value: "RELEASED", label: "Released" },
  { value: "REJECTED", label: "Rejected" },
  { value: "CANCELLED", label: "Cancelled" },
  { value: "PARKED", label: "Parked" },
  { value: "POSTED", label: "Posted" },
  { value: "BLOCKED", label: "Blocked" },
  { value: "PAID", label: "Paid" },
]

const categoryOptions = [
  { value: "", label: "—" },
  { value: "GOODS", label: "Goods" },
  { value: "SERVICES", label: "Services" },
  { value: "CAPEX", label: "Capex" },
  { value: "OPEX", label: "Opex" },
]

const inspectionOptions = [
  { value: "", label: "—" },
  { value: "ACCEPTED", label: "Accepted" },
  { value: "REJECTED", label: "Rejected" },
  { value: "PARTIAL", label: "Partial" },
]

const coreRecordFields: ProcurementFieldDef[] = [
  { path: "reference", label: "Record reference" },
  { path: "title", label: "Title / summary" },
  {
    path: "status",
    label: "Status",
    type: "select",
    options: statusOptions,
  },
  { path: "description", label: "Description / notes", type: "textarea", colSpan: 2 },
  { path: "party_name", label: "Party / vendor name" },
  { path: "amount", label: "Amount", type: "number" },
  { path: "start_date", label: "Start / document date", type: "date" },
  { path: "end_date", label: "End / due date", type: "date" },
]

export const prLineItemFields: ProcurementFieldDef[] = [
  { path: "item_code", label: "Item code" },
  { path: "description", label: "Description" },
  { path: "specifications", label: "Specifications" },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "uom", label: "UOM" },
]

export const poLineItemFields: ProcurementFieldDef[] = [
  { path: "item_code", label: "Item code" },
  { path: "description", label: "Description" },
  { path: "uom", label: "UOM" },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "unit_price", label: "Unit price", type: "number" },
  { path: "discount", label: "Discount", type: "number" },
  { path: "tax", label: "Tax", type: "number" },
  { path: "total", label: "Line total", type: "number" },
]

export const grnLineItemFields: ProcurementFieldDef[] = [
  { path: "item_code", label: "Item code" },
  { path: "received_qty", label: "Received qty", type: "number" },
  { path: "uom", label: "UOM" },
  { path: "batch_serial_lot", label: "Batch / serial / lot" },
  { path: "damage_notes", label: "Damage / shortage notes", type: "textarea", colSpan: 2 },
]

export const invoiceLineItemFields: ProcurementFieldDef[] = [
  { path: "item_code", label: "Item code" },
  { path: "matched_qty", label: "Matched qty", type: "number" },
  { path: "unit_price", label: "Unit price", type: "number" },
  { path: "line_amount", label: "Line amount", type: "number" },
]

const prHeaderFields: ProcurementFieldDef[] = [
  { path: "header.requisition_number", label: "Requisition number" },
  { path: "header.requester_name", label: "Requester name" },
  { path: "header.department", label: "Department" },
  { path: "header.cost_center", label: "Cost center" },
  { path: "header.required_delivery_date", label: "Required delivery date", type: "date" },
  { path: "header.budget_reference", label: "Budget reference" },
  { path: "header.gl_account", label: "GL account" },
  { path: "header.justification", label: "Justification / notes", type: "textarea", colSpan: 2 },
  { path: "header.approval_workflow", label: "Approval workflow" },
  {
    path: "header.category",
    label: "Category",
    type: "select",
    options: categoryOptions,
  },
]

const poHeaderFields: ProcurementFieldDef[] = [
  { path: "header.po_number", label: "PO number (auto if blank)" },
  { path: "header.vendor_code", label: "Vendor code" },
  { path: "header.vendor_name", label: "Vendor name" },
  { path: "header.po_date", label: "PO date", type: "date" },
  { path: "header.validity_end_date", label: "Validity end date", type: "date" },
  { path: "header.ship_to_address", label: "Delivery / ship-to", type: "textarea", colSpan: 2 },
  { path: "header.payment_terms", label: "Payment terms" },
  { path: "header.incoterms", label: "Incoterms" },
  { path: "header.freight_charges", label: "Freight & other charges", type: "number" },
  { path: "header.approval_status", label: "Approval status" },
  { path: "header.release_strategy", label: "Release strategy" },
  { path: "header.pr_reference", label: "PR reference" },
  { path: "header.contract_reference", label: "Contract reference" },
  { path: "header.rfq_reference", label: "RFQ reference" },
  { path: "header.delivery_schedule_notes", label: "Delivery schedule", type: "textarea", colSpan: 2 },
]

const grnHeaderFields: ProcurementFieldDef[] = [
  { path: "header.grn_number", label: "GRN number" },
  { path: "header.po_reference", label: "PO reference" },
  { path: "header.receipt_date", label: "Receipt date", type: "date" },
  { path: "header.receipt_time", label: "Receipt time" },
  {
    path: "header.inspection_status",
    label: "Inspection status",
    type: "select",
    options: inspectionOptions,
  },
  { path: "header.storage_location", label: "Storage location / bin" },
  { path: "header.transporter", label: "Transporter" },
  { path: "header.lr_number", label: "LR number" },
  { path: "header.receipt_notes", label: "Receipt notes", type: "textarea", colSpan: 2 },
]

const invoiceHeaderFields: ProcurementFieldDef[] = [
  { path: "header.supplier_invoice_number", label: "Supplier invoice number" },
  { path: "header.supplier_invoice_date", label: "Invoice date", type: "date" },
  { path: "header.invoice_amount", label: "Invoice amount", type: "number" },
  { path: "header.currency", label: "Currency" },
  { path: "header.tax_breakdown", label: "Tax breakdown", type: "textarea", colSpan: 2 },
  { path: "header.po_reference", label: "PO reference" },
  { path: "header.grn_reference", label: "GRN reference" },
  { path: "header.match_status", label: "Match status (2-way / 3-way)" },
  { path: "header.payment_due_date", label: "Payment due date", type: "date" },
  { path: "header.gl_account", label: "GL account" },
  { path: "header.cost_center", label: "Cost center" },
  {
    path: "header.invoice_status",
    label: "Invoice status",
    type: "select",
    options: [
      { value: "PARKED", label: "Parked" },
      { value: "POSTED", label: "Posted" },
      { value: "BLOCKED", label: "Blocked" },
      { value: "PAID", label: "Paid" },
    ],
  },
]

const FEATURE_SECTIONS: Record<string, ProcurementSectionDef[]> = {
  purchase_requisitions: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "pr", title: "Purchase requisition", fields: prHeaderFields },
    {
      id: "lines",
      title: "Line items",
      description: "Items requested on this requisition.",
      fields: prLineItemFields,
      isLineItems: true,
    },
  ],
  purchase_orders: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "po", title: "Purchase order", fields: poHeaderFields },
    {
      id: "lines",
      title: "Line items",
      description: "PO lines — item, quantity, pricing.",
      fields: poLineItemFields,
      isLineItems: true,
    },
  ],
  goods_receipt: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "grn", title: "Goods receipt (GRN)", fields: grnHeaderFields },
    {
      id: "lines",
      title: "Received lines",
      fields: grnLineItemFields,
      isLineItems: true,
    },
  ],
  invoice_matching: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "inv", title: "Supplier invoice", fields: invoiceHeaderFields },
    {
      id: "lines",
      title: "Matching lines",
      fields: invoiceLineItemFields,
      isLineItems: true,
    },
  ],
  vendor_management: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    {
      id: "hint",
      title: "Vendor master",
      description:
        "Operational vendor master is maintained under Suppliers. Use this record for procurement workflow notes only.",
      fields: [{ path: "header.vendor_code", label: "Linked vendor code" }],
    },
  ],
}

export const PROCUREMENT_FEATURE_OPTIONS = [
  { value: "purchase_requisitions", label: "Purchase Requisition (PR)" },
  { value: "purchase_orders", label: "Purchase Order (PO)" },
  { value: "goods_receipt", label: "Goods Receipt (GRN)" },
  { value: "invoice_matching", label: "Invoice Matching" },
] as const

export function getProcurementSectionsForFeature(
  featureCode: string,
): ProcurementSectionDef[] {
  return FEATURE_SECTIONS[featureCode] ?? FEATURE_SECTIONS.purchase_requisitions
}

export function lineItemFieldsForFeature(featureCode: string): ProcurementFieldDef[] {
  switch (featureCode) {
    case "purchase_orders":
      return poLineItemFields
    case "goods_receipt":
      return grnLineItemFields
    case "invoice_matching":
      return invoiceLineItemFields
    default:
      return prLineItemFields
  }
}
