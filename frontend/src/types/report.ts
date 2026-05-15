export type SalesPeriod = "today" | "week"

export interface SalesChartPoint {
  label: string
  revenue: string
  sale_count: number
}

export interface SaleSummaryRow {
  id: number
  created_at: string
  item_count: number
  total: string
}

export interface SalesReport {
  period: SalesPeriod
  total_revenue: string
  sale_count: number
  chart: SalesChartPoint[]
  sales: SaleSummaryRow[]
}

export interface TopProductRow {
  product_id: number
  sku: string
  name: string
  quantity_sold: number
  revenue: string
}

export interface TopProductsReport {
  products: TopProductRow[]
}

export interface StockValueRow {
  product_id: number
  sku: string
  name: string
  stock: number
  cost_price: string
  line_value: string
}

export interface StockValueReport {
  total_value: string
  product_count: number
  items: StockValueRow[]
}
