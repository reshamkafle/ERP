import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { createInventoryItem, updateInventoryItem } from "@/features/inventory/inventory-api"
import {
  inventoryFormSchema,
  type InventoryFormValues,
} from "@/lib/inventory-schema"
import type { Category, InventoryItem } from "@/types/inventory"

const defaultValues: InventoryFormValues = {
  sku: "",
  name: "",
  description: "",
  barcode: "",
  alternate_codes: "",
  category_id: null,
  sub_category: "",
  product_line: "",
  item_type: "TRADING",
  size: "",
  color: "",
  model: "",
  variant: "",
  serial_number_flag: false,
  batch_lot_flag: false,
  expiry_date_flag: false,
  primary_uom: "EA",
  secondary_uom: "",
  conversion_factor: "",
  length: "",
  width: "",
  height: "",
  volume: "",
  gross_weight: "",
  net_weight: "",
  lifecycle_status: "ACTIVE",
  approval_status: "DRAFT",
  tax_code: "",
  hs_code: "",
  country_of_origin: "",
  hazardous_flag: false,
  perishable_flag: false,
  price: 0,
  cost_price: 0,
  low_stock_threshold: 0,
  initial_stock: 0,
}

function itemToForm(item: InventoryItem): InventoryFormValues {
  return {
    sku: item.sku,
    name: item.name,
    description: item.description ?? "",
    barcode: item.barcode ?? "",
    alternate_codes: item.alternate_codes ?? "",
    category_id: item.category_id,
    sub_category: item.sub_category ?? "",
    product_line: item.product_line ?? "",
    item_type: item.item_type,
    size: item.size ?? "",
    color: item.color ?? "",
    model: item.model ?? "",
    variant: item.variant ?? "",
    serial_number_flag: item.serial_number_flag,
    batch_lot_flag: item.batch_lot_flag,
    expiry_date_flag: item.expiry_date_flag,
    primary_uom: item.primary_uom,
    secondary_uom: item.secondary_uom ?? "",
    conversion_factor: item.conversion_factor ?? "",
    length: item.length ?? "",
    width: item.width ?? "",
    height: item.height ?? "",
    volume: item.volume ?? "",
    gross_weight: item.gross_weight ?? "",
    net_weight: item.net_weight ?? "",
    lifecycle_status: item.lifecycle_status,
    approval_status: item.approval_status,
    tax_code: item.tax_code ?? "",
    hs_code: item.hs_code ?? "",
    country_of_origin: item.country_of_origin ?? "",
    hazardous_flag: item.hazardous_flag,
    perishable_flag: item.perishable_flag,
    price: Number(item.price),
    cost_price: Number(item.cost_price),
    low_stock_threshold: item.low_stock_threshold,
  }
}

type Props = {
  open: boolean
  item: InventoryItem | null
  categories: Category[]
  onClose: () => void
}

