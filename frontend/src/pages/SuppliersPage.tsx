import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate } from "react-router-dom"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SupplierFormDialog } from "@/features/suppliers/SupplierFormDialog"
import { deleteSupplier, fetchSuppliers } from "@/features/suppliers/suppliers-api"
import { useAuth } from "@/context/AuthContext"
import { formatMoney } from "@/lib/format-money"
import type { Supplier } from "@/types/supplier"

export function SuppliersPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const listQuery = useQuery({
    queryKey: ["suppliers", "list", search],
    queryFn: () => fetchSuppliers({ search: search || undefined, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      toast.success("Supplier deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete supplier"
      toast.error(typeof detail === "string" ? detail : "Could not delete supplier")
    },
  })

  const suppliers = listQuery.data?.items ?? []
  const isAdmin = user?.role === "ADMIN"

  return (
    <div className="space-y-6">
      <PageHeader
        title="Suppliers"
        description="Vendors you buy from — contact details and total spend."
        action={
          <div className="flex gap-2">
            <Link
              to="/purchases"
              className="inline-flex h-8 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium hover:bg-muted"
            >
              Record purchase
            </Link>
            <Button
              type="button"
              onClick={() => {
                setEditing(null)
                setDialogOpen(true)
              }}
            >
              Add supplier
            </Button>
          </div>
        }
      />

      <div className="rounded-xl border border-border bg-card p-4">
        <Input
          placeholder="Search by name, phone, or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Phone</th>
              <th className="px-3 py-2 font-medium">Purchases</th>
              <th className="px-3 py-2 font-medium text-right">Total spent</th>
              <th className="px-3 py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listQuery.isLoading ? (
              <tr>
                <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                  Loading suppliers…
                </td>
              </tr>
            ) : suppliers.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                  No suppliers found. Add your first supplier.
                </td>
              </tr>
            ) : (
              suppliers.map((supplier) => (
                <tr key={supplier.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2">
                    <Link
                      to={`/suppliers/${supplier.id}`}
                      className="font-medium text-emerald-600 hover:underline dark:text-emerald-400"
                    >
                      {supplier.name}
                    </Link>
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">{supplier.phone ?? "—"}</td>
                  <td className="px-3 py-2 tabular-nums">{supplier.purchase_count}</td>
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
                    {isAdmin ? (
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
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

      {listQuery.isError ? (
        <p className="text-sm text-destructive">Could not load suppliers. Try again shortly.</p>
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
  )
}

function PageHeader({
  title,
  description,
  action,
}: {
  title: string
  description: string
  action: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </div>
  )
}
