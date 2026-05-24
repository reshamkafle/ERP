import { z } from "zod"

import type { ModuleRecord } from "@/types/module"
import { tmsLineItemFields } from "@/lib/tms-field-groups"

const optionalStr = z.string()

export const TMS_MODULE_CODE = "tms"

export const TMS_FEATURE_CODE = "shipments"

const basicSchema = z.object({
  shipment_id: optionalStr,
  order_reference: optionalStr,
  shipment_type: optionalStr,
  shipment_date: optionalStr,
  requested_delivery_date: optionalStr,
  service_level: optionalStr,
  transport_mode: optionalStr,
})

const addressSchema = z.object({
  street: optionalStr,
  city: optionalStr,
  state: optionalStr,
  zip: optionalStr,
  country: optionalStr,
})

const shipperSchema = addressSchema.extend({
  warehouse_code: optionalStr,
  contact_name: optionalStr,
  contact_phone: optionalStr,
  loading_appointment: optionalStr,
  loading_time_window: optionalStr,
})

const consigneeSchema = addressSchema.extend({
  ship_to_location: optionalStr,
  contact_name: optionalStr,
  contact_phone: optionalStr,
  delivery_appointment: optionalStr,
  delivery_time_window: optionalStr,
})

export const tmsLineItemSchema = z.object({
  item_number: optionalStr,
  item_description: optionalStr,
  quantity: optionalStr,
  weight_per_unit: optionalStr,
  weight_total: optionalStr,
  length: optionalStr,
  width: optionalStr,
  height: optionalStr,
  volume: optionalStr,
  packaging_type: optionalStr,
  hazardous_material: optionalStr,
})

const carrierSchema = z.object({
  carrier_name: optionalStr,
  carrier_code: optionalStr,
  carrier_service: optionalStr,
  quoted_rate: optionalStr,
  freight_cost: optionalStr,
  accessorial_charges: optionalStr,
  tracking_number: optionalStr,
})

const complianceSchema = z.object({
  bol_number: optionalStr,
  customs_compliance_data: optionalStr,
  insurance_value: optionalStr,
  special_instructions: optionalStr,
  label_requirements: optionalStr,
})

const trackingSchema = z.object({
  current_status: optionalStr,
  eta: optionalStr,
  actual_pickup_datetime: optionalStr,
  actual_delivery_datetime: optionalStr,
  pod_reference: optionalStr,
  exception_reason: optionalStr,
})

const financialSchema = z.object({
  freight_bill_amount: optionalStr,
  carrier_invoice_number: optionalStr,
  payment_status: optionalStr,
  cost_center: optionalStr,
  custom_fields: optionalStr,
})

export const tmsFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  basic: basicSchema,
  shipper: shipperSchema,
  consignee: consigneeSchema,
  line_items: z.array(tmsLineItemSchema),
  carrier: carrierSchema,
  compliance: complianceSchema,
  tracking: trackingSchema,
  financial: financialSchema,
})

export type TmsFormValues = z.infer<typeof tmsFormSchema>
export type TmsLineItem = z.infer<typeof tmsLineItemSchema>

function emptyBasic(): TmsFormValues["basic"] {
  return {
    shipment_id: "",
    order_reference: "",
    shipment_type: "",
    shipment_date: "",
    requested_delivery_date: "",
    service_level: "",
    transport_mode: "",
  }
}

function emptyShipper(): TmsFormValues["shipper"] {
  return {
    warehouse_code: "",
    street: "",
    city: "",
    state: "",
    zip: "",
    country: "",
    contact_name: "",
    contact_phone: "",
    loading_appointment: "",
    loading_time_window: "",
  }
}

function emptyConsignee(): TmsFormValues["consignee"] {
  return {
    ship_to_location: "",
    street: "",
    city: "",
    state: "",
    zip: "",
    country: "",
    contact_name: "",
    contact_phone: "",
    delivery_appointment: "",
    delivery_time_window: "",
  }
}

export function emptyTmsLineItem(): TmsLineItem {
  return {
    item_number: "",
    item_description: "",
    quantity: "",
    weight_per_unit: "",
    weight_total: "",
    length: "",
    width: "",
    height: "",
    volume: "",
    packaging_type: "",
    hazardous_material: "",
  }
}

function emptyCarrier(): TmsFormValues["carrier"] {
  return {
    carrier_name: "",
    carrier_code: "",
    carrier_service: "",
    quoted_rate: "",
    freight_cost: "",
    accessorial_charges: "",
    tracking_number: "",
  }
}

function emptyCompliance(): TmsFormValues["compliance"] {
  return {
    bol_number: "",
    customs_compliance_data: "",
    insurance_value: "",
    special_instructions: "",
    label_requirements: "",
  }
}

function emptyTracking(): TmsFormValues["tracking"] {
  return {
    current_status: "",
    eta: "",
    actual_pickup_datetime: "",
    actual_delivery_datetime: "",
    pod_reference: "",
    exception_reason: "",
  }
}

