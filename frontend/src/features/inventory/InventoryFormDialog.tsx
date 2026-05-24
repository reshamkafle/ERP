import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useMemo, useState } from "react"
import { useFieldArray, useForm } from "react-hook-form"
import { Link } from "react-router-dom"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { fetchBomItems } from "@/features/bom/bom-api"
import { fetchStorageLocations, fetchWarehouses } from "@/features/warehouse/warehouse-api"
import {
  createInventoryItem,
  fetchCategories,
  fetchInventoryAnalytics,
  fetchInventoryBomUsages,
  fetchInventoryTransactions,
  fetchTaxRates,
  updateInventoryItem,
} from "@/features/inventory/inventory-api"
import { fetchSuppliers } from "@/features/suppliers/suppliers-api"
import {
  defaultInventoryFormValues,
  inventoryFormSchema,
  type InventoryFormValues,
} from "@/lib/inventory-schema"
import {
  INVENTORY_TABS,
  type InventoryFieldDef,
  type InventoryTabDef,
} from "@/lib/inventory-field-groups"
import type { InventoryItem } from "@/types/inventory"

function itemToForm(item: InventoryItem): InventoryFormValues {
  return {
    ...defaultInventoryFormValues,
    sku: item.sku,
    name: item.name,
    description: item.description ?? "",
    barcode: item.barcode ?? "",
    qr_code: item.qr_code ?? "",
    rfid_tag: item.rfid_tag ?? "",
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
    roll_tracking_enabled: item.roll_tracking_enabled ?? false,
    batch_management_enabled: item.batch_management_enabled,
    expiry_date_flag: item.expiry_date_flag,
    shelf_life_days: item.shelf_life_days ?? "",
    primary_uom: item.primary_uom,
    secondary_uom: item.secondary_uom ?? "",
    purchase_uom: item.purchase_uom ?? "",
    sales_uom: item.sales_uom ?? "",
    conversion_factor: item.conversion_factor ?? "",
    length: item.length ?? "",
    width: item.width ?? "",
    height: item.height ?? "",
    volume: item.volume ?? "",
    gross_weight: item.gross_weight ?? "",
    net_weight: item.net_weight ?? "",
    abc_class: item.abc_class ?? "",
    xyz_class: item.xyz_class ?? "",
    lifecycle_status: item.lifecycle_status,
    approval_status: item.approval_status,
    tax_code: item.tax_code ?? "",
    tax_rate_id: item.tax_rate_id,
    hs_code: item.hs_code ?? "",
    country_of_origin: item.country_of_origin ?? "",
    hazardous_flag: item.hazardous_flag,
    perishable_flag: item.perishable_flag,
    hazardous_material_class: item.hazardous_material_class ?? "",
    regulatory_compliance_codes: item.regulatory_compliance_codes ?? "",
    price: Number(item.price),
    cost_price: Number(item.cost_price),
    standard_cost: item.standard_cost ? Number(item.standard_cost) : 0,
    cost_valuation_method: item.cost_valuation_method ?? "",
    low_stock_threshold: item.low_stock_threshold,
    reorder_level: item.reorder_level,
    max_stock_level: item.max_stock_level ?? "",
    economic_order_qty: item.economic_order_qty ?? "",
    lead_time_days: item.lead_time_days ?? "",
    default_supplier_id: item.default_supplier_id ?? item.default_supplier?.id ?? null,
    default_warehouse_id: item.default_warehouse_id ?? item.default_warehouse?.id ?? null,
    default_location_id: item.default_location_id ?? item.default_location?.id ?? null,
    promotion_reorder_boost: item.promotion_reorder_boost,
    reorder_point: item.reorder_point,
    safety_stock_level: item.safety_stock_level,
    min_order_qty: item.min_order_qty ?? "",
    max_order_qty: item.max_order_qty ?? "",
    procurement_lead_time_days: item.procurement_lead_time_days ?? "",
    demand_forecast_notes: item.demand_forecast_notes ?? "",
    quality_inspection_required: item.quality_inspection_required,
    inspection_checklist_json: item.inspection_checklist
      ? JSON.stringify(item.inspection_checklist, null, 2)
      : "",
    expiry_alert_threshold_days: item.expiry_alert_threshold_days ?? "",
    image_url: item.image_url ?? "",
    attachments_json: item.attachments ? JSON.stringify(item.attachments, null, 2) : "",
    product_suppliers: (item.product_supplier_links ?? []).map((ps) => ({
      supplier_id: ps.supplier_id,
      vendor_code: ps.vendor_code ?? "",
      is_preferred: ps.is_preferred,
    })),
    manufacturing_item_sku: item.manufacturing_item_sku ?? "",
  }
}

