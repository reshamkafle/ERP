import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate, useParams } from "react-router-dom"

import { ContentSheet } from "@/components/ContentSheet"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SupplierFormDialog } from "@/features/suppliers/SupplierFormDialog"
import { fetchSupplier } from "@/features/suppliers/suppliers-api"
import { formatMoney } from "@/lib/format-money"
import type { SupplierDetail } from "@/types/supplier"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"

function approvalVariant(
  status: string | null,
): "default" | "secondary" | "success" | "warning" | "danger" {
  if (!status) return "secondary"
  const s = status.toUpperCase()
  if (s === "PREFERRED" || s === "APPROVED") return "success"
  if (s === "PENDING") return "warning"
  if (s === "BLACKLISTED") return "danger"
  return "default"
}

export function SupplierDetailPage() {
  const { id } = useParams<{ id: string }>()
    const [dialogOpen, setDialogOpen] = useState(false)
  const supplierId = Number(id)

  const detailQuery = useQuery({
    queryKey: ["suppliers", "detail", supplierId],
    queryFn: () => fetchSupplier(supplierId),
    enabled: Number.isFinite(supplierId) && supplierId > 0,
  })

  if (!Number.isFinite(supplierId) || supplierId <= 0) {
    return <Navigate to="/suppliers" replace />
  }

  if (detailQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading vendor…</p>
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-destructive">Vendor not found.</p>
        <Link to="/suppliers" className="text-sm text-primary hover:underline">
          Back to vendors
        </Link>
      </div>
    )
  }

  const supplier = detailQuery.data

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <DetailHeader supplier={supplier} onEdit={() => setDialogOpen(true)} />

      <ContentSheet className="space-y-6 p-4">
        <DetailSection title="Identity">
          <DetailGrid
            rows={[
              ["Vendor code", supplier.vendor_code],
              ["Legal name", supplier.legal_name],
              ["DBA", supplier.dba],
            ]}
          />
        </DetailSection>

        <DetailSection title="Contact">
          <DetailGrid
            rows={[
              ["Address", formatAddress(supplier)],
              ["Phone", supplier.phone],
              ["Email", supplier.email],
              ["Website", supplier.website],
            ]}
          />
        </DetailSection>

        <DetailSection title="Tax & terms">
          <DetailGrid
            rows={[
              ["Tax ID", supplier.tax_id],
              ["Payment terms", supplier.payment_terms],
              ["Incoterms", supplier.incoterms],
            ]}
          />
        </DetailSection>

        <DetailSection title="Bank details">
          <DetailGrid
            rows={[
              ["Account", supplier.bank_details?.account_number],
              ["Beneficiary", supplier.bank_details?.beneficiary_name],
              ["IFSC", supplier.bank_details?.ifsc],
              ["SWIFT", supplier.bank_details?.swift],
            ]}
          />
        </DetailSection>

        <DetailSection title="Classification">
          <DetailGrid
            rows={[
              ["Category", supplier.vendor_category],
              ["Type", supplier.vendor_type],
              [
                "Approval",
                supplier.approval_status ? (
                  <Badge variant={approvalVariant(supplier.approval_status)}>
                    {supplier.approval_status}
                  </Badge>
                ) : null,
              ],
              [
                "Performance rating",
                supplier.performance_rating != null
                  ? String(supplier.performance_rating)
                  : null,
              ],
            ]}
          />
        </DetailSection>

        <DetailSection title="Operations">
          <DetailGrid
            rows={[
              ["Lead time (days)", supplier.lead_time_days?.toString()],
              ["MOQ", supplier.moq != null ? String(supplier.moq) : null],
              ["Currency", supplier.currency_code],
              ["Pricing currency", supplier.pricing_currency],
            ]}
          />
        </DetailSection>

        {(supplier.documents?.w9 ||
          supplier.documents?.certificate_of_incorporation ||
          supplier.documents?.insurance ||
          supplier.documents?.other) && (
          <DetailSection title="Documents">
            <DetailGrid
              rows={[
                ["W9", supplier.documents?.w9],
                ["Incorporation", supplier.documents?.certificate_of_incorporation],
                ["Insurance", supplier.documents?.insurance],
                ["Other", supplier.documents?.other],
              ]}
            />
          </DetailSection>
        )}
      </ContentSheet>

      <ContentSheet className="space-y-3">
        <h2 className="text-lg font-semibold text-foreground">Recent purchases (quick receive)</h2>
        <div className="overflow-x-auto rounded-md border border-border">
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
              {supplier.recent_purchases.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                    No purchases yet.
                  </td>
                </tr>
              ) : (
                supplier.recent_purchases.map((purchase) => (
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
      </ContentSheet>

      <SupplierFormDialog
        open={dialogOpen}
        supplier={supplier}
        onClose={() => setDialogOpen(false)}
      />
    </div>
    </PosOnlyRedirect>
  )
}

function DetailHeader({
  supplier,
  onEdit,
}: {
  supplier: SupplierDetail
  onEdit: () => void
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <Link
          to="/suppliers"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← Vendors
        </Link>
        <h1 className="mt-2 text-xl font-semibold text-foreground">{supplier.name}</h1>
        <p className="font-mono text-sm text-muted-foreground">{supplier.vendor_code}</p>
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
          Quick receive
        </Link>
        <Button type="button" onClick={onEdit}>
          Edit vendor
        </Button>
      </div>
    </div>
  )
}

function DetailSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="text-sm font-semibold">{title}</h3>
      <div className="mt-2">{children}</div>
    </section>
  )
}

function DetailGrid({
  rows,
}: {
  rows: [string, React.ReactNode | string | number | null | undefined][]
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {rows.map(([label, value]) => (
        <div key={label}>
          <p className="text-xs uppercase text-muted-foreground">{label}</p>
          <p className="text-sm">
            {value == null || value === "" ? "—" : typeof value === "string" ? value : value}
          </p>
        </div>
      ))}
    </div>
  )
}

function formatAddress(supplier: SupplierDetail): string | null {
  const parts = [
    supplier.address_line1,
    supplier.address_line2,
    [supplier.city, supplier.state, supplier.postal_code].filter(Boolean).join(", "),
    supplier.country,
  ].filter(Boolean)
  return parts.length ? parts.join("\n") : null
}