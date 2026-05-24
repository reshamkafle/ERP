import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import {
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
import { fetchManagerOverview } from "@/features/dashboard/manager-overview-api"
import { formatMoney } from "@/lib/format-money"
import type { ManagerPeriod } from "@/types/dashboard-manager"

const REVENUE_COLOR = "oklch(0.52 0.08 195)"
const PO_COLOR = "oklch(0.55 0.12 280)"

function toNumber(value: string): number {
  const n = Number.parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

const SEVERITY_CLASS: Record<string, string> = {
  critical: "border-destructive/40 bg-destructive/10 text-destructive",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-400",
  info: "border-border bg-muted/50 text-muted-foreground",
}

export function ManagerOverviewPanel() {
  const [period, setPeriod] = useState<ManagerPeriod>("week")

  const query = useQuery({
    queryKey: ["dashboard", "manager-overview", period],
    queryFn: () => fetchManagerOverview(period),
  })

  const chartData =
    query.data?.chart.map((point) => ({
      label: point.label,
      revenue: toNumber(point.revenue),
      purchase_spend: toNumber(point.purchase_spend),
    })) ?? []

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Operations overview</h2>
          <p className="text-sm text-muted-foreground">
            Cross-functional KPIs, sales vs purchase trend, and exception alerts.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {(
            [
              { value: "today", label: "Today" },
              { value: "week", label: "This week" },
              { value: "month", label: "This month" },
            ] as const
          ).map((opt) => (
            <Button
              key={opt.value}
              type="button"
              variant={period === opt.value ? "default" : "outline"}
              size="sm"
              onClick={() => setPeriod(opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Card className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Revenue</p>
          <p className="mt-2 text-2xl font-semibold">
            {query.isLoading ? "…" : formatMoney(query.data?.total_revenue ?? 0)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">PO spend</p>
          <p className="mt-2 text-2xl font-semibold">
            {query.isLoading ? "…" : formatMoney(query.data?.total_purchase_spend ?? 0)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Inventory value</p>
          <p className="mt-2 text-2xl font-semibold">
            {query.isLoading ? "…" : formatMoney(query.data?.inventory_value ?? 0)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Low stock SKUs</p>
          <p className="mt-2 text-2xl font-semibold">
            {query.isLoading ? "…" : (query.data?.low_stock_count ?? 0)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Open POs</p>
          <p className="mt-2 text-2xl font-semibold">
            {query.isLoading ? "…" : (query.data?.open_po_count ?? 0)}
          </p>
        </Card>
      </div>

      <Card className="p-4">
        <p className="mb-4 text-sm font-medium">Sales vs purchase spend</p>
        {query.isLoading ? (
          <p className="py-12 text-center text-sm text-muted-foreground">Loading chart…</p>
        ) : chartData.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">No activity in this period.</p>
        ) : (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v) => `$${v}`} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="revenue" name="Revenue" stroke={REVENUE_COLOR} strokeWidth={2} />
                <Line
                  type="monotone"
                  dataKey="purchase_spend"
                  name="PO spend"
                  stroke={PO_COLOR}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      <Card className="p-4">
        <p className="mb-3 text-sm font-medium">Exception board</p>
        {query.isLoading ? (
          <p className="text-sm text-muted-foreground">Loading alerts…</p>
        ) : (query.data?.alerts.length ?? 0) === 0 ? (
          <p className="text-sm text-muted-foreground">No exceptions — all clear.</p>
        ) : (
          <ul className="space-y-2">
            {query.data?.alerts.map((alert) => (
              <li
                key={`${alert.category}-${alert.message}`}
                className={`rounded-lg border px-3 py-2 text-sm ${SEVERITY_CLASS[alert.severity] ?? SEVERITY_CLASS.info}`}
              >
                <span className="font-medium uppercase">{alert.category}</span>
                <span className="mx-2">·</span>
                {alert.message}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
