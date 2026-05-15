import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { ReceiptDialog } from "@/features/pos/ReceiptDialog"
import { fetchSale } from "@/features/sales/sales-api"
import { formatMoney } from "@/lib/format-money"

export function SaleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [receiptOpen, setReceiptOpen] = useState(false)
  const saleId = Number(id)
  const canLinkCustomers = user?.role === "ADMIN" || user?.role === "MANAGER"

  const detailQuery = useQuery({
    queryKey: ["sales", "detail", saleId],
    queryFn: () => fetchSale(saleId),
    enabled: Number.isFinite(saleId) && saleId > 0,
  })

  if (!Number.isFinite(saleId) || saleId <= 0) {
    return <Navigate to="/sales" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading sale…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Sale not found.</p>
        <Link to="/sales" className="text-sm text-emerald-600 hover:underline dark:text-emerald-400">
          Back to sales
        </Link>
      </div>
    )
  }

  const sale = detailQuery.data

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/sales" className="text-sm text-muted-foreground hover:text-foreground">
            ← Sales
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-foreground">Sale #{sale.id}</h1>
          <p className="text-sm text-muted-foreground">
            {new Date(sale.created_at).toLocaleString()}
          </p>
        </div>
        <Button type="button" onClick={() => setReceiptOpen(true)}>
          View receipt
        </Button>
      </div>

      <div className="grid gap-4 rounded-xl border border-border bg-card p-4 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase text-muted-foreground">Customer</p>
          <p className="text-sm">
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
              "Walk-in"
            )}
          </p>
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">Cashier</p>
          <p className="text-sm">{sale.cashier_email ?? "—"}</p>
        </div>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Line items</h2>
        <div className="overflow-x-auto rounded-xl border border-border">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Product</th>
                <th className="px-3 py-2 font-medium">SKU</th>
                <th className="px-3 py-2 font-medium text-right">Qty</th>
                <th className="px-3 py-2 font-medium text-right">Unit price</th>
                <th className="px-3 py-2 font-medium text-right">Line total</th>
              </tr>
            </thead>
            <tbody>
              {sale.items.map((item) => (
                <tr key={item.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-medium">{item.product_name}</td>
                  <td className="px-3 py-2 font-mono text-xs text-muted-foreground">
                    {item.product_sku}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">{item.quantity}</td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {formatMoney(item.price_at_sale)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums font-medium">
                    {formatMoney(item.line_total)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t border-border bg-muted/30">
              <tr>
                <td colSpan={4} className="px-3 py-2 text-right text-muted-foreground">
                  Subtotal
                </td>
                <td className="px-3 py-2 text-right tabular-nums">{formatMoney(sale.subtotal)}</td>
              </tr>
              <tr>
                <td colSpan={4} className="px-3 py-2 text-right text-muted-foreground">
                  Tax
                </td>
                <td className="px-3 py-2 text-right tabular-nums">{formatMoney(sale.tax)}</td>
              </tr>
              <tr>
                <td colSpan={4} className="px-3 py-2 text-right font-semibold">
                  Total
                </td>
                <td className="px-3 py-2 text-right tabular-nums font-semibold text-emerald-600 dark:text-emerald-400">
                  {formatMoney(sale.total)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </section>

      {receiptOpen ? (
        <ReceiptDialog sale={sale} onClose={() => setReceiptOpen(false)} />
      ) : null}
    </div>
  )
}
