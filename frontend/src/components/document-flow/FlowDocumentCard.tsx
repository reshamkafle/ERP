import type { LucideIcon } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { FlowMetricSparkline } from "@/components/document-flow/FlowMetricSparkline"
import type { DocumentFlowCardMetrics } from "@/types/dashboard-flow"
import { cn } from "@/lib/utils"

type FlowSection = "sales" | "procurement" | "production" | "finance"

const SECTION_STYLES: Record<
  FlowSection,
  { card: string; icon: string; badge: string }
> = {
  sales: {
    card: "border-blue-200 bg-white hover:border-blue-300 hover:shadow-md",
    icon: "text-black",
    badge: "bg-neutral-100 text-black",
  },
  procurement: {
    card: "border-orange-200 bg-white hover:border-orange-300 hover:shadow-md",
    icon: "text-black",
    badge: "bg-neutral-100 text-black",
  },
  production: {
    card: "border-emerald-200 bg-white hover:border-emerald-300 hover:shadow-md",
    icon: "text-black",
    badge: "bg-neutral-100 text-black",
  },
  finance: {
    card: "border-violet-200 bg-white hover:border-violet-300 hover:shadow-md",
    icon: "text-black",
    badge: "bg-neutral-100 text-black",
  },
}

type FlowDocumentCardProps = {
  id: string
  label: string
  icon: LucideIcon
  section: FlowSection
  route: string
  metrics?: DocumentFlowCardMetrics
  loading?: boolean
  step?: number
  layout?: "kanban" | "flow"
  footer?: React.ReactNode
}

export function FlowDocumentCard({
  label,
  icon: Icon,
  section,
  route,
  metrics,
  loading,
  step,
  layout = "kanban",
  footer,
}: FlowDocumentCardProps) {
  const navigate = useNavigate()
  const styles = SECTION_STYLES[section]

  const handleActivate = () => navigate(route)

  if (layout === "flow") {
    return (
      <button
        type="button"
        onClick={handleActivate}
        className={cn(
          "flex min-w-[8.5rem] max-w-[10.5rem] flex-col items-center gap-2 rounded-lg border px-3 py-3 text-center transition-colors",
          styles.card,
          "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        )}
      >
        <div
          className={cn(
            "flex size-10 items-center justify-center rounded-full border border-current/10 bg-white",
            styles.icon,
          )}
        >
          <Icon className="size-5" strokeWidth={1.75} aria-hidden />
        </div>
        <span className="text-xs font-medium leading-snug text-black">{label}</span>
        <CardMetricsBody metrics={metrics} loading={loading} styles={styles} compact />
        {footer}
      </button>
    )
  }

  return (
    <button
      type="button"
      onClick={handleActivate}
      className={cn(
        "w-full rounded-lg border p-3 text-left shadow-sm transition-colors",
        styles.card,
        "cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
      )}
    >
      <div className="flex items-start gap-3">
        {step != null ? (
          <span
            className={cn(
              "flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold",
              styles.badge,
            )}
          >
            {step}
          </span>
        ) : null}
        <div
          className={cn(
            "flex size-9 shrink-0 items-center justify-center rounded-lg border border-current/10 bg-white",
            styles.icon,
          )}
        >
          <Icon className="size-4.5" strokeWidth={1.75} aria-hidden />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium leading-snug text-black">{label}</p>
          <CardMetricsBody metrics={metrics} loading={loading} styles={styles} />
        </div>
      </div>
      {footer ? <div className="mt-2 border-t border-dashed border-border/80 pt-2">{footer}</div> : null}
    </button>
  )
}

function CardMetricsBody({
  metrics,
  loading,
  styles,
  compact,
}: {
  metrics?: DocumentFlowCardMetrics
  loading?: boolean
  styles: (typeof SECTION_STYLES)[FlowSection]
  compact?: boolean
}) {
  if (loading) {
    return (
      <div className={cn("space-y-1.5", compact ? "mt-1 w-full" : "mt-1")}>
        <div className="h-4 w-16 animate-pulse rounded bg-muted" />
        <div className="h-10 w-full animate-pulse rounded bg-muted/60" />
      </div>
    )
  }

  if (!metrics) return null

  return (
    <div className={cn(compact ? "mt-1 w-full" : "mt-1")}>
      <div className="flex flex-wrap items-center gap-2 text-black">
        <p className="text-lg font-semibold tabular-nums leading-none">{metrics.total}</p>
        <p className="text-[10px]">total</p>
        {metrics.new_count > 0 ? (
          <span
            className={cn(
              "rounded-full px-1.5 py-0.5 text-[10px] font-semibold tabular-nums",
              styles.badge,
            )}
          >
            {metrics.new_count} new
          </span>
        ) : null}
      </div>
      <FlowMetricSparkline chart={metrics.chart} />
    </div>
  )
}
