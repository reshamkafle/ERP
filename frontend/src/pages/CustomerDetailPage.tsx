import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { CustomerFormDialog } from "@/features/customers/CustomerFormDialog"
import { fetchCustomer } from "@/features/customers/customers-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [dialogOpen, setDialogOpen] = useState(false)
  const customerId = Number(id)

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const detailQuery = useQuery({
    queryKey: ["customers", "detail", customerId],
    queryFn: () => fetchCustomer(customerId),
    enabled: Number.isFinite(customerId) && customerId > 0,
  })

  if (!Number.isFinite(customerId) || customerId <= 0) {
    return <Navigate to="/customers" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading customer…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Customer not found.</p>
        <Link to="/customers" className="text-sm text-emerald-600 hover:underline dark:text-emerald-400">
          Back to customers
        </Link>
      </div>
    )
  }

  const customer = detailQuery.data
  const sales = customer.recent_sales

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            to="/customers"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            ← Customers
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-foreground">{customer.name}</h1>
          <p className="text-sm text-muted-foreground">Purchase history and contact details</p>
        </div>
        <Button type="button" onClick={() => setDialogOpen(true)}>
          Edit customer
        </Button>
      </div>

      <div className="grid gap-4 rounded-xl border border-border bg-card p-4 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Phone</p>
          <p className="text-sm">{customer.phone ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Email</p>
          <p className="text-sm">{customer.email ?? "—"}</p>
        </div>
        {customer.notes ? (
          <div className="sm:col-span-2">
            <p className="text-xs uppercase text-muted-foreground">Notes</p>
            <p className="whitespace-pre-wrap text-sm">{customer.notes}</p>
          </div>
        ) : null}
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Recent purchases</h2>
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[480px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Sale #</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {sales.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                    No purchases yet.
                  </td>
                </tr>
              ) : (
                sales.map((sale) => (
                  <tr key={sale.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2">
                      <Link
                        to={`/sales/${sale.id}`}
                        className="font-mono text-xs font-medium text-emerald-600 hover:underline dark:text-emerald-400"
                      >
                        #{sale.id}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {new Date(sale.created_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-2">{sale.item_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(sale.total)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {sales.length > 0 ? (
          <p className="text-xs text-muted-foreground">Showing last {sales.length} sales.</p>
        ) : null}
      </section>

      <CustomerFormDialog
        open={dialogOpen}
        customer={customer}
        onClose={() => setDialogOpen(false)}
      />
    </div>
  )
}
