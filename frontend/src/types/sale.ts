export type PosProduct = {
  id: number
  sku: string
  name: string
  barcode: string | null
  price: string
  stock: number
  low_stock_threshold: number
}

export type PosProductListResponse = {
  items: PosProduct[]
  total: number
}

export type SaleCheckoutItem = {
  product_id: number
  quantity: number
}

export type SaleCheckoutPayload = {
  customer_id?: number | null
  items: SaleCheckoutItem[]
}

export type SaleItem = {
  id: number
  product_id: number
  product_name: string
  product_sku: string
  quantity: number
  price_at_sale: string
  line_total: string
}

export type Sale = {
  id: number
  customer_id: number | null
  customer_name?: string | null
  cashier_email?: string | null
  created_at: string
  items: SaleItem[]
  subtotal: string
  tax: string
  total: string
}

export type SaleListItem = {
  id: number
  customer_id: number | null
  customer_name: string | null
  cashier_email: string | null
  created_at: string
  item_count: number
  total: string
}

export type SaleListResponse = {
  items: SaleListItem[]
  total: number
}
