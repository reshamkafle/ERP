import { api } from "@/lib/api"
import type {
  FinancePeriod,
  FinanceSummaryReport,
  InventoryPerformanceReport,
  ItOverviewReport,
  MarketingFunnelReport,
  PurchaseOrdersReport,
  ReportPeriod,
  SalesReport,
  StockValueReport,
  TopProductsReport,
} from "@/types/report"

export async function fetchSalesReport(period: ReportPeriod): Promise<SalesReport> {
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

export async function fetchPurchaseOrdersReport(period: ReportPeriod): Promise<PurchaseOrdersReport> {
  const { data } = await api.get<PurchaseOrdersReport>("/v1/reports/purchase-orders", {
    params: { period },
  })
  return data
}

export async function fetchInventoryPerformanceReport(): Promise<InventoryPerformanceReport> {
  const { data } = await api.get<InventoryPerformanceReport>("/v1/reports/inventory-performance")
  return data
}

export async function fetchFinanceSummaryReport(period: FinancePeriod): Promise<FinanceSummaryReport> {
  const { data } = await api.get<FinanceSummaryReport>("/v1/reports/finance-summary", {
    params: { period },
  })
  return data
}

export async function fetchMarketingFunnelReport(): Promise<MarketingFunnelReport> {
  const { data } = await api.get<MarketingFunnelReport>("/v1/reports/marketing-funnel")
  return data
}

export async function fetchItOverviewReport(): Promise<ItOverviewReport> {
  const { data } = await api.get<ItOverviewReport>("/v1/reports/it-overview")
  return data
}
