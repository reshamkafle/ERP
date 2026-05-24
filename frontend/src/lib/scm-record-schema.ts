import { z } from "zod"

import type { ModuleRecord } from "@/types/module"
import { scmLineItemFields } from "@/lib/scm-field-groups"

const optionalStr = z.string()

export const SCM_MODULE_CODE = "scm"

export const SCM_STATUS_OPTIONS = [
  "DRAFT",
  "PENDING",
  "APPROVED",
  "IN_PROGRESS",
  "COMPLETED",
  "REJECTED",
  "CANCELLED",
] as const

const masterDataSchema = z.object({
  item_sku: optionalStr,
  item_name: optionalStr,
  item_type: optionalStr,
  primary_uom: optionalStr,
  gross_weight: optionalStr,
  net_weight: optionalStr,
  dimensions: optionalStr,
  shelf_life_days: optionalStr,
  bom_version: optionalStr,
  bom_parent_sku: optionalStr,
  supplier_code: optionalStr,
  supplier_lead_time_days: optionalStr,
  approved_vendor: optionalStr,
  customer_code: optionalStr,
  ship_to_address: optionalStr,
  credit_terms: optionalStr,
  service_level_agreement: optionalStr,
  warehouse_code: optionalStr,
  bin_location: optionalStr,
  geo_region: optionalStr,
})

const inventorySchema = z.object({
  on_hand: optionalStr,
  available: optionalStr,
  reserved: optionalStr,
  in_transit: optionalStr,
  valuation_method: optionalStr,
  lot_number: optionalStr,
  serial_number: optionalStr,
  safety_stock: optionalStr,
  reorder_point: optionalStr,
  min_stock: optionalStr,
  max_stock: optionalStr,
  abc_class: optionalStr,
  aging_bucket: optionalStr,
  last_movement_date: optionalStr,
})

const procurementSchema = z.object({
  pr_reference: optionalStr,
  po_reference: optionalStr,
  contract_reference: optionalStr,
  blanket_order: optionalStr,
  rfq_reference: optionalStr,
  quotation_history: optionalStr,
  procurement_schedule: optionalStr,
  lead_time_days: optionalStr,
  pricing_conditions: optionalStr,
})

const demandSalesSchema = z.object({
  sales_order_ref: optionalStr,
  short_term_forecast_qty: optionalStr,
  long_term_forecast_qty: optionalStr,
  historical_demand_notes: optionalStr,
  backlog_qty: optionalStr,
  delivery_schedule: optionalStr,
  promotion_adjustment_pct: optionalStr,
})

const productionSchema = z.object({
  mrp_run_ref: optionalStr,
  planned_order_qty: optionalStr,
  production_order_ref: optionalStr,
  schedule_start_date: optionalStr,
  schedule_end_date: optionalStr,
  wip_status: optionalStr,
  wip_qty: optionalStr,
  routing_id: optionalStr,
  work_center: optionalStr,
})

const logisticsSchema = z.object({
  ship_schedule: optionalStr,
  carrier: optionalStr,
  freight_forwarder: optionalStr,
  route: optionalStr,
  transport_mode: optionalStr,
  freight_cost: optionalStr,
  tracking_number: optionalStr,
  shipment_status: optionalStr,
  incoterms: optionalStr,
  customs_doc_ref: optionalStr,
})

const warehouseSchema = z.object({
  putaway_strategy: optionalStr,
  picking_strategy: optionalStr,
  packing_strategy: optionalStr,
  layout_zone: optionalStr,
  handling_unit: optionalStr,
  packaging_type: optionalStr,
  cycle_count_date: optionalStr,
  physical_variance_qty: optionalStr,
})

const financialSchema = z.object({
  purchase_price: optionalStr,
  landed_cost: optionalStr,
  transfer_price: optionalStr,
  freight_logistics_cost: optionalStr,
  ap_reference: optionalStr,
  ar_reference: optionalStr,
  budget_reference: optionalStr,
  cost_center: optionalStr,
})

const complianceSchema = z.object({
  country_of_origin: optionalStr,
  certifications: optionalStr,
  inspection_result: optionalStr,
  coa_reference: optionalStr,
  esg_notes: optionalStr,
  supplier_risk_score: optionalStr,
  disruption_alert: optionalStr,
})

const analyticsSchema = z.object({
  on_time_delivery_pct: optionalStr,
  fill_rate_pct: optionalStr,
  inventory_turnover: optionalStr,
  order_cycle_time_days: optionalStr,
  supplier_performance_score: optionalStr,
  dashboard_alert: optionalStr,
  exception_type: optionalStr,
  exception_notes: optionalStr,
})

export const scmLineItemSchema = z.object({
  item_code: optionalStr,
  description: optionalStr,
  quantity: optionalStr,
  uom: optionalStr,
  notes: optionalStr,
})

