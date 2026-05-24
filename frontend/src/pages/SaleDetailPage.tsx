import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { canAccess, canLinkCustomers as canLinkCustomersPerm } from "@/lib/permissions"
import { ReceiptDialog } from "@/features/pos/ReceiptDialog"
import { SaleOrderFormDialog } from "@/features/sales/SaleOrderFormDialog"
import {
  cancelSaleOrder,
  confirmSaleOrder,
  fetchSale,
  runAtpCheck,
  runCreditCheck,
} from "@/features/sales/sales-api"
import { formatMoney } from "@/lib/format-money"

export function SaleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [receiptOpen, setReceiptOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const saleId = Number(id)
  const canWrite = canAccess(permissions, "sales.orders.write")
  const canLinkCustomers = canLinkCustomersPerm(permissions)

  const detailQuery = useQuery({
    queryKey: ["sales", "detail", saleId],
    queryFn: () => fetchSale(saleId),
    enabled: Number.isFinite(saleId) && saleId > 0,
  })

  const confirmMutation = useMutation({
    mutationFn: () => confirmSaleOrder(saleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales"] })
      toast.success("Order confirmed")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Confirm failed"
      toast.error(typeof detail === "string" ? detail : "Confirm failed")
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => cancelSaleOrder(saleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales"] })
      toast.success("Order cancelled")
    },
  })

  const creditMutation = useMutation({
    mutationFn: () => runCreditCheck(saleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales", "detail", saleId] })
      toast.success("Credit check completed")
    },
  })

  const atpMutation = useMutation({
    mutationFn: () => runAtpCheck(saleId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales", "detail", saleId] })
      toast.success("ATP check completed")
    },
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
        <Link to="/sales" className="text-sm text-primary hover:underline">
          Back to sales
        </Link>
      </div>
    )
  }

  const sale = detailQuery.data
  const isDraft = sale.order_status === "DRAFT"

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/sales" className="text-sm text-muted-foreground hover:text-foreground">
            ← Sales orders
          </Link>
          <h1 className="mt-2 text-xl font-semibold text-foreground">{sale.order_number}</h1>
          <div className="mt-1 flex flex-wrap gap-2">
            <Badge>{sale.order_status}</Badge>
            <Badge variant="outline">{sale.payment_status}</Badge>
            <Badge variant="outline">Credit: {sale.credit_check_status}</Badge>
            <Badge variant="outline">ATP: {sale.atp_check_status}</Badge>
            {sale.delivery_status ? <Badge variant="outline">Delivery: {sale.delivery_status}</Badge> : null}
            {sale.invoice_status ? <Badge variant="outline">Billing: {sale.invoice_status}</Badge> : null}
          </div>
          <p className="text-sm text-muted-foreground">
            Order date {sale.order_date}
            {sale.requested_delivery_date ? ` · Req. delivery ${sale.requested_delivery_date}` : ""}
            · Created {new Date(sale.created_at).toLocaleString()}
            {sale.updated_at ? ` · Updated ${new Date(sale.updated_at).toLocaleString()}` : ""}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {canWrite && isDraft ? (
            <Button type="button" variant="outline" onClick={() => setEditOpen(true)}>
              Edit draft
            </Button>
          ) : null}
          {canWrite && isDraft ? (
            <Button type="button" onClick={() => confirmMutation.mutate()} disabled={confirmMutation.isPending}>
              Confirm order
            </Button>
          ) : null}
          {canWrite && sale.order_status !== "CANCELLED" ? (
            <Button
              type="button"
              variant="destructive"
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
            >
              Cancel
            </Button>
          ) : null}
          {canWrite ? (
            <>
              <Button type="button" variant="outline" size="sm" onClick={() => creditMutation.mutate()}>
                Credit check
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => atpMutation.mutate()}>
                ATP check
              </Button>
            </>
          ) : null}
          <Button type="button" variant="outline" onClick={() => setReceiptOpen(true)}>
            View receipt
          </Button>
        </div>
      </div>

      <ContentSheet>
        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-4">
          <DetailField label="Customer (sold-to)" value={sale.customer_name ?? "Walk-in"} link={sale.customer_id ? `/customers/${sale.customer_id}` : undefined} canLink={canLinkCustomers} />
          <DetailField label="Sales org / channel" value={[sale.sales_organization, sale.distribution_channel, sale.division].filter(Boolean).join(" / ") || "—"} />
          <DetailField label="Order type" value={`${sale.order_type}${sale.sales_channel ? ` · ${sale.sales_channel}` : ""}`} />
          <DetailField label="Salesperson" value={sale.salesperson_email ?? "—"} />
          <DetailField label="Payment terms" value={sale.payment_terms ?? "—"} />
          <DetailField label="PO reference" value={sale.customer_po_number ? `${sale.customer_po_number}${sale.customer_po_date ? ` (${sale.customer_po_date})` : ""}` : "—"} />
          <DetailField label="Incoterms" value={[sale.incoterms, sale.incoterms_location].filter(Boolean).join(" ") || "—"} />
          <DetailField label="Shipping" value={[sale.shipping_method, sale.shipping_conditions].filter(Boolean).join(" · ") || "—"} />
          <DetailField label="Warehouse" value={sale.warehouse_name ?? "—"} />
          <DetailField label="Shipping point" value={sale.shipping_point_name ?? "—"} />
          <DetailField label="Pricing" value={[sale.price_list_code, sale.pricing_procedure].filter(Boolean).join(" · ") || "—"} />
          <DetailField label="Campaign / opportunity" value={[sale.campaign_id, sale.opportunity_id ? `Opp #${sale.opportunity_id}` : null].filter(Boolean).join(" · ") || "—"} />
          <DetailField label="Created by" value={sale.cashier_email ?? "—"} />
          <DetailField label="Changed by" value={sale.updated_by_email ?? "—"} />
        </div>
      </ContentSheet>

      {sale.partners?.length ? (
        <ContentSheet className="space-y-2">
          <h2 className="text-lg font-semibold text-foreground">Partner functions</h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {sale.partners.map((p) => (
              <div key={p.id} className="rounded border border-border px-3 py-2 text-sm">
                <p className="text-xs uppercase text-muted-foreground">{p.role.replace(/_/g, " ")}</p>
                <p className="font-medium">
                  {p.customer_name ?? p.user_email ?? p.name_override ?? p.supplier_name ?? "—"}
                </p>
              </div>
            ))}
          </div>
        </ContentSheet>
      ) : null}

      {sale.summary ? (
        <ContentSheet>
          <h2 className="mb-3 text-lg font-semibold text-foreground">Order summary</h2>
          <div className="grid gap-3 sm:grid-cols-4">
            <DetailField label="Total items" value={String(sale.summary.total_items)} />
            <DetailField label="Total quantity" value={String(sale.summary.total_quantity)} />
            <DetailField label="Net value" value={formatMoney(sale.summary.total_net, sale.currency_code)} />
            <DetailField label="Tax" value={formatMoney(sale.summary.total_tax, sale.currency_code)} />
            <DetailField label="Discount" value={formatMoney(sale.summary.total_discount, sale.currency_code)} />
            <DetailField label="Freight" value={formatMoney(sale.summary.freight, sale.currency_code)} />
            <DetailField label="Grand total" value={formatMoney(sale.summary.grand_total, sale.currency_code)} />
          </div>
        </ContentSheet>
      ) : null}

      <ContentSheet className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Line items</h2>
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="w-full min-w-[1100px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">#</th>
                <th className="px-3 py-2 font-medium">SKU</th>
                <th className="px-3 py-2 font-medium">Description</th>
                <th className="px-3 py-2 font-medium text-right">Qty</th>
                <th className="px-3 py-2 font-medium">UoM</th>
                <th className="px-3 py-2 font-medium text-right">Unit</th>
                <th className="px-3 py-2 font-medium text-right">Net</th>
                <th className="px-3 py-2 font-medium text-right">Tax</th>
                <th className="px-3 py-2 font-medium text-right">Line total</th>
                <th className="px-3 py-2 font-medium">Plant</th>
                <th className="px-3 py-2 font-medium">Batch / serial</th>
                <th className="px-3 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {sale.items.map((item) => (
                <tr key={item.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2">{item.line_number}</td>
                  <td className="px-3 py-2 font-mono text-xs">{item.product_sku}</td>
                  <td className="px-3 py-2 font-medium">{item.description ?? item.product_name}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{item.quantity}</td>
                  <td className="px-3 py-2 text-muted-foreground">{item.uom ?? "—"}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{formatMoney(item.unit_price)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{formatMoney(item.net_amount)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{formatMoney(item.tax_amount)}</td>
                  <td className="px-3 py-2 text-right tabular-nums font-medium">
                    {formatMoney(item.line_total)}
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">{item.warehouse_name ?? "—"}</td>
                  <td className="px-3 py-2 text-xs text-muted-foreground">
                    {[item.batch_number, item.serial_number].filter(Boolean).join(" / ") || "—"}
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">{item.line_status}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t border-border bg-muted/30">
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right text-muted-foreground">Gross</td>
                <td className="px-3 py-2 text-right tabular-nums">{formatMoney(sale.gross_total)}</td>
                <td colSpan={3} />
              </tr>
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right text-muted-foreground">Header discount</td>
                <td className="px-3 py-2 text-right tabular-nums">-{formatMoney(sale.header_discount_amount)}</td>
                <td colSpan={3} />
              </tr>
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right text-muted-foreground">Subtotal</td>
                <td className="px-3 py-2 text-right tabular-nums">{formatMoney(sale.subtotal)}</td>
                <td colSpan={3} />
              </tr>
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right text-muted-foreground">Tax</td>
                <td className="px-3 py-2 text-right tabular-nums">{formatMoney(sale.tax)}</td>
                <td colSpan={3} />
              </tr>
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right text-muted-foreground">Freight / other</td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatMoney(
                    Number(sale.freight_amount) + Number(sale.insurance_amount) + Number(sale.handling_amount),
                  )}
                </td>
                <td colSpan={3} />
              </tr>
              <tr>
                <td colSpan={8} className="px-3 py-2 text-right font-semibold">Grand total</td>
                <td className="px-3 py-2 text-right tabular-nums font-semibold text-primary">
                  {formatMoney(sale.total)} {sale.currency_code}
                </td>
                <td colSpan={3} />
              </tr>
            </tfoot>
          </table>
        </div>
      </ContentSheet>

      {receiptOpen ? <ReceiptDialog sale={sale} onClose={() => setReceiptOpen(false)} /> : null}
      {editOpen ? (
        <SaleOrderFormDialog open={editOpen} sale={sale} onClose={() => setEditOpen(false)} />
      ) : null}
    </div>
  )
}

function DetailField({
  label,
  value,
  link,
  canLink,
}: {
  label: string
  value: string
  link?: string
  canLink?: boolean
}) {
  return (
    <div>
      <p className="text-xs uppercase text-muted-foreground">{label}</p>
      <p className="text-sm">
        {link && canLink ? (
          <Link to={link} className="text-primary hover:underline">
            {value}
          </Link>
        ) : (
          value
        )}
      </p>
    </div>
  )
}