type Props = {
  open: boolean
  item: InventoryItem | null
  onClose: () => void
}

const EDIT_EXTRA_TABS = [
  { id: "stock", title: "Stock" },
  { id: "transactions", title: "Transactions" },
  { id: "audit", title: "Audit" },
] as const

export function InventoryFormDialog({ open, item, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = item !== null
  const [activeTab, setActiveTab] = useState("identification")

  const categoriesQuery = useQuery({
    queryKey: ["inventory", "categories"],
    queryFn: fetchCategories,
    enabled: open,
  })
  const suppliersQuery = useQuery({
    queryKey: ["suppliers", "list", "inventory-form"],
    queryFn: () => fetchSuppliers({ limit: 200 }),
    enabled: open,
  })
  const taxRatesQuery = useQuery({
    queryKey: ["inventory", "tax-rates"],
    queryFn: fetchTaxRates,
    enabled: open,
  })
  const warehousesQuery = useQuery({
    queryKey: ["warehouses", "list"],
    queryFn: () => fetchWarehouses({ limit: 200 }),
    enabled: open,
  })

  const form = useForm<InventoryFormValues>({
    resolver: zodResolver(inventoryFormSchema),
    defaultValues: defaultInventoryFormValues,
  })

  const warehouseId = form.watch("default_warehouse_id")
  const locationsQuery = useQuery({
    queryKey: ["storage-locations", warehouseId],
    queryFn: () => fetchStorageLocations({ warehouse_id: warehouseId ?? undefined, limit: 200 }),
    enabled: open && warehouseId != null,
  })

  const suppliersArray = useFieldArray({ control: form.control, name: "product_suppliers" })

  useEffect(() => {
    if (!open) return
    setActiveTab("identification")
    form.reset(item ? itemToForm(item) : defaultInventoryFormValues)
  }, [open, item, form])

  const mfgItemsQuery = useQuery({
    queryKey: ["bom", "items", "inventory-link"],
    queryFn: () => fetchBomItems(),
    enabled: open,
  })
  const bomUsagesQuery = useQuery({
    queryKey: ["inventory", "bom-usages", item?.id],
    queryFn: () => fetchInventoryBomUsages(item!.id),
    enabled: open && isEdit && item !== null,
  })
  const transactionsQuery = useQuery({
    queryKey: ["inventory", "transactions", item?.id],
    queryFn: () => fetchInventoryTransactions(item!.id),
    enabled: open && isEdit && activeTab === "transactions" && item !== null,
  })
  const analyticsQuery = useQuery({
    queryKey: ["inventory", "analytics", item?.id],
    queryFn: () => fetchInventoryAnalytics(item!.id),
    enabled: open && isEdit && activeTab === "stock" && item !== null,
  })

  const saveMutation = useMutation({
    mutationFn: async (values: InventoryFormValues) => {
      if (isEdit && item) return updateInventoryItem(item.id, values)
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

  const tabs = useMemo(() => {
    const base = [...INVENTORY_TABS]
    if (isEdit) return [...base, ...EDIT_EXTRA_TABS]
    return base
  }, [isEdit])

  const categories = categoriesQuery.data ?? []
  const suppliers = suppliersQuery.data?.items ?? []
  const taxRates = taxRatesQuery.data ?? []
  const warehouses = warehousesQuery.data?.items ?? []
  const locations = locationsQuery.data?.items ?? []
  const linkableMfgItems = (mfgItemsQuery.data ?? []).filter((i) => i.category !== "FINISHED_GOOD")

  if (!open) return null

  const { register, handleSubmit, formState, watch, setValue } = form
  const watchAll = watch()

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
    >
      <form
        className="my-4 flex w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
      >
        <div className="border-b border-border px-4 py-3">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-lg font-semibold">{isEdit ? "Edit item" : "New item"}</h2>
            <Button type="button" variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
          <div className="mt-3 flex flex-wrap gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`rounded-md px-2.5 py-1 text-xs font-medium ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.title}
              </button>
            ))}
          </div>
        </div>

        <div className="max-h-[min(65vh,640px)] overflow-y-auto p-4">
          {activeTab === "manufacturing" ? (
            <ManufacturingTab
              register={register}
              linkableMfgItems={linkableMfgItems}
              isEdit={isEdit}
              bomUsages={bomUsagesQuery.data}
              item={item}
            />
          ) : activeTab === "stock" && isEdit && item ? (
            <StockTab item={item} analytics={analyticsQuery.data} loading={analyticsQuery.isLoading} />
          ) : activeTab === "transactions" && isEdit ? (
            <TransactionsTab
              transactions={transactionsQuery.data?.items}
              loading={transactionsQuery.isLoading}
            />
          ) : activeTab === "audit" && isEdit && item ? (
            <AuditTab item={item} />
          ) : activeTab === "replenishment" ? (
            <ReplenishmentTab
              register={register}
              suppliers={suppliers}
              suppliersArray={suppliersArray}
              setValue={setValue}
            />
          ) : (
            <FieldsTab
              tab={INVENTORY_TABS.find((t) => t.id === activeTab) ?? INVENTORY_TABS[0]}
              register={register}
              formState={formState}
              watchAll={watchAll}
              categories={categories}
              taxRates={taxRates}
              warehouses={warehouses}
              locations={locations}
              setValue={setValue}
            />
          )}
          {!isEdit && activeTab === "pricing" ? (
            <p className="mt-3 text-xs text-muted-foreground">
              Initial stock is set on create. Per-warehouse balances appear after Phase 3 posting.
            </p>
          ) : null}
          {!isEdit && activeTab === "pricing" ? (
            <Field label="Initial stock" className="mt-2 max-w-xs">
              <Input type="number" min={0} {...register("initial_stock", { valueAsNumber: true })} />
            </Field>
          ) : null}
        </div>

        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending} data-testid="inventory-create">
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create item"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function FieldsTab({
  tab,
  register,
  formState,
  watchAll,
  categories,
  taxRates,
  warehouses,
  locations,
  setValue,
}: {
  tab: InventoryTabDef
  register: ReturnType<typeof useForm<InventoryFormValues>>["register"]
  formState: ReturnType<typeof useForm<InventoryFormValues>>["formState"]
  watchAll: InventoryFormValues
  categories: { id: number; name: string }[]
  taxRates: { id: number; code: string; name: string }[]
  warehouses: { id: number; code: string; name: string }[]
  locations: { id: number; code: string }[]
  setValue: ReturnType<typeof useForm<InventoryFormValues>>["setValue"]
}) {
  const visibleFields = tab.fields.filter((f) => {
    if (!f.showWhen) return true
    return Boolean(watchAll[f.showWhen as keyof InventoryFormValues])
  })

  return (
    <section className="space-y-3">
      {tab.description ? (
        <p className="text-xs text-muted-foreground">{tab.description}</p>
      ) : null}
      <div className="grid gap-3 sm:grid-cols-2">
        {visibleFields.map((field) => (
          <InventoryField
            key={field.path}
            field={field}
            register={register}
            error={formState.errors[field.path as keyof InventoryFormValues]?.message as string}
            categories={categories}
            taxRates={taxRates}
            warehouses={warehouses}
            locations={locations}
              setValue={setValue}
          />
        ))}
      </div>
    </section>
  )
}

