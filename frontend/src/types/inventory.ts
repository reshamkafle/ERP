export type ItemType = "RAW" | "FINISHED" | "TRADING" | "SERVICE" | "ASSET"
export type ItemLifecycleStatus = "ACTIVE" | "INACTIVE" | "DISCONTINUED" | "OBSOLETE"
export type ApprovalStatus = "DRAFT" | "PENDING" | "APPROVED" | "REJECTED"

export type Category = {
  id: number
  name: string
}

export type InventoryItem = {
  id: number
  sku: string
  name: string
  description: string | null
  barcode: string | null
  alternate_codes: string | null
  category_id: number | null
  category: Category | null
  sub_category: string | null
  product_line: string | null
  item_type: ItemType
  size: string | null
  color: string | null
  model: string | null
  variant: string | null
  serial_number_flag: boolean
  batch_lot_flag: boolean
  expiry_date_flag: boolean
  primary_uom: string
  secondary_uom: string | null
  conversion_factor: string | null
  length: string | null
  width: string | null
  height: string | null
  volume: string | null
  gross_weight: string | null
  net_weight: string | null
  lifecycle_status: ItemLifecycleStatus
  approval_status: ApprovalStatus
  tax_code: string | null
  hs_code: string | null
  country_of_origin: string | null
  hazardous_flag: boolean
  perishable_flag: boolean
  price: string
  cost_price: string
  stock: number
  low_stock_threshold: number
  default_supplier_id: number | null
  default_supplier: { id: number; name: string } | null
  promotion_reorder_boost: boolean
}

export type InventoryListResponse = {
  items: InventoryItem[]
  total: number
}

export type InventoryItemInput = {
  sku: string
  name: string
  description?: string
  barcode?: string
  alternate_codes?: string
  category_id?: number | null
  sub_category?: string
  product_line?: string
  item_type: ItemType
  size?: string
  color?: string
  model?: string
  variant?: string
  serial_number_flag: boolean
  batch_lot_flag: boolean
  expiry_date_flag: boolean
  primary_uom: string
  secondary_uom?: string
  conversion_factor?: string
  length?: string
  width?: string
  height?: string
  volume?: string
  gross_weight?: string
  net_weight?: string
  lifecycle_status: ItemLifecycleStatus
  approval_status: ApprovalStatus
  tax_code?: string
  hs_code?: string
  country_of_origin?: string
  hazardous_flag: boolean
  perishable_flag: boolean
  price: string
  cost_price: string
  low_stock_threshold: number
  default_supplier_id?: number | null
  promotion_reorder_boost: boolean
  initial_stock?: number
}
