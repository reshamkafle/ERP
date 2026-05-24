import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { PurchaseFormCard } from "@/features/purchases/PurchaseFormCard"
import {
  confirmPurchase,
  createProcurementRun,
  discardDraftPurchase,
  fetchPurchases,
} from "@/features/purchases/purchases-api"
import { formatMoney } from "@/lib/format-money"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

export function PurchasesPage() {
    const queryClient = useQueryClient()

  const listQuery = useQuery({
    queryKey: ["purchases", "list"],
    queryFn: () => fetchPurchases({ limit: 50 }),
  })

  const procurementMutation = useMutation({
    mutationFn: () =>
      createProcurementRun({
        sales_lookback_days: 14,
        max_lines_per_supplier: 50,
        velocity_limit: 30,
      }),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: ["purchases", "list"] })
      const n = data.draft_purchase_ids.length
      const w = data.warnings.length
      toast.success(
        n
          ? `Created ${n} draft purchase order(s). Review and confirm below.`
          : "Agent run completed — no draft lines (check default suppliers and signals).",
      )
      if (w > 0) {
        toast.message(`${w} warning(s)`, {
          description: data.warnings.slice(0, 5).join("\n"),
        })
      }
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Procurement agent failed"
      toast.error(typeof detail === "string" ? detail : "Procurement agent failed")
    },
  })

  const confirmMutation = useMutation({
    mutationFn: (id: number) => confirmPurchase(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["purchases", "list"] })
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      toast.success("Purchase confirmed — stock updated.")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not confirm"
      toast.error(typeof detail === "string" ? detail : "Could not confirm")
    },
  })

  const discardMutation = useMutation({
    mutationFn: (id: number) => discardDraftPurchase(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["purchases", "list"] })
      toast.success("Draft purchase removed.")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not discard"
      toast.error(typeof detail === "string" ? detail : "Could not discard")
    },
  })

  const purchases = listQuery.data?.items ?? []

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Purchases"
        description="Receive inventory from suppliers — stock increases when a purchase is confirmed. AI can prepare draft orders; managers confirm to receive stock."
        actions={
          <Link to="/suppliers" className="text-sm text-primary hover:underline">
            Manage suppliers →
          </Link>
        }
      />

      <ContentSheet className="space-y-4">
      <section className="rounded-md border border-border bg-muted/30 p-4 space-y-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">AI procurement agent</h2>
            <p className="text-sm text-muted-foreground">
              LangGraph agents analyze low stock, sales velocity, and promotion flags (per product).
              Draft POs are grouped by each product&apos;s default supplier — you confirm each draft
              in the list below.
            </p>
          </div>
          <Button
            type="button"
            onClick={() => procurementMutation.mutate()}
            disabled={procurementMutation.isPending}
          >
            {procurementMutation.isPending ? "Running agent…" : "Run AI reorder"}
          </Button>
        </div>
      </section>

      <PurchaseFormCard />

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Purchases</h2>
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[800px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Supplier</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
                <th className="px-3 py-2 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {listQuery.isLoading ? (
                <tr>
                  <td colSpan={7} className="px-3 py-8 text-center text-muted-foreground">
                    Loading purchases…
                  </td>
                </tr>
              ) : purchases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-3 py-8 text-center text-muted-foreground">
                    No purchases recorded yet.
                  </td>
                </tr>
              ) : (
                purchases.map((purchase) => (
                  <tr key={purchase.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">#{purchase.id}</td>
                    <td className="px-3 py-2">
                      <Badge variant={purchase.status === "DRAFT" ? "warning" : "success"}>
                        {purchase.status}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">
                      <Link
                        to={`/suppliers/${purchase.supplier_id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {purchase.supplier_name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {new Date(purchase.created_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-2 tabular-nums">{purchase.item_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(purchase.total)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {purchase.status === "DRAFT" ? (
                        <div className="flex flex-wrap justify-end gap-2">
                          <Button
                            type="button"
                            size="sm"
                            variant="default"
                            disabled={confirmMutation.isPending}
                            onClick={() => confirmMutation.mutate(purchase.id)}
                          >
                            Confirm
                          </Button>
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            disabled={discardMutation.isPending}
                            onClick={() => {
                              if (window.confirm(`Discard draft #${purchase.id}?`)) {
                                discardMutation.mutate(purchase.id)
                              }
                            }}
                          >
                            Discard
                          </Button>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {listQuery.isError ? (
          <p className="text-sm text-destructive">Could not load purchases.</p>
        ) : null}
      </section>
      </ContentSheet>
    </div>
    </PosOnlyRedirect>
  )
}