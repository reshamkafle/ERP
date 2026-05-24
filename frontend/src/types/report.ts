export type ReportPeriod = "today" | "week" | "month"
export type FinancePeriod = "week" | "month"

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
  period: ReportPeriod
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

export interface PurchaseOrderChartPoint {
  label: string
  spend: string
  po_count: number
}

export interface PurchaseOrderSummaryRow {
  id: number
  created_at: string
  supplier_name: string | null
  status: string
  total: string
}

export interface PurchaseOrdersReport {
  period: ReportPeriod
  total_spend: string
  po_count: number
  open_po_count: number
  open_po_value: string
  chart: PurchaseOrderChartPoint[]
  purchases: PurchaseOrderSummaryRow[]
}

export interface LowStockRow {
  product_id: number
  sku: string
  name: string
  stock: number
  low_stock_threshold: number
  line_value: string
}

export interface DeadStockRow {
  product_id: number
  sku: string
  name: string
  stock: number
  line_value: string
}

export interface SellThroughRow {
  product_id: number
  sku: string
  name: string
  units_sold: number
  stock: number
  sell_through_pct: string
}

export interface InventoryPerformanceReport {
  low_stock_count: number
  dead_stock_value: string
  total_stock_value: string
  avg_turnover_ratio: string
  low_stock_items: LowStockRow[]
  dead_stock_items: DeadStockRow[]
  sell_through_items: SellThroughRow[]
  open_po_count: number
  open_po_items: PurchaseOrderSummaryRow[]
}

export interface CashFlowChartPoint {
  label: string
  inbound: string
  outbound: string
}

export interface OutstandingDocumentRow {
  id: number
  party_name: string
  total: string
  amount_paid: string
  outstanding: string
}

export interface VendorSpendRow {
  supplier_id: number | null
  supplier_name: string
  total_spend: string
  po_count: number
}

export interface FinanceSummaryReport {
  period: FinancePeriod
  payments_in: string
  payments_out: string
  ap_outstanding: string
  ar_outstanding: string
  revenue: string
  cogs_approx: string
  gross_margin_pct: string
  chart: CashFlowChartPoint[]
  ap_by_supplier: OutstandingDocumentRow[]
  po_spend_by_vendor: VendorSpendRow[]
}

export interface StatusCountRow {
  status: string
  count: number
}

export interface StageCountRow {
  stage: string
  count: number
  total_value: string
}

export interface CustomerGrowthPoint {
  label: string
  count: number
}

export interface MarketingFunnelReport {
  total_leads: number
  leads_by_status: StatusCountRow[]
  total_opportunities: number
  opportunities_by_stage: StageCountRow[]
  total_customers: number
  new_customers_30d: number
  customer_growth_chart: CustomerGrowthPoint[]
}

export interface RoleSummaryRow {
  role_name: string
  user_count: number
}

export interface AgentRunStatusRow {
  run_type: string
  status: string
  count: number
}

export interface ItOverviewReport {
  api_status: string
  db_status: string
  active_user_count: number
  role_count: number
  permission_count: number
  roles: RoleSummaryRow[]
  agent_runs: AgentRunStatusRow[]
}

export type ReportTabId =
  | "sales"
  | "top-products"
  | "purchase-orders"
  | "inventory-performance"
  | "stock-value"
  | "finance-summary"
  | "marketing-funnel"
  | "it-overview"
