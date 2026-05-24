import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { toast } from "sonner"

import { ContentSheet } from "@/components/ContentSheet"
import { PageHeader } from "@/components/PageHeader"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { LocationFormDialog } from "@/features/warehouse/LocationFormDialog"
import {
  deleteStorageLocation,
  fetchStorageLocations,
  fetchWarehouses,
} from "@/features/warehouse/warehouse-api"
import type { StorageLocation } from "@/types/inventory"

export function LocationsPage() {
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const [search, setSearch] = useState(() => searchParams.get("search") ?? "")
  const [warehouseFilter, setWarehouseFilter] = useState(
    () => searchParams.get("warehouse_id") ?? "",
  )
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<StorageLocation | null>(null)

  useEffect(() => {
    const nextSearch = searchParams.get("search") ?? ""
    const nextWarehouse = searchParams.get("warehouse_id") ?? ""
    setSearch(nextSearch)
    setWarehouseFilter(nextWarehouse)
  }, [searchParams])

  const warehousesQuery = useQuery({
    queryKey: ["warehouses", "list"],
    queryFn: () => fetchWarehouses({ limit: 200 }),
  })

  const query = useQuery({
    queryKey: ["storage-locations", search, warehouseFilter],
    queryFn: () =>
      fetchStorageLocations({
        search: search || undefined,
        warehouse_id: warehouseFilter ? Number(warehouseFilter) : undefined,
        limit: 200,
      }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteStorageLocation,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["storage-locations"] })
      toast.success("Location deleted")
    },
    onError: () => toast.error("Could not delete location"),
  })

  const items = query.data?.items ?? []

  return (
    <>
      <PageHeader
        title="Storage locations"
        description="Bins, racks, and zones within warehouses."
        actions={
          <Button
            onClick={() => {
              setEditing(null)
              setDialogOpen(true)
            }}
          >
            Add location
          </Button>
        }
      />
      <ContentSheet>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input
            className="max-w-xs"
            placeholder="Search location code…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Select
            className="max-w-xs"
            value={warehouseFilter}
            onChange={(e) => setWarehouseFilter(e.target.value)}
          >
            <option value="">All warehouses</option>
            {(warehousesQuery.data?.items ?? []).map((w) => (
              <option key={w.id} value={w.id}>
                {w.code}
              </option>
            ))}
          </Select>
        </div>
        <div className="overflow-x-auto rounded-md border border-border">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b bg-muted/50 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-2">Code</th>
                <th className="px-3 py-2">Warehouse</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">Zone</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((loc) => (
                <tr key={loc.id} className="border-b border-border/50">
                  <td className="px-3 py-2 font-mono text-xs">{loc.code}</td>
                  <td className="px-3 py-2">{loc.warehouse_id}</td>
                  <td className="px-3 py-2">{loc.location_type}</td>
                  <td className="px-3 py-2">{loc.zone ?? "—"}</td>
                  <td className="px-3 py-2">{loc.status}</td>
                  <td className="px-3 py-2 text-right space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditing(loc)
                        setDialogOpen(true)
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteMutation.mutate(loc.id)}
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
      <LocationFormDialog
        open={dialogOpen}
        location={editing}
        onClose={() => {
          setDialogOpen(false)
          setEditing(null)
        }}
      />
    </>
  )
}
