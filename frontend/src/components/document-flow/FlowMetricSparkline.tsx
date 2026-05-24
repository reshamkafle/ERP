import { Line, LineChart, ResponsiveContainer, Tooltip, YAxis } from "recharts"

import type { DocumentFlowChartPoint } from "@/types/dashboard-flow"
import { cn } from "@/lib/utils"

const STROKE_COLOR = "#000000"

type FlowMetricSparklineProps = {
  chart: DocumentFlowChartPoint[]
  className?: string
}

export function FlowMetricSparkline({
  chart,
  className,
}: FlowMetricSparklineProps) {
  const stroke = STROKE_COLOR
  const hasActivity = chart.some((p) => p.count > 0)

  if (!hasActivity) {
    return (
      <p className={cn("py-2 text-center text-[10px] text-black", className)}>
        No activity
      </p>
    )
  }

  return (
    <div className={cn("h-12 w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chart} margin={{ top: 2, right: 2, left: -24, bottom: 0 }}>
          <YAxis hide domain={[0, "auto"]} />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null
              const row = payload[0].payload as DocumentFlowChartPoint
              return (
                <div className="rounded-md border border-border bg-card px-2 py-1 text-[10px] text-black shadow-sm">
                  <p className="font-medium">{row.label}</p>
                  <p>{row.count} records</p>
                </div>
              )
            }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke={stroke}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 2, fill: "#000000", stroke: "#000000" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
