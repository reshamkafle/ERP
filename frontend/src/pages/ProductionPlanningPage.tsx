import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import {
  completeCutOrder,
  fetchCutOrders,
  fetchProductionPlans,
  releasePlan,
  schedulePlan,
  type ProductionPlan,
} from "@/features/manufacturing/garment-planning-api"
import { cn } from "@/lib/utils"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "IN_PROGRESS") return "default"
  if (s === "SCHEDULED") return "warning"
  if (s === "CLOSED") return "success"
  if (s === "CANCELLED") return "danger"
  return "secondary"
}

function PlanDetailPanel({ plan }: { plan: ProductionPlan }) {
  const queryClient = useQueryClient()
  const { data: cutOrders = [] } = useQuery({
    queryKey: ["cut-orders", plan.id],
    queryFn: () => fetchCutOrders(plan.id),
  })

  const scheduleMut = useMutation({
    mutationFn: () => schedulePlan(plan.id),
    onSuccess: () => {
      toast.success("Plan scheduled")
      void queryClient.invalidateQueries({ queryKey: ["production-plans"] })
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const releaseMut = useMutation({
    mutationFn: () => releasePlan(plan.id),
    onSuccess: () => {
      toast.success("Plan released — cut orders and MOs created")
      void queryClient.invalidateQueries({ queryKey: ["production-plans"] })
      void queryClient.invalidateQueries({ queryKey: ["cut-orders", plan.id] })
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const completeCutMut = useMutation({
    mutationFn: (id: number) => completeCutOrder(id),
    onSuccess: () => {
      toast.success("Cut order completed")
      void queryClient.invalidateQueries({ queryKey: ["cut-orders", plan.id] })
    },
    onError: (e: Error) => toast.error(e.message),
  })

  const totalPlanned = plan.lines.reduce((s, l) => s + Number(l.quantity_planned), 0)

  return (
    <div className="space-y-4 rounded-lg border bg-card p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="font-mono text-sm font-semibold">{plan.plan_number}</h3>
        <Badge variant={statusVariant(plan.status)}>{plan.status}</Badge>
        {plan.contract_type && (
          <Badge variant="outline">
            {plan.contract_type}
            {plan.contract_number ? ` · ${plan.contract_number}` : ""}
          </Badge>
        )}
      </div>

      <div className="grid gap-2 text-xs text-muted-foreground sm:grid-cols-3">
        <span>Lines: {plan.lines.length}</span>
        <span>Total qty: {totalPlanned}</span>
        <span>Ship: {plan.target_ship_date ?? "—"}</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {plan.status === "DRAFT" && (
          <Button size="sm" variant="outline" onClick={() => scheduleMut.mutate()} disabled={scheduleMut.isPending}>
            Auto-schedule
          </Button>
        )}
        {(plan.status === "DRAFT" || plan.status === "SCHEDULED") && (
          <Button size="sm" onClick={() => releaseMut.mutate()} disabled={releaseMut.isPending}>
            Release plan
          </Button>
        )}
      </div>

      <div>
        <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Style / color / size matrix
        </h4>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b text-left text-muted-foreground">
                <th className="p-2">SKU</th>
                <th className="p-2">Color</th>
                <th className="p-2">Size</th>
                <th className="p-2 text-right">Planned</th>
                <th className="p-2 text-right">Cut</th>
              </tr>
            </thead>
            <tbody>
              {plan.lines.map((line) => (
                <tr key={line.id} className="border-b border-border/50">
                  <td className="p-2 font-mono">{line.product_sku}</td>
                  <td className="p-2">{line.color_label ?? "—"}</td>
                  <td className="p-2">{line.size_label ?? "—"}</td>
                  <td className="p-2 text-right">{line.quantity_planned}</td>
                  <td className="p-2 text-right">{line.quantity_cut}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {cutOrders.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Cut orders</h4>
          <ul className="space-y-2">
            {cutOrders.map((co) => (
              <li key={co.id} className="flex flex-wrap items-center justify-between gap-2 rounded border px-3 py-2 text-xs">
                <span className="font-mono">{co.cut_order_number}</span>
                <Badge variant={statusVariant(co.status)}>{co.status}</Badge>
                <span className="text-muted-foreground">
                  {co.fabric_item_sku ?? "Fabric"} · plies {co.plies ?? "—"} · {co.marker_ref ?? "no marker"}
                </span>
                {co.status !== "COMPLETED" && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => completeCutMut.mutate(co.id)}
                    disabled={completeCutMut.isPending}
                  >
                    Mark cut complete
                  </Button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {plan.schedules.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Schedule</h4>
          <ul className="space-y-1 text-xs">
            {plan.schedules.map((s) => (
              <li key={s.id} className="text-muted-foreground">
                {s.schedule_date} · {s.sewing_line_code ?? "Line"} · output {s.planned_output}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export function ProductionPlanningPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ["production-plans"],
    queryFn: () => fetchProductionPlans(),
  })

  const plans = data?.items ?? []
  const selected = plans.find((p) => p.id === selectedId) ?? plans[0] ?? null

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Production Planning & Scheduling"
        description="APS with style-color-size matrix, CMT contracts, cut orders, and line balancing."
        actions={
          <Button variant="outline" size="sm" asChild>
            <Link to="/manufacturing">Back to Manufacturing</Link>
          </Button>
        }
      />

      <ControlPanel>
        <p className="text-sm text-muted-foreground">
          Create plans from confirmed sales orders via API{" "}
          <code className="rounded bg-muted px-1">POST /manufacturing/planning/plans/from-sales</code>. Release
          generates cut orders and production orders with automatic line balancing.
        </p>
      </ControlPanel>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading plans…</p>
      ) : plans.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No production plans yet. Link a sales order to create your first plan.
        </p>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <ul className="space-y-1">
            {plans.map((plan) => (
              <li key={plan.id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(plan.id)}
                  className={cn(
                    "w-full rounded-md border px-3 py-2 text-left text-sm transition-colors",
                    selected?.id === plan.id ? "border-primary bg-primary/5" : "hover:bg-muted/50",
                  )}
                >
                  <span className="font-mono text-xs">{plan.plan_number}</span>
                  <Badge className="ml-2" variant={statusVariant(plan.status)}>
                    {plan.status}
                  </Badge>
                </button>
              </li>
            ))}
          </ul>
          {selected && <PlanDetailPanel plan={selected} />}
        </div>
      )}
    </div>
  )
}