export const scmFormSchema = z.object({
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
  master_data: masterDataSchema,
  inventory: inventorySchema,
  procurement: procurementSchema,
  demand_sales: demandSalesSchema,
  production: productionSchema,
  logistics: logisticsSchema,
  warehouse: warehouseSchema,
  financial: financialSchema,
  compliance: complianceSchema,
  analytics: analyticsSchema,
  line_items: z.array(scmLineItemSchema),
})

export type ScmFormValues = z.infer<typeof scmFormSchema>
export type ScmLineItem = z.infer<typeof scmLineItemSchema>

export const SCM_CATEGORY_KEYS = [
  "master_data",
  "inventory",
  "procurement",
  "demand_sales",
  "production",
  "logistics",
  "warehouse",
  "financial",
  "compliance",
  "analytics",
] as const

function emptyMasterData(): ScmFormValues["master_data"] {
  return {
    item_sku: "",
    item_name: "",
    item_type: "",
    primary_uom: "",
    gross_weight: "",
    net_weight: "",
    dimensions: "",
    shelf_life_days: "",
    bom_version: "",
    bom_parent_sku: "",
    supplier_code: "",
    supplier_lead_time_days: "",
    approved_vendor: "",
    customer_code: "",
    ship_to_address: "",
    credit_terms: "",
    service_level_agreement: "",
    warehouse_code: "",
    bin_location: "",
    geo_region: "",
  }
}

function emptyInventory(): ScmFormValues["inventory"] {
  return {
    on_hand: "",
    available: "",
    reserved: "",
    in_transit: "",
    valuation_method: "",
    lot_number: "",
    serial_number: "",
    safety_stock: "",
    reorder_point: "",
    min_stock: "",
    max_stock: "",
    abc_class: "",
    aging_bucket: "",
    last_movement_date: "",
  }
}

function emptyProcurement(): ScmFormValues["procurement"] {
  return {
    pr_reference: "",
    po_reference: "",
    contract_reference: "",
    blanket_order: "",
    rfq_reference: "",
    quotation_history: "",
    procurement_schedule: "",
    lead_time_days: "",
    pricing_conditions: "",
  }
}

function emptyDemandSales(): ScmFormValues["demand_sales"] {
  return {
    sales_order_ref: "",
    short_term_forecast_qty: "",
    long_term_forecast_qty: "",
    historical_demand_notes: "",
    backlog_qty: "",
    delivery_schedule: "",
    promotion_adjustment_pct: "",
  }
}

function emptyProduction(): ScmFormValues["production"] {
  return {
    mrp_run_ref: "",
    planned_order_qty: "",
    production_order_ref: "",
    schedule_start_date: "",
    schedule_end_date: "",
    wip_status: "",
    wip_qty: "",
    routing_id: "",
    work_center: "",
  }
}

function emptyLogistics(): ScmFormValues["logistics"] {
  return {
    ship_schedule: "",
    carrier: "",
    freight_forwarder: "",
    route: "",
    transport_mode: "",
    freight_cost: "",
    tracking_number: "",
    shipment_status: "",
    incoterms: "",
    customs_doc_ref: "",
  }
}

function emptyWarehouse(): ScmFormValues["warehouse"] {
  return {
    putaway_strategy: "",
    picking_strategy: "",
    packing_strategy: "",
    layout_zone: "",
    handling_unit: "",
    packaging_type: "",
    cycle_count_date: "",
    physical_variance_qty: "",
  }
}

function emptyFinancial(): ScmFormValues["financial"] {
  return {
    purchase_price: "",
    landed_cost: "",
    transfer_price: "",
    freight_logistics_cost: "",
    ap_reference: "",
    ar_reference: "",
    budget_reference: "",
    cost_center: "",
  }
}

function emptyCompliance(): ScmFormValues["compliance"] {
  return {
    country_of_origin: "",
    certifications: "",
    inspection_result: "",
    coa_reference: "",
    esg_notes: "",
    supplier_risk_score: "",
    disruption_alert: "",
  }
}

function emptyAnalytics(): ScmFormValues["analytics"] {
  return {
    on_time_delivery_pct: "",
    fill_rate_pct: "",
    inventory_turnover: "",
    order_cycle_time_days: "",
    supplier_performance_score: "",
    dashboard_alert: "",
    exception_type: "",
    exception_notes: "",
  }
}

export const emptyScmLineItem = (): ScmLineItem => ({
  item_code: "",
  description: "",
  quantity: "",
  uom: "",
  notes: "",
})

export const defaultScmFormValues: ScmFormValues = {
  feature_code: "demand_planning",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  party_name: "",
  amount: "",
  quantity: "",
  start_date: "",
  end_date: "",
  master_data: emptyMasterData(),
  inventory: emptyInventory(),
  procurement: emptyProcurement(),
  demand_sales: emptyDemandSales(),
  production: emptyProduction(),
  logistics: emptyLogistics(),
  warehouse: emptyWarehouse(),
  financial: emptyFinancial(),
  compliance: emptyCompliance(),
  analytics: emptyAnalytics(),
  line_items: [],
}

function strField(value: unknown): string {
  return typeof value === "string" ? value : value != null ? String(value) : ""
}

