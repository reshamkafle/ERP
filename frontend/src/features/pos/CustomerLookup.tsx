import { useQuery } from "@tanstack/react-query"
import { User, X } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { fetchCustomers } from "@/features/customers/customers-api"
import { useCartStore, type SelectedCustomer } from "@/features/pos/cart-store"
import { useDebouncedValue } from "@/features/pos/useDebouncedValue"
import type { Customer } from "@/types/customer"

function toSelected(customer: Customer): SelectedCustomer {
  return { id: customer.id, name: customer.name, phone: customer.phone }
}

export function CustomerLookup() {
  const selected = useCartStore((s) => s.selectedCustomer)
  const setSelectedCustomer = useCartStore((s) => s.setSelectedCustomer)
  const [search, setSearch] = useState("")
  const debouncedSearch = useDebouncedValue(search, 300)

  const lookupQuery = useQuery({
    queryKey: ["customers", "pos-lookup", debouncedSearch],
    queryFn: () =>
      fetchCustomers({ search: debouncedSearch || undefined, limit: 8 }),
    enabled: debouncedSearch.trim().length >= 2,
  })

  const results = lookupQuery.data?.items ?? []

  if (selected) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50/80 p-3 dark:border-emerald-900 dark:bg-emerald-950/40">
        <div className="flex items-start justify-between gap-2">
          <div className="flex min-w-0 items-center gap-2">
            <User className="size-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-foreground">{selected.name}</p>
              {selected.phone ? (
                <p className="truncate text-xs text-muted-foreground">{selected.phone}</p>
              ) : null}
            </div>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={() => setSelectedCustomer(null)}
            aria-label="Remove customer"
          >
            <X className="size-4" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-muted-foreground">Customer (optional)</label>
      <Input
        placeholder="Search phone or name…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {debouncedSearch.trim().length >= 2 ? (
        <ul className="max-h-36 overflow-y-auto rounded-md border border-border bg-background text-sm">
          {lookupQuery.isLoading ? (
            <li className="px-3 py-2 text-muted-foreground">Searching…</li>
          ) : results.length === 0 ? (
            <li className="px-3 py-2 text-muted-foreground">No customers found</li>
          ) : (
            results.map((customer) => (
              <li key={customer.id}>
                <button
                  type="button"
                  className="flex w-full flex-col px-3 py-2 text-left hover:bg-muted"
                  onClick={() => {
                    setSelectedCustomer(toSelected(customer))
                    setSearch("")
                  }}
                >
                  <span className="font-medium">{customer.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {[customer.phone, customer.email].filter(Boolean).join(" · ") || "No contact info"}
                  </span>
                </button>
              </li>
            ))
          )}
        </ul>
      ) : null}
    </div>
  )
}