function InventoryField({
  field,
  register,
  error,
  categories,
  taxRates,
  warehouses,
  locations,
  setValue,
}: {
  field: InventoryFieldDef
  register: ReturnType<typeof useForm<InventoryFormValues>>["register"]
  error?: string
  categories: { id: number; name: string }[]
  taxRates: { id: number; code: string; name: string }[]
  warehouses: { id: number; code: string; name: string }[]
  locations: { id: number; code: string }[]
  setValue: ReturnType<typeof useForm<InventoryFormValues>>["setValue"]
}) {
  const span = field.colSpan === 2 ? "sm:col-span-2" : ""
  const path = field.path as keyof InventoryFormValues

  if (field.path === "category_id") {
    return (
      <Field label={field.label} error={error} className={span}>
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
    )
  }
  if (field.path === "tax_rate_id") {
    return (
      <Field label={field.label} error={error} className={span}>
        <Select
          {...register("tax_rate_id", {
            setValueAs: (v) => (v === "" || v === undefined ? null : Number(v)),
          })}
        >
          <option value="">— None —</option>
          {taxRates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.code} — {t.name}
            </option>
          ))}
        </Select>
      </Field>
    )
  }
  if (field.path === "default_warehouse_id") {
    return (
      <Field label={field.label} error={error} className={span}>
        <Select
          {...register("default_warehouse_id", {
            setValueAs: (v) => (v === "" || v === undefined ? null : Number(v)),
          })}
          onChange={(e) => {
            setValue("default_warehouse_id", e.target.value ? Number(e.target.value) : null)
            setValue("default_location_id", null)
          }}
        >
          <option value="">— None —</option>
          {warehouses.map((w) => (
            <option key={w.id} value={w.id}>
              {w.code} — {w.name}
            </option>
          ))}
        </Select>
      </Field>
    )
  }
  if (field.path === "default_location_id") {
    return (
      <Field label={field.label} error={error} className={span}>
        <Select
          {...register("default_location_id", {
            setValueAs: (v) => (v === "" || v === undefined ? null : Number(v)),
          })}
        >
          <option value="">— None —</option>
          {locations.map((l) => (
            <option key={l.id} value={l.id}>
              {l.code}
            </option>
          ))}
        </Select>
      </Field>
    )
  }

  if (field.type === "checkbox") {
    return (
      <Field label={field.label} error={error} className={`${span} flex items-center gap-2 pt-6`}>
        <input type="checkbox" className="h-4 w-4" {...register(path)} />
      </Field>
    )
  }
  if (field.type === "textarea") {
    return (
      <Field label={field.label} error={error} className={span}>
        <Textarea {...register(path)} rows={3} placeholder={field.placeholder} />
      </Field>
    )
  }
  if (field.type === "select" && field.options) {
    return (
      <Field label={field.label} error={error} className={span}>
        <Select {...register(path)}>
          {field.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </Field>
    )
  }
  if (field.type === "number") {
    return (
      <Field label={field.label} error={error} className={span}>
        <Input
          type="number"
          {...register(path, {
            setValueAs: (v) => (v === "" || v === undefined ? "" : Number(v)),
          })}
        />
      </Field>
    )
  }
  return (
    <Field label={field.label} error={error} className={span}>
      <Input {...register(path)} placeholder={field.placeholder} />
    </Field>
  )
}

