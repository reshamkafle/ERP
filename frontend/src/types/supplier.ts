export type Supplier = {
  id: number
  name: string
  phone: string | null
  email: string | null
  notes: string | null
}

export type SupplierListItem = Supplier & {
  total_spent: string
  purchase_count: number
}

export type SupplierListResponse = {
  items: SupplierListItem[]
  total: number
}

export type SupplierPurchaseSummary = {
  id: number
  created_at: string
  item_count: number
  total: string
}

export type SupplierDetail = Supplier & {
  total_spent: string
  purchase_count: number
  recent_purchases: SupplierPurchaseSummary[]
}
