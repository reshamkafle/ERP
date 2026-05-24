import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { ArrowDown, ArrowRight, GitBranch, LayoutGrid, Workflow } from "lucide-react"

import { FlowDocumentCard } from "@/components/document-flow/FlowDocumentCard"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/context/AuthContext"
import { fetchDocumentFlowMetrics } from "@/features/dashboard/dashboard-flow-api"
import {
  CROSS_LINKS,
  NODE_LABELS,
  buildVisibleFlowLanes,
  type FlowLaneView,
  type FlowSection,
} from "@/lib/document-flow-cards"
import { canAccess } from "@/lib/permissions"
import { cn } from "@/lib/utils"
import type { DocumentFlowCardMetrics } from "@/types/dashboard-flow"

type ViewMode = "kanban" | "flow"

const SECTION_STYLES: Record<
  FlowSection,
  {
    lane: string
    legend: string
    arrow: string
    column: string
    columnHeader: string
  }
> = {
  sales: {
    lane: "border-blue-200 bg-blue-50/60",
    legend: "bg-blue-500",
    arrow: "text-blue-400",
    column: "border-blue-200/80 bg-blue-50/40",
    columnHeader: "border-blue-300 bg-blue-100/80 text-blue-950",
  },
  procurement: {
    lane: "border-orange-200 bg-orange-50/60",
    legend: "bg-orange-500",
    arrow: "text-orange-400",
    column: "border-orange-200/80 bg-orange-50/40",
    columnHeader: "border-orange-300 bg-orange-100/80 text-orange-950",
  },
  production: {
    lane: "border-emerald-200 bg-emerald-50/60",
    legend: "bg-emerald-500",
    arrow: "text-emerald-400",
    column: "border-emerald-200/80 bg-emerald-50/40",
    columnHeader: "border-emerald-300 bg-emerald-100/80 text-emerald-950",
  },
  finance: {
    lane: "border-violet-200 bg-violet-50/60",
    legend: "bg-violet-500",
    arrow: "text-violet-400",
    column: "border-violet-200/80 bg-violet-50/40",
    columnHeader: "border-violet-300 bg-violet-100/80 text-violet-950",
  },
}

const OUTBOUND_LINKS = CROSS_LINKS.reduce<Record<string, typeof CROSS_LINKS>>((acc, link) => {
  if (!acc[link.from]) acc[link.from] = []
  acc[link.from].push(link)
  return acc
}, {})

