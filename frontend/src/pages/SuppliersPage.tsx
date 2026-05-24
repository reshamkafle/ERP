import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { SupplierFormDialog } from "@/features/suppliers/SupplierFormDialog"
import { deleteSupplier, fetchSuppliers } from "@/features/suppliers/suppliers-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"
import { cn } from "@/lib/utils"
import type { Supplier } from "@/types/supplier"
import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"
import { canDeleteSuppliers } from "@/lib/permissions"

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

export function SuppliersPage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)

  const listQuery = useQuery({
    queryKey: ["suppliers", "list", search],
    queryFn: () => fetchSuppliers({ search: search || undefined, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      toast.success("Vendor deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete vendor"
      toast.error(typeof detail === "string" ? detail : "Could not delete vendor")
    },
  })

  const suppliers = listQuery.data?.items ?? []
  const canDelete = canDeleteSuppliers(permissions)

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Vendor master"
        description="Supplier / vendor master data — codes, terms, banking, and performance."
        actions={
          <div className="flex gap-2">
            <Link
              to="/purchases"
              className="inline-flex h-8 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium hover:bg-muted"
            >
              Quick receive
            </Link>
            <Button
              type="button"
              onClick={() => {
                setEditing(null)
                setDialogOpen(true)
              }}
            >
              Add vendor
            </Button>
          </div>
        }
      />

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder="Search code, name, category, email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[960px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Vendor code</th>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Category</th>
                <th className="px-3 py-2 font-medium">Approval</th>
                <th className="px-3 py-2 font-medium">Rating</th>
                <th className="px-3 py-2 font-medium">Currency</th>
                <th className="px-3 py-2 font-medium text-right">Total spent</th>
                <th className="px-3 py-2 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {listQuery.isLoading ? (
                <tr>
                  <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                    Loading vendors…
                  </td>
                </tr>
              ) : suppliers.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                    No vendors found. Add your first vendor.
                  </td>
                </tr>
              ) : (
                suppliers.map((supplier) => (
                  <tr key={supplier.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">{supplier.vendor_code}</td>
                    <td className="px-3 py-2">
                      <Link
                        to={`/suppliers/${supplier.id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {supplier.name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">
                      {supplier.vendor_category ?? "—"}
                    </td>
                    <td className="px-3 py-2">
                      {supplier.approval_status ? (
                        <Badge variant={approvalVariant(supplier.approval_status)}>
                          {supplier.approval_status}
                        </Badge>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-3 py-2 tabular-nums">
                      {supplier.performance_rating != null
                        ? Number(supplier.performance_rating).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">{supplier.currency_code}</td>
                    <td className="px-3 py-2 text-right tabular-nums font-medium">
                      {formatMoney(supplier.total_spent)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditing(supplier)
                          setDialogOpen(true)
                        }}
                      >
                        Edit
                      </Button>
                      {canDelete ? (
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          className={cn("ml-1")}
                          disabled={deleteMutation.isPending}
                          onClick={() => {
                            if (window.confirm(`Delete ${supplier.name}?`)) {
                              deleteMutation.mutate(supplier.id)
                            }
                          }}
                        >
                          Delete
                        </Button>
                      ) : null}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </ContentSheet>

      {listQuery.isError ? (
        <p className="text-sm text-destructive">Could not load vendors. Try again shortly.</p>
      ) : null}

      <SupplierFormDialog
        open={dialogOpen}
        supplier={editing}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </div>
    </PosOnlyRedirect>
  )
}