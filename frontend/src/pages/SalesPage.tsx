import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link } from "react-router-dom"

import { Input } from "@/components/ui/input"
import { useAuth } from "@/context/AuthContext"
import { fetchSales } from "@/features/sales/sales-api"
import { formatMoney } from "@/lib/format-money"

export function SalesPage() {
  const { user } = useAuth()
  const [saleIdFilter, setSaleIdFilter] = useState("")
  const canLinkCustomers = user?.role === "ADMIN" || user?.role === "MANAGER"

  const listQuery = useQuery({
    queryKey: ["sales", "list"],
    queryFn: () => fetchSales({ limit: 100 }),
  })

  const sales = listQuery.data?.items ?? []
  const filterNum = saleIdFilter.trim() ? Number(saleIdFilter.trim()) : null
  const filtered =
    filterNum !== null && Number.isFinite(filterNum) && filterNum > 0
      ? sales.filter((sale) => sale.id === filterNum)
      : sales

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Sales</h1>
          <p className="text-sm text-muted-foreground">
            POS orders — view receipts, line items, and customer details.
          </p>
        </div>
        <Link
          to="/pos"
          className="text-sm text-emerald-600 hover:underline dark:text-emerald-400"
        >
          Open POS →
        </Link>
      </header>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="max-w-xs space-y-1">
          <label htmlFor="sale-id-filter" className="text-xs font-medium text-muted-foreground">
            Filter by sale #
          </label>
          <Input
            id="sale-id-filter"
            type="number"
            min={1}
            placeholder="e.g. 42"
            value={saleIdFilter}
            onChange={(e) => setSaleIdFilter(e.target.value)}
          />
        </div>
        {listQuery.data ? (
          <p className="text-sm text-muted-foreground sm:pb-2">
            {filtered.length} of {listQuery.data.total} orders
          </p>
        ) : null}
      </div>

      <section className="space-y-3">
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Sale #</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Customer</th>
                <th className="px-3 py-2 font-medium">Cashier</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {listQuery.isLoading ? (
                <tr>
                  <td colSpan={6} className="px-3 py-8 text-center text-muted-foreground">
                    Loading sales…
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-3 py-8 text-center text-muted-foreground">
                    {sales.length === 0
                      ? "No sales yet. Complete a checkout in POS to create one."
                      : "No sale matches that number."}
                  </td>
                </tr>
              ) : (
                filtered.map((sale) => (
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
                    <td className="px-3 py-2">
                      {sale.customer_id && sale.customer_name ? (
                        canLinkCustomers ? (
                          <Link
                            to={`/customers/${sale.customer_id}`}
                            className="text-emerald-600 hover:underline dark:text-emerald-400"
                          >
                            {sale.customer_name}
                          </Link>
                        ) : (
                          sale.customer_name
                        )
                      ) : (
                        <span className="text-muted-foreground">Walk-in</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {sale.cashier_email ?? "—"}
                    </td>
                    <td className="px-3 py-2 tabular-nums">{sale.item_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(sale.total)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {listQuery.isError ? (
          <p className="text-sm text-destructive">Could not load sales.</p>
        ) : null}
      </section>
    </div>
  )
}
