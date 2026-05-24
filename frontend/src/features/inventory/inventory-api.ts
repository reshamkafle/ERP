import { api } from "@/lib/api"
import type { InventoryFormValues } from "@/lib/inventory-schema"
import type {
  Category,
  InventoryAnalytics,
  InventoryBomUsageListResponse,
  InventoryItem,
  InventoryListResponse,
  InventoryTransactionListResponse,
} from "@/types/inventory"

function optInt(v: number | "" | undefined): number | null {
  if (v === "" || v === undefined) return null
  return v
}

function optEnum<T extends string>(v: T | "" | undefined): T | null {
  if (!v) return null
  return v
}

function parseJsonField(raw: string | undefined): unknown {
  const t = raw?.trim()
  if (!t) return null
  try {
    return JSON.parse(t)
  } catch {
    return null
  }
}

export function buildPayload(values: InventoryFormValues, includeInitialStock: boolean) {
  const payload: Record<string, unknown> = {
    sku: values.sku,
    name: values.name,
    description: values.description || null,
    barcode: values.barcode || null,
    qr_code: values.qr_code || null,
    rfid_tag: values.rfid_tag || null,
    alternate_codes: values.alternate_codes || null,
    category_id: values.category_id,
    sub_category: values.sub_category || null,
    product_line: values.product_line || null,
    item_type: values.item_type,
    size: values.size || null,
    color: values.color || null,
    model: values.model || null,
    variant: values.variant || null,
    serial_number_flag: values.serial_number_flag,
    batch_lot_flag: values.batch_lot_flag,
    roll_tracking_enabled: values.roll_tracking_enabled,
    batch_management_enabled: values.batch_management_enabled,
    expiry_date_flag: values.expiry_date_flag,
    shelf_life_days: optInt(values.shelf_life_days),
    primary_uom: values.primary_uom,
    secondary_uom: values.secondary_uom || null,
    purchase_uom: values.purchase_uom || null,
    sales_uom: values.sales_uom || null,
    conversion_factor: values.conversion_factor || null,
    length: values.length || null,
    width: values.width || null,
    height: values.height || null,
    volume: values.volume || null,
    gross_weight: values.gross_weight || null,
    net_weight: values.net_weight || null,
    abc_class: optEnum(values.abc_class),
    xyz_class: optEnum(values.xyz_class),
    lifecycle_status: values.lifecycle_status,
    approval_status: values.approval_status,
    tax_code: values.tax_code || null,
    tax_rate_id: values.tax_rate_id,
    hs_code: values.hs_code || null,
    country_of_origin: values.country_of_origin || null,
    hazardous_flag: values.hazardous_flag,
    perishable_flag: values.perishable_flag,
    hazardous_material_class: values.hazardous_material_class || null,
    regulatory_compliance_codes: values.regulatory_compliance_codes || null,
    price: values.price,
    cost_price: values.cost_price,
    standard_cost: values.standard_cost || null,
    cost_valuation_method: optEnum(values.cost_valuation_method),
    low_stock_threshold: values.low_stock_threshold,
    reorder_level: values.reorder_level,
    max_stock_level: optInt(values.max_stock_level),
    economic_order_qty: optInt(values.economic_order_qty),
    lead_time_days: optInt(values.lead_time_days),
    default_supplier_id: values.default_supplier_id,
    default_warehouse_id: values.default_warehouse_id,
    default_location_id: values.default_location_id,
    promotion_reorder_boost: values.promotion_reorder_boost,
    reorder_point: values.reorder_point,
    safety_stock_level: values.safety_stock_level,
    min_order_qty: optInt(values.min_order_qty),
    max_order_qty: optInt(values.max_order_qty),
    procurement_lead_time_days: optInt(values.procurement_lead_time_days),
    demand_forecast_notes: values.demand_forecast_notes || null,
    quality_inspection_required: values.quality_inspection_required,
    inspection_checklist: parseJsonField(values.inspection_checklist_json),
    expiry_alert_threshold_days: optInt(values.expiry_alert_threshold_days),
    image_url: values.image_url || null,
    attachments: parseJsonField(values.attachments_json) as
      | { name: string; url: string; type?: string }[]
      | null,
    product_suppliers: values.product_suppliers,
    manufacturing_item_sku: values.manufacturing_item_sku?.trim() || null,
  }
  if (includeInitialStock) {
    payload.initial_stock = values.initial_stock ?? 0
  }
  return payload
}

export async function fetchInventory(params: {
  search?: string
  category_id?: number
  item_type?: string
  lifecycle_status?: string
  template_id?: number
  style_code?: string
  color?: string
  size?: string
  variants_only?: boolean
  skip?: number
  limit?: number
  include_sales_insight?: boolean
}) {
  const { data } = await api.get<InventoryListResponse>("/v1/inventory", { params })
  return data
}

export async function fetchInventoryItem(id: number) {
  const { data } = await api.get<InventoryItem>(`/v1/inventory/${id}`)
  return data
}

export async function fetchCategories() {
  const { data } = await api.get<Category[]>("/v1/inventory/categories")
  return data
}

export async function fetchTaxRates() {
  const { data } = await api.get<{ id: number; code: string; name: string }[]>(
    "/v1/inventory/tax-rates",
  )
  return data
}

export async function createInventoryItem(values: InventoryFormValues) {
  const { data } = await api.post<InventoryItem>("/v1/inventory", buildPayload(values, true))
  return data
}

export async function updateInventoryItem(id: number, values: InventoryFormValues) {
  const { data } = await api.patch<InventoryItem>(
    `/v1/inventory/${id}`,
    buildPayload(values, false),
  )
  return data
}

export async function deleteInventoryItem(id: number) {
  await api.delete(`/v1/inventory/${id}`)
}

export async function fetchInventoryBomUsages(itemId: number) {
  const { data } = await api.get<InventoryBomUsageListResponse>(
    `/v1/inventory/${itemId}/bom-usages`,
  )
  return data.usages
}

export async function fetchInventoryTransactions(itemId: number, skip = 0, limit = 50) {
  const { data } = await api.get<InventoryTransactionListResponse>(
    `/v1/inventory/${itemId}/transactions`,
    { params: { skip, limit } },
  )
  return data
}

export async function fetchInventoryAnalytics(itemId: number) {
  const { data } = await api.get<InventoryAnalytics>(`/v1/inventory/${itemId}/analytics`)
  return data
}