function categoryFromExtra<T extends Record<string, string>>(
  extra: Record<string, unknown> | undefined,
  key: string,
  defaults: T,
): T {
  const raw = extra?.[key]
  if (!raw || typeof raw !== "object") return { ...defaults }
  const out = { ...defaults }
  for (const k of Object.keys(defaults) as (keyof T)[]) {
    out[k] = strField((raw as Record<string, unknown>)[k as string]) as T[keyof T]
  }
  return out
}

function lineItemsFromExtra(extra: Record<string, unknown> | undefined): ScmLineItem[] {
  const raw = extra?.line_items
  if (!Array.isArray(raw)) return []
  return raw.map((row) => {
    if (!row || typeof row !== "object") return emptyScmLineItem()
    const r = row as Record<string, unknown>
    return {
      item_code: strField(r.item_code),
      description: strField(r.description),
      quantity: strField(r.quantity),
      uom: strField(r.uom),
      notes: strField(r.notes),
    }
  })
}

export function recordToForm(record: ModuleRecord): ScmFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, unknown>
  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    party_name: record.party_name ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    quantity: record.quantity != null ? String(record.quantity) : "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    master_data: categoryFromExtra(extra, "master_data", emptyMasterData()),
    inventory: categoryFromExtra(extra, "inventory", emptyInventory()),
    procurement: categoryFromExtra(extra, "procurement", emptyProcurement()),
    demand_sales: categoryFromExtra(extra, "demand_sales", emptyDemandSales()),
    production: categoryFromExtra(extra, "production", emptyProduction()),
    logistics: categoryFromExtra(extra, "logistics", emptyLogistics()),
    warehouse: categoryFromExtra(extra, "warehouse", emptyWarehouse()),
    financial: categoryFromExtra(extra, "financial", emptyFinancial()),
    compliance: categoryFromExtra(extra, "compliance", emptyCompliance()),
    analytics: categoryFromExtra(extra, "analytics", emptyAnalytics()),
    line_items: lineItemsFromExtra(extra),
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function buildExtraData(values: ScmFormValues): Record<string, unknown> {
  return {
    master_data: values.master_data,
    inventory: values.inventory,
    procurement: values.procurement,
    demand_sales: values.demand_sales,
    production: values.production,
    logistics: values.logistics,
    warehouse: values.warehouse,
    financial: values.financial,
    compliance: values.compliance,
    analytics: values.analytics,
    line_items: values.line_items,
  }
}

function deriveTopLevel(values: ScmFormValues) {
  let party = values.party_name.trim()
  let amount = parseOptionalNumber(values.amount)
  let startDate = values.start_date.trim() || null
  let endDate = values.end_date.trim() || null

  const md = values.master_data
  const ds = values.demand_sales
  const lg = values.logistics

  if (!party) {
    party =
      md.supplier_code.trim() ||
      md.customer_code.trim() ||
      lg.carrier.trim() ||
      ""
  }
  if (amount == null) {
    amount = parseOptionalNumber(values.financial.landed_cost)
  }
  if (!startDate) {
    startDate = values.production.schedule_start_date.trim() || ds.delivery_schedule.trim() || null
  }
  if (!endDate) {
    endDate = values.production.schedule_end_date.trim() || null
  }

  return {
    party_name: party || null,
    amount,
    quantity: parseOptionalNumber(values.quantity),
    start_date: startDate,
    end_date: endDate,
  }
}

export function formToCreatePayload(values: ScmFormValues) {
  const top = deriveTopLevel(values)
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
    extra_data: buildExtraData(values),
  }
}

export function formToUpdatePayload(values: ScmFormValues) {
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
    extra_data: buildExtraData(values),
  }
}

export function newScmReference(featureCode: string): string {
  const prefix =
    featureCode === "forecasting"
      ? "FCST"
      : featureCode === "logistics"
        ? "LOG"
        : featureCode === "transportation"
          ? "TRN"
          : featureCode === "supplier_relationship"
            ? "SRM"
            : "SCM"
  return `${prefix}-${Date.now().toString(36).toUpperCase()}`
}

export function keyLabelFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data as Record<string, unknown> | undefined
  const md = (extra?.master_data ?? {}) as Record<string, unknown>
  const lg = (extra?.logistics ?? {}) as Record<string, unknown>
  const sku = strField(md.item_sku)
  const tracking = strField(lg.tracking_number)
  if (sku) return sku
  if (tracking) return tracking
  return strField(md.supplier_code) || "—"
}

export function scmLineFields() {
  return scmLineItemFields
}

/** Fraction of identity + category fields with any non-empty value (0–100). */
export function scmFormCompletionPercent(values: ScmFormValues): number {
  const checks: string[] = [
    values.reference,
    values.title,
    values.party_name,
    values.master_data.item_sku,
    values.inventory.on_hand,
    values.demand_sales.sales_order_ref,
    values.logistics.tracking_number,
    values.analytics.exception_type,
  ]
  const filled = checks.filter((v) => v.trim().length > 0).length
  return Math.round((filled / checks.length) * 100)
}
