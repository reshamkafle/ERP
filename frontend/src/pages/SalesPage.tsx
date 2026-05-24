import { useQuery } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { Link } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { useAuth } from "@/context/AuthContext"
import { canAccess, canLinkCustomers as canLinkCustomersPerm } from "@/lib/permissions"
import { SaleOrderFormDialog } from "@/features/sales/SaleOrderFormDialog"
import { fetchSales } from "@/features/sales/sales-api"
import { formatMoney } from "@/lib/format-money"

export function SalesPage() {
  const { permissions } = useAuth()
  const [searchParams] = useSearchParams()
  const deliveryFilter = searchParams.get("delivery_filter")
  const [orderNumberFilter, setOrderNumberFilter] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [formOpen, setFormOpen] = useState(false)
  const canWrite = canAccess(permissions, "sales.orders.write")
  const canLinkCustomers = canLinkCustomersPerm(permissions)

  const listQuery = useQuery({
    queryKey: ["sales", "list", orderNumberFilter, statusFilter],
    queryFn: () =>
      fetchSales({
        limit: 100,
        order_number: orderNumberFilter.trim() || undefined,
        order_status: statusFilter || undefined,
      }),
  })

  const sales = useMemo(() => {
    const items = listQuery.data?.items ?? []
    if (deliveryFilter !== "open") return items
    return items.filter(
      (s) => s.delivery_status && s.delivery_status !== "COMPLETE",
    )
  }, [listQuery.data?.items, deliveryFilter])

  return (
    <div className="space-y-4">
      <PageHeader
        title="Sales orders"
        description="Order management — create drafts, confirm, and track fulfillment."
        actions={
          <div className="flex flex-wrap gap-2">
            {canWrite ? (
              <Button type="button" onClick={() => setFormOpen(true)} data-testid="new-sales-order">
                New sales order
              </Button>
            ) : null}
            <Link to="/pos" className="text-sm text-primary hover:underline self-center">
              Open POS →
            </Link>
          </div>
        }
      />

      <ControlPanel className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="max-w-xs space-y-1">
          <label htmlFor="order-number-filter" className="text-xs font-medium text-muted-foreground">
            Order number
          </label>
          <Input
            id="order-number-filter"
            placeholder="SO-2026-"
            value={orderNumberFilter}
            onChange={(e) => setOrderNumberFilter(e.target.value)}
          />
        </div>
        <div className="max-w-xs space-y-1">
          <label htmlFor="status-filter" className="text-xs font-medium text-muted-foreground">
            Status
          </label>
          <Select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All</option>
            <option value="DRAFT">Draft</option>
            <option value="CREATED">Created</option>
            <option value="RELEASED">Released</option>
            <option value="IN_PROCESS">In process</option>
            <option value="DELIVERED">Delivered</option>
            <option value="INVOICED">Invoiced</option>
            <option value="CLOSED">Closed</option>
            <option value="CANCELLED">Cancelled</option>
          </Select>
        </div>
        {listQuery.data ? (
          <p className="text-sm text-muted-foreground sm:pb-2">
            {sales.length} of {listQuery.data.total} orders
          </p>
        ) : null}
      </ControlPanel>

      <ContentSheet className="space-y-3 p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Order #</th>
                <th className="px-3 py-2 font-medium">Status</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Delivery</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2 font-medium">Customer</th>
                <th className="px-3 py-2 font-medium">Payment</th>
                <th className="px-3 py-2 font-medium">Items</th>
                <th className="px-3 py-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {listQuery.isLoading ? (
                <tr>
                  <td colSpan={9} className="px-3 py-8 text-center text-muted-foreground">
                    Loading sales…
                  </td>
                </tr>
              ) : sales.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-3 py-8 text-center text-muted-foreground">
                    No sales orders yet.
                  </td>
                </tr>
              ) : (
                sales.map((sale) => (
                  <tr key={sale.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2">
                      <Link
                        to={`/sales/${sale.id}`}
                        className="font-mono text-xs font-medium text-primary hover:underline"
                      >
                        {sale.order_number}
                      </Link>
                    </td>
                    <td className="px-3 py-2">
                      <Badge variant="outline">{sale.order_status}</Badge>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{sale.order_type}</td>
                    <td className="px-3 py-2 text-muted-foreground">{sale.delivery_status ?? "—"}</td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {sale.order_date}
                    </td>
                    <td className="px-3 py-2">
                      {sale.customer_id && sale.customer_name ? (
                        canLinkCustomers ? (
                          <Link
                            to={`/customers/${sale.customer_id}`}
                            className="text-primary hover:underline"
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
                    <td className="px-3 py-2 text-muted-foreground">{sale.payment_status}</td>
                    <td className="px-3 py-2 tabular-nums">{sale.item_count}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(sale.total)} {sale.currency_code}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {listQuery.isError ? (
          <p className="p-4 text-sm text-destructive">Could not load sales.</p>
        ) : null}
      </ContentSheet>

      {formOpen ? (
        <SaleOrderFormDialog open={formOpen} sale={null} onClose={() => setFormOpen(false)} />
      ) : null}
    </div>
  )
}
