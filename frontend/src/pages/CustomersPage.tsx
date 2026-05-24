import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { PosOnlyRedirect } from "@/components/PosOnlyRedirect"
import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { ControlPanel } from "@/components/ui/control-panel"
import { Input } from "@/components/ui/input"
import { CustomerFormDialog } from "@/features/customers/CustomerFormDialog"
import { deleteCustomer, fetchCustomers } from "@/features/customers/customers-api"
import { useAuth } from "@/context/AuthContext"
import { canDeleteCustomers } from "@/lib/permissions"
import type { Customer } from "@/types/customer"

export function CustomersPage() {
  const { permissions } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Customer | null>(null)

  const listQuery = useQuery({
    queryKey: ["customers", "list", search],
    queryFn: () => fetchCustomers({ search: search || undefined, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCustomer,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["customers"] })
      toast.success("Customer deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete customer"
      toast.error(typeof detail === "string" ? detail : "Could not delete customer")
    },
  })

  const customers = listQuery.data?.items ?? []
  const canDelete = canDeleteCustomers(permissions)

  return (
    <PosOnlyRedirect>
    <div className="space-y-4">
      <PageHeader
        title="Customers"
        description="Customer master data — profiles, credit, tax, and 360° view."
        actions={
          <Button
            type="button"
            onClick={() => {
              setEditing(null)
              setDialogOpen(true)
            }}
          >
            Add customer
          </Button>
        }
      />

      <ControlPanel>
        <Input
          className="max-w-md"
          placeholder="Search by name, phone, or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </ControlPanel>

      <ContentSheet className="p-0 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[800px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Code</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Segment</th>
              <th className="px-3 py-2 font-medium">Group</th>
              <th className="px-3 py-2 font-medium">Phone</th>
              <th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listQuery.isLoading ? (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                  Loading customers…
                </td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                  No customers found. Add your first customer.
                </td>
              </tr>
            ) : (
              customers.map((customer) => (
                <tr key={customer.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2">
                    <Link
                      to={`/customers/${customer.id}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {customer.name}
                    </Link>
                  </td>
                  <td className="px-3 py-2 font-mono text-xs text-muted-foreground">
                    {customer.customer_code ?? "—"}
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">{customer.status ?? "—"}</td>
                  <td className="px-3 py-2 text-muted-foreground">{customer.segment ?? "—"}</td>
                  <td className="px-3 py-2 text-muted-foreground">{customer.customer_group ?? "—"}</td>
                  <td className="px-3 py-2 text-muted-foreground">{customer.phone ?? "—"}</td>
                  <td className="px-3 py-2 text-muted-foreground">{customer.email ?? "—"}</td>
                  <td className="px-3 py-2 text-right">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setEditing(customer)
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
                        disabled={deleteMutation.isPending}
                        onClick={() => {
                          if (window.confirm(`Delete ${customer.name}?`)) {
                            deleteMutation.mutate(customer.id)
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
        <p className="text-sm text-destructive">Could not load customers. Try again shortly.</p>
      ) : null}

      <CustomerFormDialog
        open={dialogOpen}
        customer={editing}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </div>
    </PosOnlyRedirect>
  )
}