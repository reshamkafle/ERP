import { z } from "zod"

import type { ModuleRecord } from "@/types/module"
import {
  grnLineItemFields,
  invoiceLineItemFields,
  poLineItemFields,
  prLineItemFields,
} from "@/lib/procurement-field-groups"

const optionalStr = z.string()

export const PROCUREMENT_MODULE_CODE = "procurement"

export const PROCUREMENT_STATUS_OPTIONS = [
  "DRAFT",
  "PENDING",
  "APPROVED",
  "RELEASED",
  "REJECTED",
  "CANCELLED",
  "PARKED",
  "POSTED",
  "BLOCKED",
  "PAID",
] as const

export const prLineItemSchema = z.object({
  item_code: optionalStr,
  description: optionalStr,
  specifications: optionalStr,
  quantity: optionalStr,
  uom: optionalStr,
})

export const poLineItemSchema = z.object({
  item_code: optionalStr,
  description: optionalStr,
  uom: optionalStr,
  quantity: optionalStr,
  unit_price: optionalStr,
  discount: optionalStr,
  tax: optionalStr,
  total: optionalStr,
})

export const grnLineItemSchema = z.object({
  item_code: optionalStr,
  received_qty: optionalStr,
  uom: optionalStr,
  batch_serial_lot: optionalStr,
  damage_notes: optionalStr,
})

export const invoiceLineItemSchema = z.object({
  item_code: optionalStr,
  matched_qty: optionalStr,
  unit_price: optionalStr,
  line_amount: optionalStr,
})

export const prHeaderSchema = z.object({
  requisition_number: optionalStr,
  requester_name: optionalStr,
  department: optionalStr,
  cost_center: optionalStr,
  required_delivery_date: optionalStr,
  budget_reference: optionalStr,
  gl_account: optionalStr,
  justification: optionalStr,
  approval_workflow: optionalStr,
  category: optionalStr,
})

export const poHeaderSchema = z.object({
  po_number: optionalStr,
  vendor_code: optionalStr,
  vendor_name: optionalStr,
  po_date: optionalStr,
  validity_end_date: optionalStr,
  ship_to_address: optionalStr,
  payment_terms: optionalStr,
  incoterms: optionalStr,
  freight_charges: optionalStr,
  approval_status: optionalStr,
  release_strategy: optionalStr,
  pr_reference: optionalStr,
  contract_reference: optionalStr,
  rfq_reference: optionalStr,
  delivery_schedule_notes: optionalStr,
})

export const grnHeaderSchema = z.object({
  grn_number: optionalStr,
  po_reference: optionalStr,
  receipt_date: optionalStr,
  receipt_time: optionalStr,
  inspection_status: optionalStr,
  storage_location: optionalStr,
  transporter: optionalStr,
  lr_number: optionalStr,
  receipt_notes: optionalStr,
})

export const invoiceHeaderSchema = z.object({
  supplier_invoice_number: optionalStr,
  supplier_invoice_date: optionalStr,
  invoice_amount: optionalStr,
  currency: optionalStr,
  tax_breakdown: optionalStr,
  po_reference: optionalStr,
  grn_reference: optionalStr,
  match_status: optionalStr,
  payment_due_date: optionalStr,
  gl_account: optionalStr,
  cost_center: optionalStr,
  invoice_status: optionalStr,
})

export const procurementHeaderSchema = z.union([
  prHeaderSchema,
  poHeaderSchema,
  grnHeaderSchema,
  invoiceHeaderSchema,
])

export const procurementFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  party_name: optionalStr,
  amount: optionalStr,
  quantity: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  header: z.record(z.string(), optionalStr),
  line_items: z.array(z.record(z.string(), optionalStr)),
})

export type ProcurementFormValues = z.infer<typeof procurementFormSchema>
export type PrLineItem = z.infer<typeof prLineItemSchema>
export type PoLineItem = z.infer<typeof poLineItemSchema>
export type GrnLineItem = z.infer<typeof grnLineItemSchema>
export type InvoiceLineItem = z.infer<typeof invoiceLineItemSchema>

