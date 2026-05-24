import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { WarehouseFormDialog } from "@/features/warehouse/WarehouseFormDialog"
import { deleteWarehouse, fetchWarehouses } from "@/features/warehouse/warehouse-api"
import type { Warehouse } from "@/types/inventory"

export function WarehousesPage() {
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const [search, setSearch] = useState(() => searchParams.get("search") ?? "")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Warehouse | null>(null)

  useEffect(() => {
    setSearch(searchParams.get("search") ?? "")
  }, [searchParams])

  const query = useQuery({
    queryKey: ["warehouses", "list", search],
    queryFn: () => fetchWarehouses({ search: search || undefined, limit: 100 }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteWarehouse,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["warehouses"] })
      toast.success("Warehouse deleted")
    },
    onError: () => toast.error("Could not delete warehouse"),
  })

  const items = query.data?.items ?? []

  return (
    <>
      <PageHeader
        title="Warehouses"
        description="Warehouse master data — sites, capacity, and operations settings."
        actions={
          <Button
            onClick={() => {
              setEditing(null)
              setDialogOpen(true)
            }}
          >
            Add warehouse
          </Button>
        }
      />
      <ContentSheet>
        <div className="mb-4 max-w-sm">
          <Input
            placeholder="Search code or name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Code</th>
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Default</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((w) => (
                <tr key={w.id} className="border-b border-border/50">
                  <td className="px-3 py-2 font-mono text-xs">{w.code}</td>
                  <td className="px-3 py-2">{w.name}</td>
                  <td className="px-3 py-2">{w.warehouse_type}</td>
                  <td className="px-3 py-2">{w.status}</td>
                  <td className="px-3 py-2">{w.is_default ? "Yes" : "—"}</td>
                  <td className="px-3 py-2 text-right space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditing(w)
                        setDialogOpen(true)
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMutation.mutate(w.id)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ContentSheet>
      <WarehouseFormDialog
        open={dialogOpen}
        warehouse={editing}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </>
  )
}
