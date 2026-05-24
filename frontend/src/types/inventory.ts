export type ItemType =
  | "RAW"
  | "FINISHED"
  | "SEMI_FINISHED"
  | "CONSUMABLE"
  | "TRADING"
  | "SERVICE"
  | "ASSET"
export type ItemLifecycleStatus = "ACTIVE" | "INACTIVE" | "DISCONTINUED" | "OBSOLETE"
export type ApprovalStatus = "DRAFT" | "PENDING" | "APPROVED" | "REJECTED"
export type AbcClass = "A" | "B" | "C"
export type XyzClass = "FAST" | "SLOW" | "NON_MOVING"
export type CostValuationMethod =
  | "STANDARD"
  | "AVERAGE"
  | "LAST_PURCHASE"
  | "FIFO"
  | "LIFO"

export type Category = {
  id: number
  name: string
}

export type ProductSupplierLink = {
  id: number
  supplier_id: number
  vendor_code: string | null
  is_preferred: boolean
  supplier_name: string | null
}

export type TaxRateBrief = {
  id: number
  code: string
  name: string
  rate_percent: string
}

export type WarehouseBrief = {
  id: number
  code: string
  name: string
}

export type StorageLocationBrief = {
  id: number
  code: string
  warehouse_id: number
}

export type StockBalance = {
  id: number
  warehouse_id: number
  warehouse_code: string | null
  warehouse_name: string | null
  location_id: number | null
  location_code: string | null
  on_hand: number
  available: number
  reserved: number
  in_transit: number
  quality_status: string
  valuation_method: CostValuationMethod | null
  last_transaction_at: string | null
  expiry_date: string | null
  lot_number: string | null
}

export type InventoryTransaction = {
  id: number
  transaction_type: string
  transaction_at: string
  reference_document: string | null
  quantity: number
  unit_cost: string | null
  reason_code: string | null
  user_email: string | null
  remarks: string | null
}

export type InventoryAnalytics = {
  turnover_ratio: string
  inventory_accuracy_pct: string
  stock_value: string
  dead_stock_value: string
  inventory_holding_cost: string
}

export type InventorySalesDailyPoint = {
  date: string
  quantity_sold: number
  revenue: string
}

export type InventorySalesInsight = {
  lookback_days: number
  quantity_sold: number
  revenue: string
  top_buyer_name: string | null
  top_seller_name: string | null
  daily_chart: InventorySalesDailyPoint[]
}

export type InventoryItem = {
  id: number
  sku: string
  name: string
  description: string | null
  barcode: string | null
  qr_code: string | null
  rfid_tag: string | null
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
  template_id: number | null
  style_code: string | null
  color_value_id: number | null
  size_value_id: number | null
  template: { id: number; style_code: string; name: string } | null
  serial_number_flag: boolean
  batch_lot_flag: boolean
  roll_tracking_enabled: boolean
  batch_management_enabled: boolean
  expiry_date_flag: boolean
  shelf_life_days: number | null
  primary_uom: string
  secondary_uom: string | null
  purchase_uom: string | null
  sales_uom: string | null
  conversion_factor: string | null
  length: string | null
  width: string | null
  height: string | null
  volume: string | null
  gross_weight: string | null
  net_weight: string | null
  abc_class: AbcClass | null
  xyz_class: XyzClass | null
  lifecycle_status: ItemLifecycleStatus
  approval_status: ApprovalStatus
  tax_code: string | null
  tax_rate_id: number | null
  tax_rate: TaxRateBrief | null
  hs_code: string | null
  country_of_origin: string | null
  hazardous_flag: boolean
  perishable_flag: boolean
  hazardous_material_class: string | null
  regulatory_compliance_codes: string | null
  price: string
  cost_price: string
  standard_cost: string | null
  cost_valuation_method: CostValuationMethod | null
  stock: number
  low_stock_threshold: number
  reorder_level: number
  max_stock_level: number | null
  economic_order_qty: number | null
  lead_time_days: number | null
  default_supplier_id: number | null
  default_supplier: { id: number; name: string } | null
  default_warehouse_id: number | null
  default_warehouse: WarehouseBrief | null
  default_location_id: number | null
  default_location: StorageLocationBrief | null
  promotion_reorder_boost: boolean
  reorder_point: number
  safety_stock_level: number
  min_order_qty: number | null
  max_order_qty: number | null
  procurement_lead_time_days: number | null
  demand_forecast_notes: string | null
  quality_inspection_required: boolean
  inspection_checklist: Record<string, unknown> | null
  expiry_alert_threshold_days: number | null
  image_url: string | null
  attachments: { name: string; url: string; type?: string }[] | null
  created_at: string
  updated_at: string
  created_by: { id: number; email: string } | null
  updated_by: { id: number; email: string } | null
  product_supplier_links: ProductSupplierLink[]
  manufacturing_item_sku: string | null
  bom_parent_count: number
  has_bom_shortage: boolean
  sales_insight?: InventorySalesInsight | null
  stock_balances?: StockBalance[]
  analytics?: InventoryAnalytics | null
}

export type InventoryBomUsage = {
  parent_sku: string
  parent_name: string
  parent_category: string
  required_qty: string
  on_hand_stock: number
  is_short: boolean
}

export type InventoryBomUsageListResponse = {
  usages: InventoryBomUsage[]
}

export type InventoryListResponse = {
  items: InventoryItem[]
  total: number
}

export type InventoryTransactionListResponse = {
  items: InventoryTransaction[]
  total: number
}

export type Warehouse = {
  id: number
  code: string
  name: string
  warehouse_type: string
  address: string | null
  capacity_weight: string | null
  capacity_volume: string | null
  capacity_pallets: number | null
  status: string
  is_default: boolean
  wave_picking_enabled: boolean
  cross_docking_enabled: boolean
  cycle_count_frequency: string | null
  cycle_count_class: string | null
  packing_rules: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export type WarehouseListResponse = {
  items: Warehouse[]
  total: number
}

export type StorageLocation = {
  id: number
  code: string
  warehouse_id: number
  aisle: string | null
  row: string | null
  column: string | null
  level: string | null
  location_type: string
  capacity: string | null
  putaway_strategy: string | null
  picking_strategy: string | null
  status: string
  zone: string | null
  created_at: string
  updated_at: string
}

export type StorageLocationListResponse = {
  items: StorageLocation[]
  total: number
}
