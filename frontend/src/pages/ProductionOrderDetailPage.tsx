import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link, useParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  closeProductionOrder,
  completeProductionOrder,
  confirmProductionOrder,
  fetchProductionOrder,
  releaseProductionOrder,
  startProductionOrder,
} from "@/features/manufacturing/production-order-api"
import { useAuth } from "@/context/AuthContext"
import { canAccess } from "@/lib/permissions"

function statusVariant(status: string): "default" | "secondary" | "success" | "warning" | "danger" {
  const s = status.toUpperCase()
  if (s === "COMPLETED" || s === "CLOSED") return "success"
  if (s === "IN_PROGRESS" || s === "RELEASED") return "default"
  if (s === "PLANNED") return "secondary"
  if (s === "CANCELLED") return "danger"
  return "warning"
}

export function ProductionOrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const poId = Number(id)
  const queryClient = useQueryClient()
  const { permissions } = useAuth()
  const canWrite = canAccess(permissions, "manufacturing.ops.write")

  const poQuery = useQuery({
    queryKey: ["production-order", poId],
    queryFn: () => fetchProductionOrder(poId),
    enabled: Number.isFinite(poId),
  })

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["production-order", poId] })
    void queryClient.invalidateQueries({ queryKey: ["production-orders"] })
  }

  const releaseMut = useMutation({
    mutationFn: () => releaseProductionOrder(poId),
    onSuccess: () => {
      invalidate()
      toast.success("Order released")
    },
    onError: () => toast.error("Action failed"),
  })
  const startMut = useMutation({
    mutationFn: () => startProductionOrder(poId),
    onSuccess: () => {
      invalidate()
      toast.success("Production started")
    },
    onError: () => toast.error("Action failed"),
  })
  const confirmMut = useMutation({
    mutationFn: () =>
      confirmProductionOrder(poId, {
        quantity_completed: poQuery.data?.quantity_planned ?? "1",
        backflush: true,
      }),
    onSuccess: () => {
      invalidate()
      toast.success("Confirmation recorded")
    },
    onError: () => toast.error("Action failed"),
  })
  const completeMut = useMutation({
    mutationFn: () => completeProductionOrder(poId),
    onSuccess: () => {
      invalidate()
      toast.success("Order completed")
    },
    onError: () => toast.error("Action failed"),
  })
  const closeMut = useMutation({
    mutationFn: () => closeProductionOrder(poId),
    onSuccess: () => {
      invalidate()
      toast.success("Order closed")
    },
    onError: () => toast.error("Action failed"),
  })

  const po = poQuery.data

  if (poQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading…</p>
  }
  if (!po) {
    return <p className="text-sm text-muted-foreground">Production order not found.</p>
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={po.order_number}
        description={
          po.product_sku
            ? `${po.product_sku} — ${po.product_name ?? ""}`
            : `Product #${po.product_id}`
        }
        actions={
          <Link
            to="/manufacturing"
            className="inline-flex h-8 items-center rounded-md border px-3 text-xs font-medium"
          >
            Back to manufacturing
          </Link>
        }
      />

      <ContentSheet className="p-4">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant={statusVariant(po.status)}>{po.status}</Badge>
          <span className="text-sm">
            Planned: <strong>{po.quantity_planned}</strong>
          </span>
          <span className="text-sm">
            Completed: <strong>{po.quantity_completed}</strong>
          </span>
          <span className="text-sm text-muted-foreground">Priority: {po.priority}</span>
        </div>
        {canWrite ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {po.status === "PLANNED" ? (
              <Button size="sm" disabled={releaseMut.isPending} onClick={() => releaseMut.mutate()}>
                Release
              </Button>
            ) : null}
            {po.status === "RELEASED" ? (
              <Button size="sm" disabled={startMut.isPending} onClick={() => startMut.mutate()}>
                Start
              </Button>
            ) : null}
            {po.status === "IN_PROGRESS" || po.status === "RELEASED" ? (
              <Button size="sm" disabled={confirmMut.isPending} onClick={() => confirmMut.mutate()}>
                Confirm (backflush)
              </Button>
            ) : null}
            {po.status === "IN_PROGRESS" ? (
              <Button size="sm" disabled={completeMut.isPending} onClick={() => completeMut.mutate()}>
                Complete
              </Button>
            ) : null}
            {po.status === "COMPLETED" ? (
              <Button size="sm" disabled={closeMut.isPending} onClick={() => closeMut.mutate()}>
                Close (post variance)
              </Button>
            ) : null}
          </div>
        ) : null}
      </ContentSheet>

      <ContentSheet className="p-4">
        <h3 className="text-sm font-semibold">Operations</h3>
        {po.operations.length === 0 ? (
          <p className="mt-2 text-xs text-muted-foreground">No operations — assign a routing on edit.</p>
        ) : (
          <table className="mt-2 w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground">
                <th className="py-1">Seq</th>
                <th>Operation</th>
                <th>Status</th>
                <th className="text-right">Run min</th>
              </tr>
            </thead>
            <tbody>
              {po.operations.map((op) => (
                <tr key={op.id} className="border-t border-border/60">
                  <td className="py-2">{op.sequence}</td>
                  <td>{op.operation_name}</td>
                  <td>{op.status}</td>
                  <td className="text-right tabular-nums">{op.run_time_minutes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </ContentSheet>

      {po.notes ? (
        <ContentSheet className="p-4">
          <h3 className="text-sm font-semibold">Notes</h3>
          <p className="mt-1 text-sm text-muted-foreground">{po.notes}</p>
        </ContentSheet>
      ) : null}
    </div>
  )
}
