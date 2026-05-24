import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createWarehouse,
  updateWarehouse,
  type WarehouseFormValues,
} from "@/features/warehouse/warehouse-api"
import type { Warehouse } from "@/types/inventory"

const defaults: WarehouseFormValues = {
  code: "",
  name: "",
  warehouse_type: "MAIN",
  address: "",
  capacity_weight: "",
  capacity_volume: "",
  capacity_pallets: "",
  status: "ACTIVE",
  is_default: false,
  wave_picking_enabled: false,
  cross_docking_enabled: false,
  cycle_count_frequency: "",
  cycle_count_class: "",
  packing_rules_json: "",
}

function toForm(w: Warehouse): WarehouseFormValues {
  return {
    code: w.code,
    name: w.name,
    warehouse_type: w.warehouse_type,
    address: w.address ?? "",
    capacity_weight: w.capacity_weight ?? "",
    capacity_volume: w.capacity_volume ?? "",
    capacity_pallets: w.capacity_pallets ?? "",
    status: w.status,
    is_default: w.is_default,
    wave_picking_enabled: w.wave_picking_enabled,
    cross_docking_enabled: w.cross_docking_enabled,
    cycle_count_frequency: w.cycle_count_frequency ?? "",
    cycle_count_class: w.cycle_count_class ?? "",
    packing_rules_json: w.packing_rules ? JSON.stringify(w.packing_rules, null, 2) : "",
  }
}

type Props = {
  open: boolean
  warehouse: Warehouse | null
  onClose: () => void
}

export function WarehouseFormDialog({ open, warehouse, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = warehouse !== null
  const form = useForm<WarehouseFormValues>({ defaultValues: defaults })

  useEffect(() => {
    if (!open) return
    form.reset(warehouse ? toForm(warehouse) : defaults)
  }, [open, warehouse, form])

  const saveMutation = useMutation({
    mutationFn: (values: WarehouseFormValues) =>
      isEdit && warehouse
        ? updateWarehouse(warehouse.id, values)
        : createWarehouse(values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["warehouses"] })
      toast.success(isEdit ? "Warehouse updated" : "Warehouse created")
      onClose()
    },
    onError: () => toast.error("Could not save warehouse"),
  })

  if (!open) return null

  const { register, handleSubmit } = form

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form
        className="w-full max-w-lg rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="mb-4 text-lg font-semibold">{isEdit ? "Edit warehouse" : "New warehouse"}</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Code">
            <Input {...register("code")} required />
          </Field>
          <Field label="Name">
            <Input {...register("name")} required />
          </Field>
          <Field label="Type">
            <Select {...register("warehouse_type")}>
              <option value="MAIN">Main</option>
              <option value="DISTRIBUTION">Distribution</option>
              <option value="PRODUCTION">Production</option>
              <option value="COLD_STORAGE">Cold storage</option>
              <option value="THIRD_PARTY">3PL</option>
              <option value="OTHER">Other</option>
            </Select>
          </Field>
          <Field label="Status">
            <Select {...register("status")}>
              <option value="ACTIVE">Active</option>
              <option value="INACTIVE">Inactive</option>
            </Select>
          </Field>
          <Field label="Address" className="sm:col-span-2">
            <Textarea {...register("address")} rows={2} />
          </Field>
          <Field label="Default warehouse" className="flex items-center gap-2 pt-6">
            <input type="checkbox" {...register("is_default")} />
          </Field>
          <Field label="Wave picking" className="flex items-center gap-2 pt-6">
            <input type="checkbox" {...register("wave_picking_enabled")} />
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
