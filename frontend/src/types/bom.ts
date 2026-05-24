export type ItemCategory =
  | "FABRIC"
  | "TRIM"
  | "ACCESSORY"
  | "SUB_ASSEMBLY"
  | "FINISHED_GOOD"

export type ConsumptionType = "FABRIC" | "TRIM" | "OTHER"

export type UnitOfMeasure = "meter" | "kg" | "piece" | "yard" | "gram" | "set" | "ea"

export type BOMStatus = "DRAFT" | "ACTIVE" | "OBSOLETE" | "SUPERSEDED"

export type BOMType =
  | "MANUFACTURING"
  | "ENGINEERING"
  | "SALES"
  | "SERVICE"
  | "PHANTOM"

export interface ManufacturingItem {
  id: number
  sku: string
  name: string
  category: ItemCategory
  unit: UnitOfMeasure
  cost_per_unit: string
}

export interface ProductSnapshot {
  product_id: number
  sku: string
  name: string
  description: string | null
  primary_uom: string
  standard_cost: string | null
  cost_price: string
  item_type: string
  default_supplier_id: number | null
  default_supplier_name: string | null
  country_of_origin: string | null
  hs_code: string | null
  gross_weight: string | null
  length: string | null
  width: string | null
  height: string | null
  volume: string | null
  batch_lot_flag: boolean
  serial_number_flag: boolean
  shelf_life_days: number | null
  lead_time_days: number | null
}

export interface BOMSubstituteRead {
  id: number
  substitute_item_id: number
  substitute_sku: string
  substitute_name: string
  substitute_quantity: string
  priority: number
  notes: string | null
}

export interface BOMAlternateRead {
  id: number
  alternate_parent_item_id: number
  alternate_parent_sku: string
  alternate_parent_name: string
  alternate_group: string
  priority: number
  notes: string | null
}

export interface BOMAlternateCreate {
  alternate_parent_sku: string
  alternate_group: string
  priority: number
  notes: string | null
}

export interface BOMSubstituteCreate {
  substitute_sku: string
  substitute_quantity: string
  priority: number
  notes: string | null
}

export interface BOMLineRead {
  line_id: number | null
  line_sequence: number
  component_sku: string
  component_name: string
  component_category: ItemCategory
  quantity_per_unit: string
  consumption_type: ConsumptionType
  wastage_percentage: string
  yield_percentage: string
  is_phantom: boolean
  lead_time_offset_days: number | null
  notes: string | null
  product_snapshot: ProductSnapshot | null
  substitutes: BOMSubstituteRead[]
}

export interface BOMSummary {
  parent_sku: string
  parent_name: string
  bom_number: string
  version: number
  status: BOMStatus
  bom_type: BOMType
  line_count: number
  effective_start_date: string | null
  updated_at: string | null
}

export interface BOMRead {
  parent_item_id: number | null
  parent_sku: string
  parent_name: string
  parent_description: string | null
  bom_number: string
  version: number
  status: BOMStatus
  bom_type: BOMType
  effective_start_date: string | null
  effective_end_date: string | null
  eco_number: string | null
  approved_at: string | null
  approved_by_id: number | null
  created_by_id: number | null
  created_at: string | null
  updated_by_id: number | null
  updated_at: string | null
  parent_product_snapshot: ProductSnapshot | null
  lines: BOMLineRead[]
  alternates: BOMAlternateRead[]
}

export interface BOMLineInput {
  component_sku: string
  line_sequence?: number
  quantity_per_unit: string
  consumption_type: ConsumptionType
  wastage_percentage: string
  yield_percentage: string
  is_phantom: boolean
  lead_time_offset_days: number | null
  notes: string | null
}

export interface BOMHeaderInput {
  status: BOMStatus
  bom_type: BOMType
  effective_start_date: string | null
  effective_end_date: string | null
  eco_number: string | null
}

export interface SaveBOMRequest {
  header?: BOMHeaderInput
  lines: BOMLineInput[]
}

export interface ValidationResult {
  is_valid: boolean
  errors: string[]
  warnings: string[]
}

export interface SaveBOMResponse {
  bom: BOMRead
  validation: ValidationResult
}

export interface BOMTreeNode {
  item: ManufacturingItem
  line_sequence: number
  quantity_per_unit: string
  consumption_type: ConsumptionType
  wastage_percentage: string
  yield_percentage: string
  is_phantom: boolean
  lead_time_offset_days: number | null
  notes: string | null
  children: BOMTreeNode[]
  rolled_up_cost: string | null
}

export interface BOMTree {
  root: BOMTreeNode
  parent_sku: string
}

export interface ExplosionLine {
  item_id: number
  sku: string
  name: string
  category: ItemCategory
  consumption_type: ConsumptionType
  unit: UnitOfMeasure
  gross_qty: string
  wastage_qty: string
  total_qty: string
  cost_per_unit: string
  extended_cost: string
}

export interface ExplosionResult {
  parent_sku: string
  parent_item_id: number
  order_quantity: number
  lines: ExplosionLine[]
  total_material_cost: string
}

export interface FabricLine {
  sku: string
  name: string
  unit: UnitOfMeasure
  gross_qty: string
  wastage_qty: string
  total_qty: string
  wastage_percentage: string
  extended_cost: string
}

export interface FabricSummary {
  parent_sku: string
  order_quantity: number
  fabrics: FabricLine[]
  total_meters: string
  total_fabric_cost: string
}

export interface TrimLine {
  sku: string
  name: string
  unit: UnitOfMeasure
  gross_qty: string
  wastage_qty: string
  total_qty: string
  extended_cost: string
}

export interface TrimSummary {
  parent_sku: string
  order_quantity: number
  trims: TrimLine[]
  total_trim_cost: string
}
