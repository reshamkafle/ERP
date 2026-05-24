import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { formatMoney } from "@/lib/format-money"
import type { InventorySalesDailyPoint } from "@/types/inventory"

const CHART_COLOR = "hsl(160 84% 39%)"

function formatDayLabel(isoDate: string): string {
  const d = new Date(`${isoDate}T12:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" })
}

function toNumber(value: string | number): number {
  const n = typeof value === "number" ? value : Number.parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

type InventorySalesChartProps = {
  dailyChart: InventorySalesDailyPoint[]
  lookbackDays: number
}

export function InventorySalesChart({ dailyChart, lookbackDays }: InventorySalesChartProps) {
  const chartData = dailyChart.map((p) => ({
    label: formatDayLabel(p.date),
    quantity: p.quantity_sold,
    revenue: toNumber(p.revenue),
  }))

  const hasSales = chartData.some((p) => p.quantity > 0 || p.revenue > 0)

  if (!hasSales) {
    return (
      <p className="py-6 text-center text-xs text-muted-foreground">
        No sales in the last {lookbackDays} days
      </p>
    )
  }

  return (
    <div className="h-24 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 4, right: 4, left: -18, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border/60" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 9 }}
            interval="preserveStartEnd"
            minTickGap={24}
          />
          <YAxis
            tick={{ fontSize: 9 }}
            width={28}
            allowDecimals={false}
            tickFormatter={(v) => String(v)}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (!active || !payload?.[0]) return null
              const row = payload[0].payload as {
                label: string
                quantity: number
                revenue: number
              }
              return (
                <div className="rounded-md border border-border bg-card px-2.5 py-1.5 text-xs shadow-sm">
                  <p className="font-medium text-foreground">{label ?? row.label}</p>
                  <p className="text-muted-foreground">{row.quantity} units sold</p>
                  <p className="text-muted-foreground">{formatMoney(row.revenue)} revenue</p>
                </div>
              )
            }}
          />
          <Line
            type="monotone"
            dataKey="quantity"
            stroke={CHART_COLOR}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
