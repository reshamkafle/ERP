export type PurchaseProduct = {
  id: number
  sku: string
  name: string
  barcode: string | null
  cost_price: string
  stock: number
}

export type PurchaseProductListResponse = {
  items: PurchaseProduct[]
  total: number
}

export type PurchaseLineDraft = {
  product_id: number
  sku: string
  name: string
  quantity: number
  unit_cost: string
}

export type PurchaseListItem = {
  id: number
  supplier_id: number
  supplier_name: string
  created_at: string
  item_count: number
  total: string
  status: string
  procurement_run_id: number | null
  agent_summary: string | null
}

export type PurchaseListResponse = {
  items: PurchaseListItem[]
  total: number
}

export type PurchaseItemRead = {
  id: number
  product_id: number
  product_name: string
  product_sku: string
  quantity: number
  unit_cost: string
  line_total: string
}

export type PurchaseRead = {
  id: number
  supplier_id: number
  supplier_name: string
  created_at: string
  status: string
  procurement_run_id: number | null
  agent_summary: string | null
  items: PurchaseItemRead[]
  total: string
}

export type ProcurementRunResponse = {
  id: number
  status: string
  draft_purchase_ids: number[]
  warnings: string[]
  error_message: string | null
}
