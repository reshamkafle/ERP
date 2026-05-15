import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Link, Navigate } from "react-router-dom"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { CustomerFormDialog } from "@/features/customers/CustomerFormDialog"
import { deleteCustomer, fetchCustomers } from "@/features/customers/customers-api"
import { useAuth } from "@/context/AuthContext"
import type { Customer } from "@/types/customer"

export function CustomersPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Customer | null>(null)

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

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
  const isAdmin = user?.role === "ADMIN"

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Customers</h1>
          <p className="text-sm text-muted-foreground">
            Basic CRM — contact details, notes, and purchase history.
          </p>
        </div>
        <Button
          type="button"
          onClick={() => {
            setEditing(null)
            setDialogOpen(true)
          }}
        >
          Add customer
        </Button>
      </div>

      <div className="rounded-xl border border-border bg-card p-4">
        <Input
          placeholder="Search by name, phone, or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Phone</th>
              <th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listQuery.isLoading ? (
              <tr>
                <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                  Loading customers…
                </td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-3 py-8 text-center text-muted-foreground">
                  No customers found. Add your first customer.
                </td>
              </tr>
            ) : (
              customers.map((customer) => (
                <tr key={customer.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2">
                    <Link
                      to={`/customers/${customer.id}`}
                      className="font-medium text-emerald-600 hover:underline dark:text-emerald-400"
                    >
                      {customer.name}
                    </Link>
                  </td>
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
                    {isAdmin ? (
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
  )
}