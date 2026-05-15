import { api } from "@/lib/api"
import type { SalesPeriod, SalesReport, StockValueReport, TopProductsReport } from "@/types/report"

export async function fetchSalesReport(period: SalesPeriod): Promise<SalesReport> {
  const { data } = await api.get<SalesReport>("/v1/reports/sales", { params: { period } })
  return data
}

export async function fetchTopProductsReport(): Promise<TopProductsReport> {
  const { data } = await api.get<TopProductsReport>("/v1/reports/top-products")
  return data
}

export async function fetchStockValueReport(): Promise<StockValueReport> {
  const { data } = await api.get<StockValueReport>("/v1/reports/stock-value")
  return data
}
