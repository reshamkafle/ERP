export type Customer = {
  id: number
  name: string
  phone: string | null
  email: string | null
  notes: string | null
}

export type CustomerListResponse = {
  items: Customer[]
  total: number
}

export type CustomerSaleSummary = {
  id: number
  created_at: string
  item_count: number
  total: string
}

export type CustomerDetail = Customer & {
  recent_sales: CustomerSaleSummary[]
}