function emptyFinancial(): TmsFormValues["financial"] {
  return {
    freight_bill_amount: "",
    carrier_invoice_number: "",
    payment_status: "",
    cost_center: "",
    custom_fields: "",
  }
}

export const defaultTmsFormValues: TmsFormValues = {
  feature_code: TMS_FEATURE_CODE,
  reference: "",
  title: "",
  status: "PLANNED",
  description: "",
  basic: emptyBasic(),
  shipper: emptyShipper(),
  consignee: emptyConsignee(),
  line_items: [],
  carrier: emptyCarrier(),
  compliance: emptyCompliance(),
  tracking: emptyTracking(),
  financial: emptyFinancial(),
}

function strField(value: unknown): string {
  return typeof value === "string" ? value : value != null ? String(value) : ""
}

function categoryFromExtra<T extends Record<string, string>>(
  extra: Record<string, unknown> | undefined,
  key: string,
  defaults: () => T,
): T {
  const raw = extra?.[key]
  if (!raw || typeof raw !== "object") return defaults()
  const out = { ...defaults() }
  for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
    if (k in out) {
      ;(out as Record<string, string>)[k] = strField(v)
    }
  }
  return out
}

function lineItemsFromExtra(extra: Record<string, unknown> | undefined): TmsLineItem[] {
  const raw = extra?.line_items
  if (!Array.isArray(raw)) return []
  return raw.map((row) => {
    const base = emptyTmsLineItem()
    if (!row || typeof row !== "object") return base
    for (const [k, v] of Object.entries(row as Record<string, unknown>)) {
      if (k in base) {
        ;(base as Record<string, string>)[k] = strField(v)
      }
    }
    return base
  })
}

export function recordToForm(record: ModuleRecord): TmsFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, unknown>
  const lines = lineItemsFromExtra(extra)

  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    basic: {
      ...emptyBasic(),
      ...categoryFromExtra(extra, "basic", emptyBasic),
      shipment_id: categoryFromExtra(extra, "basic", emptyBasic).shipment_id || record.reference,
    },
    shipper: categoryFromExtra(extra, "shipper", emptyShipper),
    consignee: categoryFromExtra(extra, "consignee", emptyConsignee),
    line_items: lines,
    carrier: categoryFromExtra(extra, "carrier", emptyCarrier),
    compliance: categoryFromExtra(extra, "compliance", emptyCompliance),
    tracking: categoryFromExtra(extra, "tracking", emptyTracking),
    financial: categoryFromExtra(extra, "financial", emptyFinancial),
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevel(values: TmsFormValues) {
  const carrierName = values.carrier.carrier_name.trim()
  const consigneeName = values.consignee.ship_to_location.trim()
  const party = carrierName || consigneeName || null

  const amount =
    parseOptionalNumber(values.carrier.freight_cost) ??
    parseOptionalNumber(values.financial.freight_bill_amount)

  const shipmentType = values.basic.shipment_type.trim()
  const shipTo = values.consignee.ship_to_location.trim()
  let title = values.title.trim()
  if (!title) {
    if (shipmentType && shipTo) {
      title = `${shipmentType} — ${shipTo}`
    } else if (shipTo) {
      title = shipTo
    } else {
      title = "Shipment"
    }
  }

  return {
    title,
    party_name: party,
    amount,
    start_date: values.basic.shipment_date.trim() || null,
    end_date: values.basic.requested_delivery_date.trim() || null,
  }
}

function buildExtraData(values: TmsFormValues) {
  const basic = { ...values.basic }
  const shipmentId = basic.shipment_id.trim()
  if (!shipmentId) {
    basic.shipment_id = values.reference.trim()
  }

  return {
    basic,
    shipper: values.shipper,
    consignee: values.consignee,
    line_items: values.line_items,
    carrier: values.carrier,
    compliance: values.compliance,
    tracking: values.tracking,
    financial: values.financial,
  }
}

export function formToCreatePayload(values: TmsFormValues) {
  const top = deriveTopLevel(values)
  const reference = values.basic.shipment_id.trim() || values.reference.trim() || newTmsReference()

  return {
    feature_code: TMS_FEATURE_CODE,
    reference,
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: null,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: buildExtraData({ ...values, reference }),
  }
}

export function formToUpdatePayload(values: TmsFormValues) {
  const top = deriveTopLevel(values)

  return {
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: null,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: buildExtraData(values),
  }
}

export function newTmsReference(): string {
  return `SHP-${Date.now().toString(36).toUpperCase()}`
}

export function keyLabelFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data as Record<string, unknown> | undefined
  const carrier = (extra?.carrier ?? {}) as Record<string, unknown>
  const basic = (extra?.basic ?? {}) as Record<string, unknown>
  const tracking = strField(carrier.tracking_number)
  if (tracking) return tracking
  return strField(basic.shipment_id) || record.reference
}

export function tmsLineFields() {
  return tmsLineItemFields
}
