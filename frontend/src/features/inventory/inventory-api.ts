import { api } from "@/lib/api"
import type { Category, InventoryItem, InventoryListResponse } from "@/types/inventory"
import type { InventoryFormValues } from "@/lib/inventory-schema"

function buildPayload(values: InventoryFormValues, includeInitialStock: boolean) {
  const payload: Record<string, unknown> = {
    sku: values.sku,
    name: values.name,
    description: values.description || null,
    barcode: values.barcode || null,
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
    expiry_date_flag: values.expiry_date_flag,
    primary_uom: values.primary_uom,
    secondary_uom: values.secondary_uom || null,
    conversion_factor: values.conversion_factor || null,
    length: values.length || null,
    width: values.width || null,
    height: values.height || null,
    volume: values.volume || null,
    gross_weight: values.gross_weight || null,
    net_weight: values.net_weight || null,
    lifecycle_status: values.lifecycle_status,
    approval_status: values.approval_status,
    tax_code: values.tax_code || null,
    hs_code: values.hs_code || null,
    country_of_origin: values.country_of_origin || null,
    hazardous_flag: values.hazardous_flag,
    perishable_flag: values.perishable_flag,
    price: values.price,
    cost_price: values.cost_price,
    low_stock_threshold: values.low_stock_threshold,
    default_supplier_id: values.default_supplier_id,
    promotion_reorder_boost: values.promotion_reorder_boost,
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
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<InventoryListResponse>("/v1/inventory", { params })
  return data
}

export async function fetchCategories() {
  const { data } = await api.get<Category[]>("/v1/inventory/categories")
  return data
}

export async function createInventoryItem(values: InventoryFormValues) {
  const { data } = await api.post<InventoryItem>(
    "/v1/inventory",
    buildPayload(values, true),
  )
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