const emptyPrLine = (): PrLineItem => ({
  item_code: "",
  description: "",
  specifications: "",
  quantity: "",
  uom: "",
})

const emptyPoLine = (): PoLineItem => ({
  item_code: "",
  description: "",
  uom: "",
  quantity: "",
  unit_price: "",
  discount: "",
  tax: "",
  total: "",
})

const emptyGrnLine = (): GrnLineItem => ({
  item_code: "",
  received_qty: "",
  uom: "",
  batch_serial_lot: "",
  damage_notes: "",
})

const emptyInvoiceLine = (): InvoiceLineItem => ({
  item_code: "",
  matched_qty: "",
  unit_price: "",
  line_amount: "",
})

export function emptyLineItemForFeature(featureCode: string): Record<string, string> {
  switch (featureCode) {
    case "purchase_orders":
      return emptyPoLine()
    case "goods_receipt":
      return emptyGrnLine()
    case "invoice_matching":
      return emptyInvoiceLine()
    default:
      return emptyPrLine()
  }
}

const defaultPrHeader = (): Record<string, string> => ({
  requisition_number: "",
  requester_name: "",
  department: "",
  cost_center: "",
  required_delivery_date: "",
  budget_reference: "",
  gl_account: "",
  justification: "",
  approval_workflow: "",
  category: "",
})

const defaultPoHeader = (): Record<string, string> => ({
  po_number: "",
  vendor_code: "",
  vendor_name: "",
  po_date: "",
  validity_end_date: "",
  ship_to_address: "",
  payment_terms: "",
  incoterms: "",
  freight_charges: "",
  approval_status: "",
  release_strategy: "",
  pr_reference: "",
  contract_reference: "",
  rfq_reference: "",
  delivery_schedule_notes: "",
})

const defaultGrnHeader = (): Record<string, string> => ({
  grn_number: "",
  po_reference: "",
  receipt_date: "",
  receipt_time: "",
  inspection_status: "",
  storage_location: "",
  transporter: "",
  lr_number: "",
  receipt_notes: "",
})

const defaultInvoiceHeader = (): Record<string, string> => ({
  supplier_invoice_number: "",
  supplier_invoice_date: "",
  invoice_amount: "",
  currency: "",
  tax_breakdown: "",
  po_reference: "",
  grn_reference: "",
  match_status: "",
  payment_due_date: "",
  gl_account: "",
  cost_center: "",
  invoice_status: "",
})

export function defaultHeaderForFeature(featureCode: string): Record<string, string> {
  switch (featureCode) {
    case "purchase_orders":
      return defaultPoHeader()
    case "goods_receipt":
      return defaultGrnHeader()
    case "invoice_matching":
      return defaultInvoiceHeader()
    default:
      return defaultPrHeader()
  }
}

export const defaultProcurementFormValues: ProcurementFormValues = {
  feature_code: "purchase_requisitions",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  party_name: "",
  amount: "",
  quantity: "",
  start_date: "",
  end_date: "",
  header: defaultPrHeader(),
  line_items: [],
}

function strField(value: unknown): string {
  return typeof value === "string" ? value : value != null ? String(value) : ""
}

function headerFromExtra(extra: Record<string, unknown> | undefined): Record<string, string> {
  const raw = extra?.header
  if (!raw || typeof raw !== "object") return {}
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
    out[k] = strField(v)
  }
  return out
}

function lineItemsFromExtra(extra: Record<string, unknown> | undefined): Record<string, string>[] {
  const raw = extra?.line_items
  if (!Array.isArray(raw)) return []
  return raw.map((row) => {
    if (!row || typeof row !== "object") return {}
    const out: Record<string, string> = {}
    for (const [k, v] of Object.entries(row as Record<string, unknown>)) {
      out[k] = strField(v)
    }
    return out
  })
}

