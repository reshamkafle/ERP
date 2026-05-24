import { useQuery } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
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
  fetchFinanceSummaryReport,
  fetchInventoryPerformanceReport,
  fetchItOverviewReport,
  fetchMarketingFunnelReport,
  fetchPurchaseOrdersReport,
  fetchSalesReport,
  fetchStockValueReport,
  fetchTopProductsReport,
} from "@/features/reports/reports-api"
import { useAuth } from "@/context/AuthContext"
import { visibleReportTabs, type ReportTabDef } from "@/lib/report-access"
import { formatMoney } from "@/lib/format-money"
import type { FinancePeriod, ReportPeriod, ReportTabId } from "@/types/report"

const CHART_COLOR = "oklch(0.52 0.08 195)"
const CHART_COLOR_ALT = "oklch(0.55 0.12 280)"

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

function PeriodButtons({
  period,
  onChange,
  options,
}: {
  period: string
  onChange: (p: string) => void
  options: { value: string; label: string }[]
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <Button
          key={opt.value}
          type="button"
          variant={period === opt.value ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </Button>
      ))}
    </div>
  )
}

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-foreground">{value}</p>
    </Card>
  )
}

function TabButtons({
  tabs,
  tab,
  onTabChange,
}: {
  tabs: ReportTabDef[]
  tab: ReportTabId
  onTabChange: (id: ReportTabId) => void
}) {
  const groups = useMemo(() => {
    const map = new Map<string, ReportTabDef[]>()
    for (const t of tabs) {
      const list = map.get(t.group) ?? []
      list.push(t)
      map.set(t.group, list)
    }
    return [...map.entries()]
  }, [tabs])

  return (
    <div className="space-y-3">
      {groups.map(([group, groupTabs]) => (
        <div key={group} className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{group}</p>
          <div className="flex flex-wrap gap-2">
            {groupTabs.map((item) => (
              <Button
                key={item.id}
                type="button"
                variant={tab === item.id ? "default" : "outline"}
                size="sm"
                onClick={() => onTabChange(item.id)}
              >
                {item.label}
              </Button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export function ReportsHub() {
  const { permissions } = useAuth()
  const tabs = useMemo(() => visibleReportTabs(permissions), [permissions])
  const [tab, setTab] = useState<ReportTabId>(() => tabs[0]?.id ?? "sales")
  const [salesPeriod, setSalesPeriod] = useState<ReportPeriod>("today")
  const [poPeriod, setPoPeriod] = useState<ReportPeriod>("week")
  const [financePeriod, setFinancePeriod] = useState<FinancePeriod>("week")

  const activeTab = tabs.some((t) => t.id === tab) ? tab : (tabs[0]?.id ?? "sales")

  const salesQuery = useQuery({
    queryKey: ["reports", "sales", salesPeriod],
    queryFn: () => fetchSalesReport(salesPeriod),
    enabled: activeTab === "sales",
  })

  const topProductsQuery = useQuery({
    queryKey: ["reports", "top-products"],
    queryFn: fetchTopProductsReport,
    enabled: activeTab === "top-products",
  })

  const stockValueQuery = useQuery({
    queryKey: ["reports", "stock-value"],
    queryFn: fetchStockValueReport,
    enabled: activeTab === "stock-value",
  })

  const poQuery = useQuery({
    queryKey: ["reports", "purchase-orders", poPeriod],
    queryFn: () => fetchPurchaseOrdersReport(poPeriod),
    enabled: activeTab === "purchase-orders",
  })

  const inventoryQuery = useQuery({
    queryKey: ["reports", "inventory-performance"],
    queryFn: fetchInventoryPerformanceReport,
    enabled: activeTab === "inventory-performance",
  })

  const financeQuery = useQuery({
    queryKey: ["reports", "finance-summary", financePeriod],
    queryFn: () => fetchFinanceSummaryReport(financePeriod),
    enabled: activeTab === "finance-summary",
  })

  const marketingQuery = useQuery({
    queryKey: ["reports", "marketing-funnel"],
    queryFn: fetchMarketingFunnelReport,
    enabled: activeTab === "marketing-funnel",
  })

  const itQuery = useQuery({
    queryKey: ["reports", "it-overview"],
    queryFn: fetchItOverviewReport,
    enabled: activeTab === "it-overview",
  })

  if (tabs.length === 0) {
    return (
      <Card className="p-6 text-sm text-muted-foreground">
        No report permissions assigned to your role. Contact an administrator.
      </Card>
    )
  }

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
    })) ?? []

  const poChartData =
    poQuery.data?.chart.map((p) => ({
      label: p.label,
      spend: toNumber(p.spend),
      po_count: p.po_count,
    })) ?? []

  const financeChartData =
    financeQuery.data?.chart.map((p) => ({
      label: p.label,
      inbound: toNumber(p.inbound),
      outbound: toNumber(p.outbound),
    })) ?? []

  const managerChartData =
    marketingQuery.data?.customer_growth_chart.map((p) => ({
      label: p.label,
      count: p.count,
    })) ?? []

  return (
    <div className="space-y-4">
      <TabButtons tabs={tabs} tab={activeTab} onTabChange={setTab} />

      {activeTab === "sales" ? (
        <div className="space-y-4">
          <PeriodButtons
            period={salesPeriod}
            onChange={(p) => setSalesPeriod(p as ReportPeriod)}
            options={[
              { value: "today", label: "Today" },
              { value: "week", label: "This week" },
              { value: "month", label: "This month" },
            ]}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <KpiCard
              label="Total revenue"
              value={salesQuery.isLoading ? "…" : formatMoney(salesQuery.data?.total_revenue ?? 0)}
            />
            <KpiCard label="Sales count" value={salesQuery.isLoading ? "…" : (salesQuery.data?.sale_count ?? 0)} />
          </div>
          <Card className="p-4">
            <p className="mb-4 text-sm font-medium text-foreground">Revenue over time</p>
            {salesQuery.isLoading ? (
              <p className="py-12 text-center text-sm text-muted-foreground">Loading chart…</p>
            ) : salesChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">No sales in this period yet.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={salesChartData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
                    <Tooltip formatter={(value) => formatMoney(typeof value === "number" ? value : Number(value))} />
                    <Line type="monotone" dataKey="revenue" stroke={CHART_COLOR} strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
          <DataTable
            headers={["Sale #", "When", "Items", "Total"]}
            loading={salesQuery.isLoading}
            emptyMessage="No sales in this period."
            rows={(salesQuery.data?.sales ?? []).map((sale) => [
              `#${sale.id}`,
              formatDateTime(sale.created_at),
              String(sale.item_count),
              formatMoney(sale.total),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "top-products" ? (
        <div className="space-y-4">
          <Card className="p-4 text-sm text-muted-foreground">
            Top {topProductsQuery.data?.products.length ?? 10} products by units sold this week.
          </Card>
          <Card className="p-4">
            <p className="mb-4 text-sm font-medium">Units sold</p>
            {topProductsChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">No product sales this week.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={topProductsChartData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={56} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="quantity" fill={CHART_COLOR} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
          <DataTable
            headers={["SKU", "Product", "Qty sold", "Revenue"]}
            loading={topProductsQuery.isLoading}
            emptyMessage="No product sales this week."
            rows={(topProductsQuery.data?.products ?? []).map((p) => [
              p.sku,
              p.name,
              String(p.quantity_sold),
              formatMoney(p.revenue),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "purchase-orders" ? (
        <div className="space-y-4">
          <PeriodButtons
            period={poPeriod}
            onChange={(p) => setPoPeriod(p as ReportPeriod)}
            options={[
              { value: "today", label: "Today" },
              { value: "week", label: "This week" },
              { value: "month", label: "This month" },
            ]}
          />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label="PO spend" value={poQuery.isLoading ? "…" : formatMoney(poQuery.data?.total_spend ?? 0)} />
            <KpiCard label="PO count" value={poQuery.isLoading ? "…" : (poQuery.data?.po_count ?? 0)} />
            <KpiCard label="Open POs" value={poQuery.isLoading ? "…" : (poQuery.data?.open_po_count ?? 0)} />
            <KpiCard
              label="Open PO value"
              value={poQuery.isLoading ? "…" : formatMoney(poQuery.data?.open_po_value ?? 0)}
            />
          </div>
          <Card className="p-4">
            <p className="mb-4 text-sm font-medium">Purchase spend over time</p>
            {poChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">No purchase orders in this period.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={poChartData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tickFormatter={(v) => `$${v}`} />
                    <Tooltip />
                    <Line type="monotone" dataKey="spend" stroke={CHART_COLOR_ALT} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
          <DataTable
            headers={["PO #", "When", "Supplier", "Status", "Total"]}
            loading={poQuery.isLoading}
            emptyMessage="No purchase orders in this period."
            rows={(poQuery.data?.purchases ?? []).map((po) => [
              `#${po.id}`,
              formatDateTime(po.created_at),
              po.supplier_name ?? "—",
              po.status,
              formatMoney(po.total),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "inventory-performance" ? (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label="Low stock SKUs" value={inventoryQuery.isLoading ? "…" : (inventoryQuery.data?.low_stock_count ?? 0)} />
            <KpiCard
              label="Dead stock value"
              value={inventoryQuery.isLoading ? "…" : formatMoney(inventoryQuery.data?.dead_stock_value ?? 0)}
            />
            <KpiCard
              label="Total stock value"
              value={inventoryQuery.isLoading ? "…" : formatMoney(inventoryQuery.data?.total_stock_value ?? 0)}
            />
            <KpiCard label="Open POs" value={inventoryQuery.isLoading ? "…" : (inventoryQuery.data?.open_po_count ?? 0)} />
          </div>
          <DataTable
            title="Low stock items"
            headers={["SKU", "Product", "Stock", "Threshold", "Value"]}
            loading={inventoryQuery.isLoading}
            emptyMessage="No low-stock items."
            rows={(inventoryQuery.data?.low_stock_items ?? []).map((item) => [
              item.sku,
              item.name,
              String(item.stock),
              String(item.low_stock_threshold),
              formatMoney(item.line_value),
            ])}
          />
          <DataTable
            title="Dead / non-moving stock"
            headers={["SKU", "Product", "Stock", "Value"]}
            loading={inventoryQuery.isLoading}
            emptyMessage="No dead stock flagged."
            rows={(inventoryQuery.data?.dead_stock_items ?? []).map((item) => [
              item.sku,
              item.name,
              String(item.stock),
              formatMoney(item.line_value),
            ])}
          />
          <DataTable
            title="Sell-through (top movers)"
            headers={["SKU", "Product", "Sold", "Stock", "Sell-through %"]}
            loading={inventoryQuery.isLoading}
            emptyMessage="No sell-through data."
            rows={(inventoryQuery.data?.sell_through_items ?? []).map((item) => [
              item.sku,
              item.name,
              String(item.units_sold),
              String(item.stock),
              `${item.sell_through_pct}%`,
            ])}
          />
          <DataTable
            title="Open POs awaiting receipt"
            headers={["PO #", "When", "Supplier", "Total"]}
            loading={inventoryQuery.isLoading}
            emptyMessage="No open purchase orders."
            rows={(inventoryQuery.data?.open_po_items ?? []).map((po) => [
              `#${po.id}`,
              formatDateTime(po.created_at),
              po.supplier_name ?? "—",
              formatMoney(po.total),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "stock-value" ? (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <KpiCard
              label="Total stock value (at cost)"
              value={stockValueQuery.isLoading ? "…" : formatMoney(stockValueQuery.data?.total_value ?? 0)}
            />
            <KpiCard label="Active SKUs" value={stockValueQuery.isLoading ? "…" : (stockValueQuery.data?.product_count ?? 0)} />
          </div>
          <DataTable
            headers={["SKU", "Product", "Stock", "Cost", "Value"]}
            loading={stockValueQuery.isLoading}
            emptyMessage="No active products in inventory."
            rows={(stockValueQuery.data?.items ?? []).map((item) => [
              item.sku,
              item.name,
              String(item.stock),
              formatMoney(item.cost_price),
              formatMoney(item.line_value),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "finance-summary" ? (
        <div className="space-y-4">
          <PeriodButtons
            period={financePeriod}
            onChange={(p) => setFinancePeriod(p as FinancePeriod)}
            options={[
              { value: "week", label: "This week" },
              { value: "month", label: "This month" },
            ]}
          />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label="Payments in" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.payments_in ?? 0)} />
            <KpiCard label="Payments out" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.payments_out ?? 0)} />
            <KpiCard label="AP outstanding" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.ap_outstanding ?? 0)} />
            <KpiCard label="AR outstanding" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.ar_outstanding ?? 0)} />
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <KpiCard label="Revenue" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.revenue ?? 0)} />
            <KpiCard label="COGS (approx.)" value={financeQuery.isLoading ? "…" : formatMoney(financeQuery.data?.cogs_approx ?? 0)} />
            <KpiCard label="Gross margin" value={financeQuery.isLoading ? "…" : `${financeQuery.data?.gross_margin_pct ?? 0}%`} />
          </div>
          <Card className="p-4">
            <p className="mb-4 text-sm font-medium">Cash flow</p>
            {financeChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">No confirmed payments in this period.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={financeChartData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis tickFormatter={(v) => `$${v}`} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="inbound" name="In" stroke={CHART_COLOR} strokeWidth={2} />
                    <Line type="monotone" dataKey="outbound" name="Out" stroke={CHART_COLOR_ALT} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
          <DataTable
            title="AP outstanding by supplier"
            headers={["PO #", "Supplier", "Total", "Paid", "Outstanding"]}
            loading={financeQuery.isLoading}
            emptyMessage="No outstanding AP."
            rows={(financeQuery.data?.ap_by_supplier ?? []).map((row) => [
              `#${row.id}`,
              row.party_name,
              formatMoney(row.total),
              formatMoney(row.amount_paid),
              formatMoney(row.outstanding),
            ])}
          />
          <DataTable
            title="PO spend by vendor"
            headers={["Supplier", "Spend", "PO count"]}
            loading={financeQuery.isLoading}
            emptyMessage="No vendor spend in this period."
            rows={(financeQuery.data?.po_spend_by_vendor ?? []).map((row) => [
              row.supplier_name,
              formatMoney(row.total_spend),
              String(row.po_count),
            ])}
          />
        </div>
      ) : null}

      {activeTab === "marketing-funnel" ? (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <KpiCard label="Total leads" value={marketingQuery.isLoading ? "…" : (marketingQuery.data?.total_leads ?? 0)} />
            <KpiCard label="Opportunities" value={marketingQuery.isLoading ? "…" : (marketingQuery.data?.total_opportunities ?? 0)} />
            <KpiCard label="Customers" value={marketingQuery.isLoading ? "…" : (marketingQuery.data?.total_customers ?? 0)} />
            <KpiCard label="New customers (30d)" value={marketingQuery.isLoading ? "…" : (marketingQuery.data?.new_customers_30d ?? 0)} />
          </div>
          <DataTable
            title="Leads by status"
            headers={["Status", "Count"]}
            loading={marketingQuery.isLoading}
            emptyMessage="No leads yet."
            rows={(marketingQuery.data?.leads_by_status ?? []).map((row) => [row.status, String(row.count)])}
          />
          <DataTable
            title="Opportunities by stage"
            headers={["Stage", "Count", "Pipeline value"]}
            loading={marketingQuery.isLoading}
            emptyMessage="No opportunities yet."
            rows={(marketingQuery.data?.opportunities_by_stage ?? []).map((row) => [
              row.stage,
              String(row.count),
              formatMoney(row.total_value),
            ])}
          />
          <Card className="p-4">
            <p className="mb-4 text-sm font-medium">Customer growth (30 days)</p>
            {managerChartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">No new customers in the last 30 days.</p>
            ) : (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={managerChartData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill={CHART_COLOR} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </Card>
        </div>
      ) : null}

      {activeTab === "it-overview" ? (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <KpiCard label="API status" value={itQuery.data?.api_status ?? "…"} />
            <KpiCard label="Database" value={itQuery.data?.db_status ?? "…"} />
            <KpiCard label="Active users" value={itQuery.isLoading ? "…" : (itQuery.data?.active_user_count ?? 0)} />
            <KpiCard label="Roles" value={itQuery.isLoading ? "…" : (itQuery.data?.role_count ?? 0)} />
            <KpiCard label="Permissions" value={itQuery.isLoading ? "…" : (itQuery.data?.permission_count ?? 0)} />
          </div>
          <DataTable
            title="Users by role"
            headers={["Role", "Users"]}
            loading={itQuery.isLoading}
            emptyMessage="No roles configured."
            rows={(itQuery.data?.roles ?? []).map((row) => [row.role_name, String(row.user_count)])}
          />
          <DataTable
            title="Agent runs"
            headers={["Type", "Status", "Count"]}
            loading={itQuery.isLoading}
            emptyMessage="No agent runs recorded."
            rows={(itQuery.data?.agent_runs ?? []).map((row) => [row.run_type, row.status, String(row.count)])}
          />
        </div>
      ) : null}
    </div>
  )
}

function DataTable({
  title,
  headers,
  rows,
  loading,
  emptyMessage,
}: {
  title?: string
  headers: string[]
  rows: string[][]
  loading?: boolean
  emptyMessage: string
}) {
  return (
    <div className="space-y-2">
      {title ? <p className="text-sm font-medium text-foreground">{title}</p> : null}
      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[480px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              {headers.map((header) => (
                <th key={header} className="px-3 py-2 font-medium">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={headers.length} className="px-3 py-8 text-center text-muted-foreground">
                  Loading…
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={headers.length} className="px-3 py-8 text-center text-muted-foreground">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={`${row[0]}-${index}`} className="border-b border-border last:border-0">
                  {row.map((cell, cellIndex) => (
                    <td
                      key={`${index}-${cellIndex}`}
                      className={`px-3 py-2 ${cellIndex === row.length - 1 ? "text-right font-medium" : ""}`}
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
