import type { ItemLifecycleStatus, ItemType } from "@/types/inventory"

export type AttributeValue = {
  id: number
  attribute_id: number
  code: string
  label: string
  sort_order: number
  is_active: boolean
}

export type ProductAttribute = {
  id: number
  code: string
  name: string
  sort_order: number
  is_active: boolean
  values: AttributeValue[]
}

export type ProductTemplate = {
  id: number
  style_code: string
  name: string
  description: string | null
  sku_prefix: string
  category_id: number | null
  item_type: ItemType
  product_line: string | null
  primary_uom: string
  default_price: string
  default_cost_price: string
  image_url: string | null
  manufacturing_item_sku: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  variant_count: number
  total_stock: number
}

export type ProductTemplateListResponse = {
  items: ProductTemplate[]
  total: number
}

export type VariantBrief = {
  id: number
  sku: string
  name: string
  color: string | null
  size: string | null
  color_value_id: number | null
  size_value_id: number | null
  stock: number
  lifecycle_status: ItemLifecycleStatus
  price: string
}

export type TemplateVariantsResponse = {
  template: ProductTemplate
  variants: VariantBrief[]
}

export type MatrixGenerateRequest = {
  color_value_ids: number[]
  size_value_ids: number[]
  skip_existing?: boolean
  initial_stock?: number
  lifecycle_status?: ItemLifecycleStatus
}

export type MatrixGenerateResult = {
  created: VariantBrief[]
  skipped: string[]
  errors: string[]
}
