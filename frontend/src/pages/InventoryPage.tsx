import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useMemo, useState } from "react"
import { Navigate } from "react-router-dom"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { InventoryFormDialog } from "@/features/inventory/InventoryFormDialog"
import { deleteInventoryItem, fetchCategories, fetchInventory } from "@/features/inventory/inventory-api"
import { useAuth } from "@/context/AuthContext"
import type { InventoryItem, ItemLifecycleStatus, ItemType } from "@/types/inventory"

function statusBadgeVariant(status: ItemLifecycleStatus) {
  if (status === "ACTIVE") return "success" as const
  if (status === "INACTIVE") return "secondary" as const
  if (status === "DISCONTINUED") return "warning" as const
  return "danger" as const
}

export function InventoryPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [categoryId, setCategoryId] = useState("")
  const [itemType, setItemType] = useState<ItemType | "">("")
  const [lifecycleStatus, setLifecycleStatus] = useState<ItemLifecycleStatus | "">("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<InventoryItem | null>(null)

  if (user?.role === "CASHIER") {
    return <Navigate to="/pos" replace />
  }

  const categoriesQuery = useQuery({
    queryKey: ["inventory", "categories"],
    queryFn: fetchCategories,
  })

  const listQuery = useQuery({
    queryKey: ["inventory", "list", search, categoryId, itemType, lifecycleStatus],
    queryFn: () =>
      fetchInventory({
        search: search || undefined,
        category_id: categoryId ? Number(categoryId) : undefined,
        item_type: itemType || undefined,
        lifecycle_status: lifecycleStatus || undefined,
        limit: 100,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteInventoryItem,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      toast.success("Item deleted")
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not delete item"
      toast.error(typeof detail === "string" ? detail : "Could not delete item")
    },
  })

  const items = listQuery.data?.items ?? []
  const categories = categoriesQuery.data ?? []
  const isAdmin = user?.role === "ADMIN"

  const lowStockIds = useMemo(
    () =>
      new Set(
        items
          .filter((i) => i.stock < i.low_stock_threshold)
          .map((i) => i.id),
      ),
    [items],
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Inventory</h1>
          <p className="text-sm text-muted-foreground">
            Manage item master data — SKU, classification, UOM, compliance, and status.
          </p>
        </div>
        <Button
          type="button"
          onClick={() => {
            setEditing(null)
            setDialogOpen(true)
          }}
        >
          Add item
        </Button>
      </div>

      <div className="grid gap-3 rounded-xl border border-border bg-card p-4 sm:grid-cols-2 lg:grid-cols-4">
        <Input
          placeholder="Search SKU, name, barcode…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </Select>
        <Select value={itemType} onChange={(e) => setItemType(e.target.value as ItemType | "")}>
          <option value="">All types</option>
          <option value="RAW">Raw</option>
          <option value="FINISHED">Finished</option>
          <option value="TRADING">Trading</option>
          <option value="SERVICE">Service</option>
          <option value="ASSET">Asset</option>
        </Select>
        <Select
          value={lifecycleStatus}
          onChange={(e) => setLifecycleStatus(e.target.value as ItemLifecycleStatus | "")}
        >
          <option value="">All statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
          <option value="DISCONTINUED">Discontinued</option>
          <option value="OBSOLETE">Obsolete</option>
        </Select>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-3 py-2 font-medium">SKU</th>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Category</th>
              <th className="px-3 py-2 font-medium">Type</th>
              <th className="px-3 py-2 font-medium">UOM</th>
              <th className="px-3 py-2 font-medium">Stock</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {listQuery.isLoading ? (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                  Loading items…
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                  No items found. Create your first inventory item.
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id} className="border-b border-border last:border-0">
                  <td className="px-3 py-2 font-mono text-xs">{item.sku}</td>
                  <td className="px-3 py-2">
                    <div className="font-medium">{item.name}</div>
                    {item.barcode ? (
                      <p className="text-xs text-muted-foreground">{item.barcode}</p>
                    ) : null}
                  </td>
                  <td className="px-3 py-2 text-muted-foreground">
                    {item.category?.name ?? "—"}
                  </td>
                  <td className="px-3 py-2">{item.item_type}</td>
                  <td className="px-3 py-2">{item.primary_uom}</td>
                  <td className="px-3 py-2">
                    <span className={lowStockIds.has(item.id) ? "font-semibold text-destructive" : ""}>
                      {item.stock}
                    </span>
                    {lowStockIds.has(item.id) ? (
                      <Badge variant="danger" className="ml-2">
                        Low
                      </Badge>
                    ) : null}
                  </td>
                  <td className="px-3 py-2">
                    <Badge variant={statusBadgeVariant(item.lifecycle_status)}>
                      {item.lifecycle_status}
                    </Badge>
                  </td>
                  <td className="px-3 py-2 text-right">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setEditing(item)
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
                          if (window.confirm(`Delete ${item.sku}?`)) {
                            deleteMutation.mutate(item.id)
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
        <p className="text-sm text-destructive">Could not load inventory. Try again shortly.</p>
      ) : null}

      <InventoryFormDialog
        open={dialogOpen}
        item={editing}
        categories={categories}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </div>
  )
}
