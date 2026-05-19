export type PromotionRunCreateBody = {
  sales_lookback_days?: number
  max_anchor_products?: number
  max_related_per_anchor?: number
  max_projects?: number
  category_id?: number | null
  co_purchase_pair_limit?: number
}

export type PromotionRunResponse = {
  id: number
  status: string
  warnings: string[]
  error_message: string | null
}

export type PromotionProposalsPayload = {
  merge_notes?: string
  fallback_used?: boolean
  signals_warnings?: string[]
  projects: PromotionProject[]
}

export type PromotionProject = {
  project_id: string
  anchor: Record<string, unknown>
  related_items: PromotionRelatedLine[]
  discount_kind?: string
  discount_percent?: number | null
  discount_amount?: string | null
  duration_days?: number
  start_date?: string | null
  end_date?: string | null
  rationale?: string
  confidence?: string
}

export type PromotionRelatedLine = {
  product_id: number
  sku?: string
  name?: string
  discount_kind?: string
  discount_percent?: number | null
  discount_amount?: string | null
  duration_days?: number
  rationale?: string
  confidence?: string
}

export type PromotionRunDetail = {
  id: number
  status: string
  created_at: string
  proposals_json: PromotionProposalsPayload | null
  approved_json: { projects: PromotionProject[]; rejected?: boolean } | null
  error_message: string | null
}

export type PromotionConfirmBody = {
  projects: PromotionProject[]
  reject?: boolean
}