export function recordToForm(record: ModuleRecord): ProcurementFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, unknown>
  const feature = record.feature_code
  const header = { ...defaultHeaderForFeature(feature), ...headerFromExtra(extra) }
  const lines = lineItemsFromExtra(extra)

  return {
    feature_code: feature,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    party_name: record.party_name ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    quantity: record.quantity != null ? String(record.quantity) : "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    header,
    line_items: lines.length ? lines : [],
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevel(values: ProcurementFormValues) {
  const h = values.header
  let party = values.party_name.trim()
  let amount = parseOptionalNumber(values.amount)
  let startDate = values.start_date.trim() || null
  let endDate = values.end_date.trim() || null

  switch (values.feature_code) {
    case "purchase_requisitions":
      party = party || strField(h.requester_name)
      startDate = startDate || strField(h.required_delivery_date) || null
      break
    case "purchase_orders":
      party = party || strField(h.vendor_name)
      amount = amount ?? parseOptionalNumber(strField(h.freight_charges))
      startDate = startDate || strField(h.po_date) || null
      endDate = endDate || strField(h.validity_end_date) || null
      break
    case "goods_receipt":
      startDate = startDate || strField(h.receipt_date) || null
      break
    case "invoice_matching":
      party = party || strField(h.supplier_invoice_number)
      amount = amount ?? parseOptionalNumber(strField(h.invoice_amount))
      startDate = startDate || strField(h.supplier_invoice_date) || null
      endDate = endDate || strField(h.payment_due_date) || null
      break
    default:
      break
  }

  return {
    party_name: party || null,
    amount,
    quantity: parseOptionalNumber(values.quantity),
    start_date: startDate,
    end_date: endDate,
  }
}

export function formToCreatePayload(values: ProcurementFormValues) {
  const top = deriveTopLevel(values)
  const header = { ...values.header }
  const poNum = strField(header.po_number)
  const reqNum = strField(header.requisition_number)
  const grnNum = strField(header.grn_number)
  if (values.feature_code === "purchase_orders" && !poNum) {
    header.po_number = newPoNumber()
  }
  if (values.feature_code === "purchase_requisitions" && !reqNum) {
    header.requisition_number = values.reference
  }
  if (values.feature_code === "goods_receipt" && !grnNum) {
    header.grn_number = values.reference
  }

  return {
    feature_code: values.feature_code,
    reference: values.reference.trim(),
    title: values.title.trim(),
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: {
      header,
      line_items: values.line_items,
    },
  }
}

export function formToUpdatePayload(values: ProcurementFormValues) {
  const top = deriveTopLevel(values)
  return {
    title: values.title.trim(),
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: {
      header: values.header,
      line_items: values.line_items,
    },
  }
}

export function newProcurementReference(featureCode: string): string {
  const prefix =
    featureCode === "purchase_orders"
      ? "PO"
      : featureCode === "goods_receipt"
        ? "GRN"
        : featureCode === "invoice_matching"
          ? "INV"
          : "PR"
  return `${prefix}-${Date.now().toString(36).toUpperCase()}`
}

export function newPoNumber(): string {
  return `PO-${Date.now().toString(36).toUpperCase()}`
}

export function keyLabelFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data as Record<string, unknown> | undefined
  const h = (extra?.header ?? {}) as Record<string, unknown>
  switch (record.feature_code) {
    case "purchase_orders":
      return strField(h.po_number) || strField(h.vendor_code) || "—"
    case "goods_receipt":
      return strField(h.grn_number) || strField(h.po_reference) || "—"
    case "invoice_matching":
      return strField(h.supplier_invoice_number) || "—"
    case "purchase_requisitions":
      return strField(h.requisition_number) || "—"
    default:
      return "—"
  }
}

export function lineFieldsForFeature(featureCode: string) {
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
