import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import {
  createStorageLocation,
  fetchWarehouses,
  updateStorageLocation,
  type LocationFormValues,
} from "@/features/warehouse/warehouse-api"
import type { StorageLocation } from "@/types/inventory"

const defaults: LocationFormValues = {
  code: "",
  warehouse_id: 0,
  aisle: "",
  row: "",
  column: "",
  level: "",
  location_type: "BULK",
  capacity: "",
  putaway_strategy: "",
  picking_strategy: "",
  status: "AVAILABLE",
  zone: "",
}

function toForm(loc: StorageLocation): LocationFormValues {
  return {
    code: loc.code,
    warehouse_id: loc.warehouse_id,
    aisle: loc.aisle ?? "",
    row: loc.row ?? "",
    column: loc.column ?? "",
    level: loc.level ?? "",
    location_type: loc.location_type,
    capacity: loc.capacity ?? "",
    putaway_strategy: loc.putaway_strategy ?? "",
    picking_strategy: loc.picking_strategy ?? "",
    status: loc.status,
    zone: loc.zone ?? "",
  }
}

type Props = {
  open: boolean
  location: StorageLocation | null
  onClose: () => void
}

export function LocationFormDialog({ open, location, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = location !== null
  const form = useForm<LocationFormValues>({ defaultValues: defaults })

  const warehousesQuery = useQuery({
    queryKey: ["warehouses", "list"],
    queryFn: () => fetchWarehouses({ limit: 200 }),
    enabled: open,
  })

  useEffect(() => {
    if (!open) return
    const wh = warehousesQuery.data?.items?.[0]?.id ?? 0
    form.reset(location ? toForm(location) : { ...defaults, warehouse_id: wh })
  }, [open, location, form, warehousesQuery.data])

  const saveMutation = useMutation({
    mutationFn: (values: LocationFormValues) =>
      isEdit && location
        ? updateStorageLocation(location.id, values)
        : createStorageLocation(values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["storage-locations"] })
      toast.success(isEdit ? "Location updated" : "Location created")
      onClose()
    },
    onError: () => toast.error("Could not save location"),
  })

  if (!open) return null

  const { register, handleSubmit } = form
  const warehouses = warehousesQuery.data?.items ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form
        className="w-full max-w-lg rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="mb-4 text-lg font-semibold">{isEdit ? "Edit location" : "New location"}</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Warehouse" className="sm:col-span-2">
            <Select {...register("warehouse_id", { valueAsNumber: true })}>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.code} — {w.name}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Location code">
            <Input {...register("code")} required />
          </Field>
          <Field label="Type">
            <Select {...register("location_type")}>
              <option value="BULK">Bulk</option>
              <option value="PICKING">Picking</option>
              <option value="RECEIVING">Receiving</option>
              <option value="SHIPPING">Shipping</option>
              <option value="QUARANTINE">Quarantine</option>
              <option value="STAGING">Staging</option>
            </Select>
          </Field>
          <Field label="Aisle">
            <Input {...register("aisle")} />
          </Field>
          <Field label="Row">
            <Input {...register("row")} />
          </Field>
          <Field label="Column">
            <Input {...register("column")} />
          </Field>
          <Field label="Level">
            <Input {...register("level")} />
          </Field>
          <Field label="Zone">
            <Input {...register("zone")} />
          </Field>
          <Field label="Status">
            <Select {...register("status")}>
              <option value="AVAILABLE">Available</option>
              <option value="BLOCKED">Blocked</option>
              <option value="DAMAGED">Damaged</option>
            </Select>
          </Field>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            Save
          </Button>
        </div>
      </form>
    </div>
  )
}

function Field({
  label,
  className,
  children,
}: {
  label: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={className}>
      <Label className="text-xs">{label}</Label>
      {children}
    </div>
  )
}