export function InventoryFormDialog({ open, item, categories, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = item !== null

  const form = useForm<InventoryFormValues>({
    resolver: zodResolver(inventoryFormSchema),
    defaultValues,
  })

  useEffect(() => {
    if (!open) return
    form.reset(item ? itemToForm(item) : defaultValues)
  }, [open, item, form])

  const saveMutation = useMutation({
    mutationFn: async (values: InventoryFormValues) => {
      if (isEdit && item) {
        return updateInventoryItem(item.id, values)
      }
      return createInventoryItem(values)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["inventory"] })
      toast.success(isEdit ? "Item updated" : "Item created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save item"
      toast.error(typeof detail === "string" ? detail : "Could not save item")
    },
  })

  if (!open) return null

  const { register, handleSubmit, formState } = form

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-8"
      role="dialog"
      aria-modal="true"
    >
      <form
        className="w-full max-w-3xl rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">{isEdit ? "Edit item" : "New item"}</h2>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>

        <div className="max-h-[70vh] space-y-6 overflow-y-auto p-4">
          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Identification</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="SKU / Item code" error={formState.errors.sku?.message}>
                <Input {...register("sku")} />
              </Field>
              <Field label="Item name" error={formState.errors.name?.message}>
                <Input {...register("name")} />
              </Field>
              <Field label="Barcode (EAN/UPC)" className="sm:col-span-2">
                <Input {...register("barcode")} />
              </Field>
              <Field label="Alternate codes" className="sm:col-span-2">
                <Textarea {...register("alternate_codes")} placeholder="Comma-separated codes" />
              </Field>
              <Field label="Description" className="sm:col-span-2">
                <Textarea {...register("description")} />
              </Field>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Classification</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Category / group">
                <Select
                  {...register("category_id", {
                    setValueAs: (v) => (v === "" || v === undefined ? null : Number(v)),
                  })}
                >
                  <option value="">— None —</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Sub-category">
                <Input {...register("sub_category")} />
              </Field>
              <Field label="Product line">
                <Input {...register("product_line")} />
              </Field>
              <Field label="Type">
                <Select {...register("item_type")}>
                  <option value="RAW">Raw</option>
                  <option value="FINISHED">Finished</option>
                  <option value="TRADING">Trading</option>
                  <option value="SERVICE">Service</option>
                  <option value="ASSET">Asset</option>
                </Select>
              </Field>
              <Field label="Size">
                <Input {...register("size")} />
              </Field>
              <Field label="Color">
                <Input {...register("color")} />
              </Field>
              <Field label="Model">
                <Input {...register("model")} />
              </Field>
              <Field label="Variant">
                <Input {...register("variant")} />
              </Field>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Tracking flags</h3>
            <div className="flex flex-wrap gap-4 text-sm">
              <label className="flex items-center gap-2">
                <input type="checkbox" {...register("serial_number_flag")} />
                Serial number
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" {...register("batch_lot_flag")} />
                Batch / lot
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" {...register("expiry_date_flag")} />
                Expiry date
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" {...register("hazardous_flag")} />
                Hazardous
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" {...register("perishable_flag")} />
                Perishable
              </label>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Units & dimensions</h3>
            <div className="grid gap-3 sm:grid-cols-3">
              <Field label="Primary UOM">
                <Input {...register("primary_uom")} />
              </Field>
              <Field label="Secondary UOM">
                <Input {...register("secondary_uom")} />
              </Field>
              <Field label="Conversion factor" error={formState.errors.conversion_factor?.message}>
                <Input {...register("conversion_factor")} placeholder="e.g. 12" />
              </Field>
              <Field label="Length">
                <Input {...register("length")} />
              </Field>
              <Field label="Width">
                <Input {...register("width")} />
              </Field>
              <Field label="Height">
                <Input {...register("height")} />
              </Field>
              <Field label="Volume">
                <Input {...register("volume")} />
              </Field>
              <Field label="Gross weight">
                <Input {...register("gross_weight")} />
              </Field>
              <Field label="Net weight">
                <Input {...register("net_weight")} />
              </Field>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Status & compliance</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Lifecycle status">
                <Select {...register("lifecycle_status")}>
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                  <option value="DISCONTINUED">Discontinued</option>
                  <option value="OBSOLETE">Obsolete</option>
                </Select>
              </Field>
              <Field label="Approval status">
                <Select {...register("approval_status")}>
                  <option value="DRAFT">Draft</option>
                  <option value="PENDING">Pending</option>
                  <option value="APPROVED">Approved</option>
                  <option value="REJECTED">Rejected</option>
                </Select>
              </Field>
              <Field label="Tax code">
                <Input {...register("tax_code")} />
              </Field>
              <Field label="HS code">
                <Input {...register("hs_code")} />
              </Field>
              <Field label="Country of origin" className="sm:col-span-2">
                <Input {...register("country_of_origin")} />
              </Field>
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Pricing & stock</h3>
            <div className="grid gap-3 sm:grid-cols-3">
              <Field label="Price">
                <Input
                  type="number"
                  step="0.01"
                  {...register("price", { valueAsNumber: true })}
                />
              </Field>
              <Field label="Cost price">
                <Input
                  type="number"
                  step="0.01"
                  {...register("cost_price", { valueAsNumber: true })}
                />
              </Field>
              <Field label="Low stock threshold">
                <Input type="number" {...register("low_stock_threshold", { valueAsNumber: true })} />
              </Field>
              {!isEdit ? (
                <Field label="Initial stock">
                  <Input type="number" {...register("initial_stock", { valueAsNumber: true })} />
                </Field>
              ) : null}
            </div>
            {isEdit ? (
              <p className="text-xs text-muted-foreground">
                On-hand stock ({item?.stock ?? 0}) changes only via sales or purchases.
              </p>
            ) : null}
          </section>
        </div>

        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create item"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function Field({
  label,
  error,
  className,
  children,
}: {
  label: string
  error?: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={className}>
      <Label className="mb-1 block">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}