function FlowArrow({ section }: { section: FlowSection }) {
  return (
    <div className={cn("flex shrink-0 items-center px-1 sm:px-2", SECTION_STYLES[section].arrow)} aria-hidden>
      <svg width="28" height="16" viewBox="0 0 28 16" fill="none" className="h-4 w-7">
        <path
          d="M0 8h20m0 0l-4-4m4 4l-4 4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  )
}

function CrossLinkFooter({ cardId }: { cardId: string }) {
  const outbound = OUTBOUND_LINKS[cardId] ?? []
  if (outbound.length === 0) return null
  return (
    <ul className="space-y-1">
      {outbound.map((link) => (
        <li key={`${link.from}-${link.to}`} className="flex items-center gap-1.5 text-[11px] text-black">
          <GitBranch className="size-3 shrink-0 text-black" aria-hidden />
          <span>
            <span className="font-medium">{link.label}</span>
            {" → "}
            {NODE_LABELS[link.to]}
          </span>
        </li>
      ))}
    </ul>
  )
}

function KanbanColumn({
  lane,
  columnIndex,
  metricsById,
  loading,
}: {
  lane: FlowLaneView
  columnIndex: number
  metricsById: Record<string, DocumentFlowCardMetrics>
  loading: boolean
}) {
  const styles = SECTION_STYLES[lane.section]
  return (
    <div className="flex min-w-[16rem] max-w-[18rem] flex-1 flex-col">
      <div
        className={cn(
          "mb-3 flex items-center justify-between rounded-lg border px-3 py-2",
          styles.columnHeader,
        )}
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide opacity-80">Stage {columnIndex + 1}</p>
          <p className="text-sm font-semibold">{lane.title}</p>
        </div>
        <span className="rounded-full bg-white/70 px-2 py-0.5 text-xs font-medium tabular-nums">
          {lane.cards.length}
        </span>
      </div>
      <div className={cn("flex flex-1 flex-col gap-2 rounded-xl border p-2.5", styles.column)}>
        {lane.cards.map((card, index) => (
          <div key={card.id} className="flex flex-col items-center gap-2">
            <FlowDocumentCard
              id={card.id}
              label={card.label}
              icon={card.icon}
              section={card.section}
              route={card.route}
              metrics={metricsById[card.id]}
              loading={loading}
              step={index + 1}
              layout="kanban"
              footer={<CrossLinkFooter cardId={card.id} />}
            />
            {index < lane.cards.length - 1 ? (
              <ArrowDown className={cn("size-4 shrink-0", styles.arrow)} strokeWidth={2} aria-hidden />
            ) : null}
          </div>
        ))}
      </div>
    </div>
  )
}

function KanbanBoard({
  lanes,
  metricsById,
  loading,
}: {
  lanes: FlowLaneView[]
  metricsById: Record<string, DocumentFlowCardMetrics>
  loading: boolean
}) {
  return (
    <div
      className="flex gap-3 overflow-x-auto pb-2"
      role="img"
      aria-label="Manufacturing document flow kanban board"
    >
      {lanes.map((lane, index) => (
        <div key={lane.id} className="flex shrink-0 items-stretch">
          <KanbanColumn
            lane={lane}
            columnIndex={index}
            metricsById={metricsById}
            loading={loading}
          />
          {index < lanes.length - 1 ? (
            <div className="flex w-8 shrink-0 items-center justify-center self-center pt-10">
              <ArrowRight className="size-5 text-muted-foreground/50" strokeWidth={1.75} aria-hidden />
            </div>
          ) : null}
        </div>
      ))}
    </div>
  )
}

function LaneRow({
  lane,
  metricsById,
  loading,
}: {
  lane: FlowLaneView
  metricsById: Record<string, DocumentFlowCardMetrics>
  loading: boolean
}) {
  const styles = SECTION_STYLES[lane.section]
  return (
    <div className={cn("rounded-xl border p-4", styles.lane)}>
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{lane.title}</p>
      <div className="flex flex-nowrap items-start gap-y-3 overflow-x-auto pb-1">
        {lane.cards.map((card, index) => (
          <div key={card.id} className="flex items-start">
            <FlowDocumentCard
              id={card.id}
              label={card.label}
              icon={card.icon}
              section={card.section}
              route={card.route}
              metrics={metricsById[card.id]}
              loading={loading}
              layout="flow"
            />
            {index < lane.cards.length - 1 ? <FlowArrow section={lane.section} /> : null}
          </div>
        ))}
      </div>
    </div>
  )
}

function CrossLinksPanel() {
  return (
    <div className="rounded-lg border border-dashed border-border bg-white p-4">
      <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Cross-process links
      </p>
      <ul className="grid gap-2 sm:grid-cols-2">
        {CROSS_LINKS.map((link) => (
          <li key={`${link.from}-${link.to}`} className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="inline-flex size-5 shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-bold text-foreground">
              ↓
            </span>
            <span>
              <span className="font-medium text-foreground">{link.label}</span>
              {" — "}
              {NODE_LABELS[link.from]} → {NODE_LABELS[link.to]}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function SectionLegend() {
  const items: { section: FlowSection; label: string }[] = [
    { section: "sales", label: "Sales" },
    { section: "procurement", label: "Procurement" },
    { section: "production", label: "Production" },
    { section: "finance", label: "Finance" },
  ]
  return (
    <div className="flex flex-wrap gap-4">
      {items.map((item) => (
        <div key={item.section} className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className={cn("size-3 rounded-sm", SECTION_STYLES[item.section].legend)} aria-hidden />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  )
}

function ViewToggle({ mode, onChange }: { mode: ViewMode; onChange: (mode: ViewMode) => void }) {
  return (
    <div className="inline-flex rounded-lg border border-border bg-muted/40 p-0.5">
      <Button
        type="button"
        size="sm"
        variant={mode === "kanban" ? "default" : "ghost"}
        className="h-7 gap-1.5 px-2.5"
        onClick={() => onChange("kanban")}
        aria-pressed={mode === "kanban"}
      >
        <LayoutGrid className="size-3.5" aria-hidden />
        Kanban
      </Button>
      <Button
        type="button"
        size="sm"
        variant={mode === "flow" ? "default" : "ghost"}
        className="h-7 gap-1.5 px-2.5"
        onClick={() => onChange("flow")}
        aria-pressed={mode === "flow"}
      >
        <Workflow className="size-3.5" aria-hidden />
        Flow
      </Button>
    </div>
  )
}

/** End-to-end manufacturing ERP document flow for the dashboard. */
export function ManufacturingDocumentFlowChart() {
  const [view, setView] = useState<ViewMode>("kanban")
  const { permissions } = useAuth()

  const lanes = useMemo(() => buildVisibleFlowLanes(permissions), [permissions])

  const metricsQuery = useQuery({
    queryKey: ["dashboard", "document-flow-metrics", "week", 30],
    queryFn: () => fetchDocumentFlowMetrics({ period: "week", newDays: 30 }),
    enabled: canAccess(permissions, "reports.dashboard.read"),
  })

  const metricsById = useMemo(() => {
    const map: Record<string, DocumentFlowCardMetrics> = {}
    for (const card of metricsQuery.data?.cards ?? []) {
      map[card.id] = card
    }
    return map
  }, [metricsQuery.data?.cards])

  const loading = metricsQuery.isLoading

  if (lanes.length === 0) {
    return (
      <Card className="border-border bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Manufacturing document flow</CardTitle>
          <CardDescription>
            You do not have permission to view any documents in this flow.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden border-border bg-white shadow-sm">
      <CardHeader className="border-b border-border/80 bg-white pb-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle className="text-lg">Manufacturing document flow</CardTitle>
            <CardDescription>
              {view === "kanban"
                ? "Kanban stages with live counts, 30-day new records, and activity trends. Click a card to open its list."
                : "End-to-end document path with metrics. Click a card to navigate."}
            </CardDescription>
          </div>
          <ViewToggle mode={view} onChange={setView} />
        </div>
        <div className="pt-2">
          <SectionLegend />
        </div>
      </CardHeader>
      <CardContent className="space-y-4 bg-white pt-4">
        {view === "kanban" ? (
          <>
            <KanbanBoard lanes={lanes} metricsById={metricsById} loading={loading} />
            <p className="text-xs text-muted-foreground">
              Cards show totals and records created in the last 30 days. Click a card to open that
              document list.
            </p>
          </>
        ) : (
          <>
            <div className="space-y-4" role="img" aria-label="Manufacturing company document flow diagram">
              {lanes.map((lane) => (
                <LaneRow key={lane.id} lane={lane} metricsById={metricsById} loading={loading} />
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              Arrows show sequence within each process area. Click any card to open its list.
            </p>
          </>
        )}
        <CrossLinksPanel />
      </CardContent>
    </Card>
  )
}
