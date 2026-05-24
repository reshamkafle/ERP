export type ManagerPeriod = "today" | "week" | "month"

export interface ManagerOverviewChartPoint {
  label: string
  revenue: string
  purchase_spend: string
}

export interface ExceptionAlertRow {
  severity: string
  category: string
  message: string
}

export interface ManagerOverview {
  period: ManagerPeriod
  total_revenue: string
  total_purchase_spend: string
  inventory_value: string
  low_stock_count: number
  open_po_count: number
  chart: ManagerOverviewChartPoint[]
  alerts: ExceptionAlertRow[]
}
