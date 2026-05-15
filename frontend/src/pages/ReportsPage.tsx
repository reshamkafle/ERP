import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Navigate } from "react-router-dom"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import {
  fetchSalesReport,
  fetchStockValueReport,
  fetchTopProductsReport,
} from "@/features/reports/reports-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"
import type { SalesPeriod } from "@/types/report"

type ReportTab = "sales" | "top-products" | "stock-value"

const CHART_COLOR = "hsl(160 84% 39%)"

function toNumber(value: string | number): number {
  const n = typeof value === "number" ? value : Number.parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

function formatDateTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function ReportsPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState<ReportTab>("sales")
  const [salesPeriod, setSalesPeriod] = useState<SalesPeriod>("today")

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const salesQuery = useQuery({
    queryKey: ["reports", "sales", salesPeriod],
    queryFn: () => fetchSalesReport(salesPeriod),
    enabled: tab === "sales",
  })

  const topProductsQuery = useQuery({
    queryKey: ["reports", "top-products"],
    queryFn: fetchTopProductsReport,
    enabled: tab === "top-products",
  })

  const stockValueQuery = useQuery({
    queryKey: ["reports", "stock-value"],
    queryFn: fetchStockValueReport,
    enabled: tab === "stock-value",
  })

  const salesChartData =
    salesQuery.data?.chart.map((p) => ({
      label: p.label,
      revenue: toNumber(p.revenue),
      sale_count: p.sale_count,
    })) ?? []

  const topProductsChartData =
    topProductsQuery.data?.products.map((p) => ({
      name: p.name.length > 18 ? `${p.name.slice(0, 16)}…` : p.name,
      quantity: p.quantity_sold,
      revenue: toNumber(p.revenue),
    })) ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Reports</h1>
        <p className="text-sm text-muted-foreground">
          Sales performance, top sellers, and inventory value at cost.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={tab === "sales" ? "default" : "outline"}
          size="sm"
          onClick={() => setTab("sales")}
        >
          Sales
        </Button>
        <Button
          type="button"
          variant={tab === "top-products" ? "default" : "outline"}
          size="sm"
          onClick={() => setTab("top-products")}
        >
          Top products
        </Button>
        <Button
          type="button"
          variant={tab === "stock-value" ? "default" : "outline"}
          size="sm"
          onClick={() => setTab("stock-value")}
        >
          Stock value
        </Button>
      </div>

      {tab === "sales" ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant={salesPeriod === "today" ? "default" : "outline"}
              size="sm"
              onClick={() => setSalesPeriod("today")}
            >
              Today
            </Button>
            <Button
              type="button"
              variant={salesPeriod === "week" ? "default" : "outline"}
              size="sm"
              onClick={() => setSalesPeriod("week")}
            >
              This week
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Total revenue
              </p>
              <p className="mt-2 text-3xl font-semibold text-foreground">
                {salesQuery.isLoading
                  ? "…"
                  : formatMoney(salesQuery.data?.total_revenue ?? 0)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Sales count
              </p>
              <p className="mt-2 text-3xl font-semibold text-foreground">
                {salesQuery.isLoading ? "…" : (salesQuery.data?.sale_count ?? 0)}
              </p>
            </Card>
          </div>

          <Card className="p-4">
            <p className="mb-4 text-sm font-medium text-foreground">Revenue over time</p>
            {salesQuery.isLoading ? (
              <p className="py-12 text-center text-sm text-muted-foreground">Loading chart…</p>
            ) : salesChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">
                No sales in this period yet.
              </p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={salesChartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
                    <Tooltip
                      formatter={(value) => [
                        formatMoney(typeof value === "number" ? value : Number(value)),
                        "Revenue",
                      ]}
                      labelFormatter={(label) => String(label)}
                    />
                    <Line
                      type="monotone"
                      dataKey="revenue"
                      stroke={CHART_COLOR}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>

          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full min-w-[480px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">Sale #</th>
                  <th className="px-3 py-2 font-medium">When</th>
                  <th className="px-3 py-2 font-medium">Items</th>
                  <th className="px-3 py-2 font-medium text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {salesQuery.isLoading ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                      Loading sales…
                    </td>
                  </tr>
                ) : (salesQuery.data?.sales.length ?? 0) === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                      No sales in this period.
                    </td>
                  </tr>
                ) : (
                  salesQuery.data?.sales.map((sale) => (
                    <tr key={sale.id} className="border-b border-border last:border-0">
                      <td className="px-3 py-2 font-mono text-xs">#{sale.id}</td>
                      <td className="px-3 py-2">{formatDateTime(sale.created_at)}</td>
                      <td className="px-3 py-2">{sale.item_count}</td>
                      <td className="px-3 py-2 text-right font-medium">
                        {formatMoney(sale.total)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {salesQuery.isError ? (
            <p className="text-sm text-destructive">Could not load sales report.</p>
          ) : null}
        </div>
      ) : null}

      {tab === "top-products" ? (
        <div className="space-y-4">
          <Card className="p-4">
            <p className="text-sm text-muted-foreground">
              Top {topProductsQuery.data?.products.length ?? 10} products by units sold this week.
            </p>
          </Card>

          <Card className="p-4">
            <p className="mb-4 text-sm font-medium text-foreground">Units sold</p>
            {topProductsQuery.isLoading ? (
              <p className="py-12 text-center text-sm text-muted-foreground">Loading chart…</p>
            ) : topProductsChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">
                No product sales this week yet.
              </p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topProductsChartData} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={56} />
                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="quantity" fill={CHART_COLOR} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>

          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">SKU</th>
                  <th className="px-3 py-2 font-medium">Product</th>
                  <th className="px-3 py-2 font-medium text-right">Qty sold</th>
                  <th className="px-3 py-2 font-medium text-right">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {topProductsQuery.isLoading ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                      Loading products…
                    </td>
                  </tr>
                ) : (topProductsQuery.data?.products.length ?? 0) === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                      No product sales this week.
                    </td>
                  </tr>
                ) : (
                  topProductsQuery.data?.products.map((p) => (
                    <tr key={p.product_id} className="border-b border-border last:border-0">
                      <td className="px-3 py-2 font-mono text-xs">{p.sku}</td>
                      <td className="px-3 py-2 font-medium">{p.name}</td>
                      <td className="px-3 py-2 text-right">{p.quantity_sold}</td>
                      <td className="px-3 py-2 text-right">{formatMoney(p.revenue)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {topProductsQuery.isError ? (
            <p className="text-sm text-destructive">Could not load top products report.</p>
          ) : null}
        </div>
      ) : null}

      {tab === "stock-value" ? (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Total stock value (at cost)
              </p>
              <p className="mt-2 text-3xl font-semibold text-foreground">
                {stockValueQuery.isLoading
                  ? "…"
                  : formatMoney(stockValueQuery.data?.total_value ?? 0)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Active SKUs
              </p>
              <p className="mt-2 text-3xl font-semibold text-foreground">
                {stockValueQuery.isLoading ? "…" : (stockValueQuery.data?.product_count ?? 0)}
              </p>
            </Card>
          </div>

          <p className="text-sm text-muted-foreground">
            Value = stock × cost price for active products. Showing top 25 by line value.
          </p>

          <div className="overflow-x-auto rounded-xl border border-border">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">SKU</th>
                  <th className="px-3 py-2 font-medium">Product</th>
                  <th className="px-3 py-2 font-medium text-right">Stock</th>
                  <th className="px-3 py-2 font-medium text-right">Cost</th>
                  <th className="px-3 py-2 font-medium text-right">Value</th>
                </tr>
              </thead>
              <tbody>
                {stockValueQuery.isLoading ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                      Loading stock value…
                    </td>
                  </tr>
                ) : (stockValueQuery.data?.items.length ?? 0) === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                      No active products in inventory.
                    </td>
                  </tr>
                ) : (
                  stockValueQuery.data?.items.map((item) => (
                    <tr key={item.product_id} className="border-b border-border last:border-0">
                      <td className="px-3 py-2 font-mono text-xs">{item.sku}</td>
                      <td className="px-3 py-2 font-medium">{item.name}</td>
                      <td className="px-3 py-2 text-right">{item.stock}</td>
                      <td className="px-3 py-2 text-right">{formatMoney(item.cost_price)}</td>
                      <td className="px-3 py-2 text-right font-medium">
                        {formatMoney(item.line_value)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {stockValueQuery.isError ? (
            <p className="text-sm text-destructive">Could not load stock value report.</p>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