function ReplenishmentTab({
  register,
  suppliers,
  suppliersArray,
  setValue,
}: {
  register: ReturnType<typeof useForm<InventoryFormValues>>["register"]
  suppliers: { id: number; name: string }[]
  suppliersArray: ReturnType<typeof useFieldArray<InventoryFormValues, "product_suppliers">>
  setValue: ReturnType<typeof useForm<InventoryFormValues>>["setValue"]
}) {
  const tab = INVENTORY_TABS.find((t) => t.id === "replenishment")!
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        {tab.fields.map((field) => {
          if (field.path === "default_supplier_id") {
            return (
              <Field key={field.path} label={field.label}>
                <Select
                  {...register("default_supplier_id", {
                    setValueAs: (v) => (v === "" || v === undefined ? null : Number(v)),
                  })}
                >
                  <option value="">— None —</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </Select>
              </Field>
            )
          }
          if (field.type === "checkbox") {
            return (
              <Field key={field.path} label={field.label} className="flex items-center gap-2 pt-6">
                <input type="checkbox" className="h-4 w-4" {...register(field.path as "promotion_reorder_boost")} />
              </Field>
            )
          }
          if (field.type === "number") {
            return (
              <Field key={field.path} label={field.label}>
                <Input
                  type="number"
                  {...register(field.path as keyof InventoryFormValues, {
                    setValueAs: (v) => (v === "" ? "" : Number(v)),
                  })}
                />
              </Field>
            )
          }
          return (
            <Field key={field.path} label={field.label} className={field.colSpan === 2 ? "sm:col-span-2" : ""}>
              <Textarea {...register(field.path as "demand_forecast_notes")} rows={2} />
            </Field>
          )
        })}
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold">Vendor codes</h4>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() =>
              suppliersArray.append({ supplier_id: suppliers[0]?.id ?? 1, vendor_code: "", is_preferred: false })
            }
          >
            Add vendor
          </Button>
        </div>
        {suppliersArray.fields.map((row, index) => (
          <div key={row.id} className="grid gap-2 rounded-lg border border-border/80 p-3 sm:grid-cols-4">
            <Field label="Supplier">
              <Select
                {...register(`product_suppliers.${index}.supplier_id`, { valueAsNumber: true })}
              >
                {suppliers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Vendor code">
              <Input {...register(`product_suppliers.${index}.vendor_code`)} />
            </Field>
            <Field label="Preferred" className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                {...register(`product_suppliers.${index}.is_preferred`)}
                onChange={(e) => {
                  if (e.target.checked) {
                    suppliersArray.fields.forEach((_, i) =>
                      setValue(`product_suppliers.${i}.is_preferred`, i === index),
                    )
                  }
                }}
              />
            </Field>
            <Button type="button" variant="ghost" size="sm" onClick={() => suppliersArray.remove(index)}>
              Remove
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}

function ManufacturingTab({
  register,
  linkableMfgItems,
  isEdit,
  bomUsages,
  item,
}: {
  register: ReturnType<typeof useForm<InventoryFormValues>>["register"]
  linkableMfgItems: { sku: string; name: string }[]
  isEdit: boolean
  bomUsages?: { parent_sku: string; parent_name: string; required_qty: string; on_hand_stock: number; is_short: boolean }[]
  item: InventoryItem | null
}) {
  return (
    <div className="space-y-4">
      <Field label="Manufacturing item SKU (BOM link)">
        <Select {...register("manufacturing_item_sku")}>
          <option value="">— None —</option>
          {linkableMfgItems.map((m) => (
            <option key={m.sku} value={m.sku}>
              {m.sku} — {m.name}
            </option>
          ))}
        </Select>
      </Field>
      {isEdit && item ? (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Used as component in {item.bom_parent_count} BOM(s).
            {item.has_bom_shortage ? (
              <Badge variant="danger" className="ml-2">
                Shortage
              </Badge>
            ) : null}
          </p>
          {bomUsages?.length ? (
            <ul className="text-sm space-y-1">
              {bomUsages.map((u) => (
                <li key={u.parent_sku}>
                  <Link to="/bom" className="text-primary hover:underline">
                    {u.parent_sku}
                  </Link>{" "}
                  — {u.parent_name} (req {u.required_qty}, on hand {u.on_hand_stock})
                  {u.is_short ? " — SHORT" : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-muted-foreground">Not used in any BOM as a component.</p>
          )}
        </div>
      ) : null}
    </div>
  )
}

function StockTab({
  item,
  analytics,
  loading,
}: {
  item: InventoryItem
  analytics?: { stock_value: string; turnover_ratio: string; dead_stock_value: string }
  loading: boolean
}) {
  return (
    <div className="space-y-4 text-sm">
      <p>
        Global on-hand: <strong>{item.stock}</strong> (legacy aggregate). Per-warehouse balances below.
      </p>
      {loading ? <Progress indeterminate /> : null}
      {analytics ? (
        <div className="grid gap-2 sm:grid-cols-3">
          <div className="rounded-lg border p-2">Stock value: {analytics.stock_value}</div>
          <div className="rounded-lg border p-2">Turnover: {analytics.turnover_ratio}</div>
          <div className="rounded-lg border p-2">Dead stock: {analytics.dead_stock_value}</div>
        </div>
      ) : null}
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="border-b">
            <th className="py-1">Warehouse</th>
            <th>Location</th>
            <th>On hand</th>
            <th>Available</th>
            <th>Reserved</th>
          </tr>
        </thead>
        <tbody>
          {(item.stock_balances ?? []).length === 0 ? (
            <tr>
              <td colSpan={5} className="py-4 text-muted-foreground">
                No per-warehouse balances yet.
              </td>
            </tr>
          ) : (
            item.stock_balances!.map((b) => (
              <tr key={b.id} className="border-b border-border/50">
                <td className="py-1">{b.warehouse_code ?? b.warehouse_id}</td>
                <td>{b.location_code ?? "—"}</td>
                <td>{b.on_hand}</td>
                <td>{b.available}</td>
                <td>{b.reserved}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

function TransactionsTab({
  transactions,
  loading,
}: {
  transactions?: { id: number; transaction_type: string; transaction_at: string; quantity: number; reference_document: string | null }[]
  loading: boolean
}) {
  if (loading) return <p className="text-sm text-muted-foreground">Loading transactions…</p>
  if (!transactions?.length) {
    return <p className="text-sm text-muted-foreground">No inventory transactions recorded yet.</p>
  }
  return (
    <table className="w-full text-left text-xs">
      <thead>
        <tr className="border-b">
          <th className="py-1">Date</th>
          <th>Type</th>
          <th>Qty</th>
          <th>Reference</th>
        </tr>
      </thead>
      <tbody>
        {transactions.map((t) => (
          <tr key={t.id} className="border-b border-border/50">
            <td className="py-1">{new Date(t.transaction_at).toLocaleString()}</td>
            <td>{t.transaction_type}</td>
            <td>{t.quantity}</td>
            <td>{t.reference_document ?? "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function AuditTab({ item }: { item: InventoryItem }) {
  return (
    <dl className="grid gap-2 text-sm sm:grid-cols-2">
      <div>
        <dt className="text-muted-foreground">Created</dt>
        <dd>{new Date(item.created_at).toLocaleString()}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Updated</dt>
        <dd>{new Date(item.updated_at).toLocaleString()}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Created by</dt>
        <dd>{item.created_by?.email ?? "—"}</dd>
      </div>
      <div>
        <dt className="text-muted-foreground">Updated by</dt>
        <dd>{item.updated_by?.email ?? "—"}</dd>
      </div>
      <div className="sm:col-span-2">
        <dt className="text-muted-foreground">Current stock (read-only)</dt>
        <dd>{item.stock} — adjusted via sales, purchases, and future stock postings.</dd>
      </div>
    </dl>
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
      <Label className="text-xs">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}
