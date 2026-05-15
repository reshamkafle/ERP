import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { SupplierFormDialog } from "@/features/suppliers/SupplierFormDialog"
import { fetchSupplier } from "@/features/suppliers/suppliers-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"

export function SupplierDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [dialogOpen, setDialogOpen] = useState(false)
  const supplierId = Number(id)

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const detailQuery = useQuery({
    queryKey: ["suppliers", "detail", supplierId],
    queryFn: () => fetchSupplier(supplierId),
    enabled: Number.isFinite(supplierId) && supplierId > 0,
  })

  if (!Number.isFinite(supplierId) || supplierId <= 0) {
    return <Navigate to="/suppliers" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading supplier…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Supplier not found.</p>
        <Link to="/suppliers" className="text-sm text-emerald-600 hover:underline dark:text-emerald-400">
          Back to suppliers
        </Link>
      </div>
    )
  }

  const supplier = detailQuery.data
  const purchases = supplier.recent_purchases

  return (
    <div className="space-y-6">
      <DetailHeader supplier={supplier} onEdit={() => setDialogOpen(true)} />

      <div className="grid gap-4 rounded-xl border border-border bg-card p-4 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Phone</p>
          <p className="text-sm">{supplier.phone ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Email</p>
          <p className="text-sm">{supplier.email ?? "—"}</p>
        </div>
        {supplier.notes ? (
          <NotesBlock notes={supplier.notes} />
        ) : null}
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Recent purchases</h2>
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[480px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Purchase #</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {purchases.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                    No purchases yet.
                  </td>
                </tr>
              ) : (
                purchases.map((purchase) => (
                  <tr key={purchase.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">#{purchase.id}</td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {new Date(purchase.created_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-2">{purchase.item_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(purchase.total)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {purchases.length > 0 ? (
          <p className="text-xs text-muted-foreground">Showing last {purchases.length} purchases.</p>
        ) : null}
      </section>

      <SupplierFormDialog
        open={dialogOpen}
        supplier={supplier}
        onClose={() => setDialogOpen(false)}
      />
    </div>
  )
}

function DetailHeader({
  supplier,
  onEdit,
}: {
  supplier: {
    name: string
    purchase_count: number
    total_spent: string
  }
  onEdit: () => void
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <Link
          to="/suppliers"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← Suppliers
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">{supplier.name}</h1>
        <p className="text-sm text-muted-foreground">
          {supplier.purchase_count} purchase{supplier.purchase_count === 1 ? "" : "s"} ·{" "}
          {formatMoney(supplier.total_spent)} total spent
        </p>
      </div>
      <div className="flex gap-2">
        <Link
          to="/purchases"
          className="inline-flex h-8 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium hover:bg-muted"
        >
          Record purchase
        </Link>
        <Button type="button" onClick={onEdit}>
          Edit supplier
        </Button>
      </div>
    </div>
  )
}

function NotesBlock({ notes }: { notes: string }) {
  return (
    <div className="sm:col-span-2">
      <p className="text-xs uppercase text-muted-foreground">Notes</p>
      <p className="whitespace-pre-wrap text-sm">{notes}</p>
    </div>
  )
}
