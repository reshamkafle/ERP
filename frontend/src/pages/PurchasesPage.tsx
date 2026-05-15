import { useQuery } from "@tanstack/react-query"
import { Link, Navigate } from "react-router-dom"

import { PurchaseFormCard } from "@/features/purchases/PurchaseFormCard"
import { fetchPurchases } from "@/features/purchases/purchases-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"

export function PurchasesPage() {
  const { user } = useAuth()

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const listQuery = useQuery({
    queryKey: ["purchases", "list"],
    queryFn: () => fetchPurchases({ limit: 50 }),
  })

  const purchases = listQuery.data?.items ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Purchases</h1>
          <p className="text-sm text-muted-foreground">
            Receive inventory from suppliers — stock increases in one transaction.
          </p>
        </div>
        <Link
          to="/suppliers"
          className="text-sm text-emerald-600 hover:underline dark:text-emerald-400"
        >
          Manage suppliers →
        </Link>
      </div>

      <PurchaseFormCard />

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Recent purchases</h2>
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">Supplier</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {listQuery.isLoading ? (
                <tr>
                  <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                    Loading purchases…
                  </td>
                </tr>
              ) : purchases.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                    No purchases recorded yet.
                  </td>
                </tr>
              ) : (
                purchases.map((purchase) => (
                  <tr key={purchase.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">#{purchase.id}</td>
                    <td className="px-3 py-2">
                      <Link
                        to={`/suppliers/${purchase.supplier_id}`}
                        className="font-medium text-emerald-600 hover:underline dark:text-emerald-400"
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
    </div>
  )
}
