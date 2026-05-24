import { zodResolver } from "@hookform/resolvers/zod"
import type { Resolver } from "react-hook-form"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { useFieldArray, useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { customerToSnapshotFields, fetchCustomers, fetchCustomer } from "@/features/customers/customers-api"
import { fetchPosProducts } from "@/features/pos/pos-api"
import { createSaleOrder, fetchSaleLookups, updateSaleOrder } from "@/features/sales/sales-api"
import { formValuesToPayload, saleToFormValues } from "@/features/sales/sale-order-payload"
import {
  defaultSaleOrderFormValues,
  saleOrderFormSchema,
  type SaleOrderFormValues,
} from "@/lib/sale-order-schema"
import {
  PARTNER_ROLE_LABELS,
  SALES_FIELD_TAB_MAP,
  SALES_ORDER_TABS,
  type SalesFieldDef,
} from "@/lib/sales-order-field-groups"
import { formatMoney } from "@/lib/format-money"
import type { SaleOrder, SalePartnerRole } from "@/types/sale"

type Props = {
  open: boolean
  sale: SaleOrder | null
  onClose: () => void
}

const PARTNER_ROLES: SalePartnerRole[] = [
  "SOLD_TO",
  "SHIP_TO",
  "BILL_TO",
  "PAYER",
  "FORWARDING_AGENT",
  "SALES_EMPLOYEE",
]

function displayFieldValue(path: string, sale: SaleOrder | null): string {
  if (!sale) {
    if (path === "_display.order_number") return "(Auto-generated on save)"
    if (path === "_display.order_time") return "—"
    if (path.startsWith("_display.created") || path.startsWith("_display.updated")) return "—"
    return "—"
  }
  switch (path) {
    case "_display.order_number":
      return sale.order_number
    case "_display.order_time":
      return new Date(sale.created_at).toLocaleTimeString()
    case "_display.created_by":
      return sale.cashier_email ?? "—"
    case "_display.created_at":
      return new Date(sale.created_at).toLocaleString()
    case "_display.updated_by":
      return sale.updated_by_email ?? "—"
    case "_display.updated_at":
      return sale.updated_at ? new Date(sale.updated_at).toLocaleString() : "—"
    case "_display.subtotal":
      return sale.subtotal
    case "_display.tax_amount":
      return sale.tax
    case "_display.gross_total":
      return sale.gross_total
    case "_display.amount_paid":
      return sale.amount_paid
    default:
      return "—"
  }
}

function FieldInput({
  field,
  register,
  readOnly,
  warehouses,
  users,
  paymentMethods,
}: {
  field: SalesFieldDef
  register: ReturnType<typeof useForm<SaleOrderFormValues>>["register"]
  readOnly?: boolean
  warehouses: { id: number; code: string; name: string }[]
  users: { id: number; email: string }[]
  paymentMethods: { id: number; code: string; name: string }[]
}) {
  const path = field.path as Parameters<typeof register>[0]
  if (field.type === "checkbox") {
    return (
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" {...register(path)} disabled={readOnly} />
        {field.label}
      </label>
    )
  }
  if (field.type === "textarea") {
    return <Textarea {...register(path)} disabled={readOnly} rows={3} />
  }
  if (field.type === "warehouse_select") {
    return (
      <Select {...register(path, { valueAsNumber: true })} disabled={readOnly}>
        <option value="">—</option>
        {warehouses.map((w) => (
          <option key={w.id} value={w.id}>
            {w.code} — {w.name}
          </option>
        ))}
      </Select>
    )
  }
  if (field.type === "user_select") {
    return (
      <Select {...register(path, { valueAsNumber: true })} disabled={readOnly}>
        <option value="">—</option>
        {users.map((u) => (
          <option key={u.id} value={u.id}>
            {u.email}
          </option>
        ))}
      </Select>
    )
  }
  if (field.type === "payment_method_select") {
    return (
      <Select {...register(path, { valueAsNumber: true })} disabled={readOnly}>
        <option value="">—</option>
        {paymentMethods.map((m) => (
          <option key={m.id} value={m.id}>
            {m.code} — {m.name}
          </option>
        ))}
      </Select>
    )
  }
  if (field.type === "select" && field.options) {
    return (
      <Select {...register(path)} disabled={readOnly}>
        {field.options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </Select>
    )
  }
  return (
    <Input
      type={field.type === "number" ? "number" : field.type === "date" ? "date" : "text"}
      {...register(path)}
      disabled={readOnly || field.readOnly}
      placeholder={field.placeholder}
    />
  )
}

function computePreviewSummary(
  values: SaleOrderFormValues,
  taxRates: { id: number; rate_percent: string }[],
) {
  const lines = values.items.filter((l) => l.product_id > 0)
  const totalQty = lines.reduce((s, l) => s + Number(l.quantity || 0), 0)
  let gross = 0
  let discount = Number(values.header_discount_amount || 0)
  let tax = 0
  for (const line of lines) {
    const unit = Number(line.unit_price || 0)
    const qty = Number(line.quantity || 0)
    const lineGross = unit * qty
    gross += lineGross
    const pct = Number(line.discount_percent || 0) / 100
    const lineDiscount = lineGross * pct + Number(line.discount_amount || 0)
    discount += lineDiscount
    const net = Math.max(0, lineGross - lineDiscount)
    const rate = taxRates.find((t) => t.id === line.tax_rate_id)
    if (rate) {
      tax += net * (Number(rate.rate_percent) / 100)
    }
  }
  const net = Math.max(0, gross - discount)
  const freight = Number(values.freight_amount || 0)
  const insurance = Number(values.insurance_amount || 0)
  const handling = Number(values.handling_amount || 0)
  const grand = net + freight + insurance + handling + tax
  return {
    total_items: lines.length,
    total_quantity: totalQty,
    total_net: net,
    total_tax: tax,
    total_discount: discount,
    freight,
    insurance,
    handling,
    grand_total: grand,
  }
}

function PartnersSection({
  partners,
  customerId,
  watchedSalespersonId,
  customers,
  users,
  register,
  appendPartner,
}: {
  partners: NonNullable<SaleOrderFormValues["partners"]>
  customerId: number | null | undefined
  watchedSalespersonId: number | null | undefined
  customers: { id: number; customer_code: string | null; name: string }[]
  users: { id: number; email: string }[]
  register: ReturnType<typeof useForm<SaleOrderFormValues>>["register"]
  appendPartner: (value: NonNullable<SaleOrderFormValues["partners"]>[number]) => void
}) {
  return (
    <div className="mb-6 space-y-3">
      <h3 className="text-sm font-semibold">Partner functions</h3>
      <p className="text-sm text-muted-foreground">
        Sold-to is set from the customer tab. Configure bill-to, ship-to, payer, carrier, and sales
        employee below.
      </p>
      {PARTNER_ROLES.filter((r) => r !== "SOLD_TO").map((role) => {
        const idx = partners.findIndex((p) => p.role === role)
        const registerPartner = (field: string) =>
          register(`partners.${idx}.${field}` as Parameters<typeof register>[0])
        return (
          <div key={role} className="grid gap-2 rounded border border-border p-3 sm:grid-cols-4">
            <div className="font-medium text-sm sm:col-span-4">{PARTNER_ROLE_LABELS[role]}</div>
            {idx < 0 ? (
              <Button
                type="button"
                size="sm"
                variant="outline"
                className="sm:col-span-4"
                onClick={() =>
                  appendPartner({
                    role,
                    customer_id:
                      role !== "SALES_EMPLOYEE" && role !== "FORWARDING_AGENT" ? customerId : null,
                    user_id: role === "SALES_EMPLOYEE" ? watchedSalespersonId : null,
                  })
                }
              >
                Configure {PARTNER_ROLE_LABELS[role]}
              </Button>
            ) : (
              <>
                {role === "SALES_EMPLOYEE" ? (
                  <div>
                    <Label>User</Label>
                    <Select {...registerPartner("user_id")}>
                      <option value="">—</option>
                      {users.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.email}
                        </option>
                      ))}
                    </Select>
                  </div>
                ) : role === "FORWARDING_AGENT" ? (
                  <div className="sm:col-span-2">
                    <Label>Carrier name</Label>
                    <Input {...registerPartner("name_override")} />
                  </div>
                ) : (
                  <div className="sm:col-span-2">
                    <Label>Customer</Label>
                    <Select {...registerPartner("customer_id")}>
                      <option value="">—</option>
                      {customers.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.customer_code ? `${c.customer_code} — ` : ""}
                          {c.name}
                        </option>
                      ))}
                    </Select>
                  </div>
                )}
                <input type="hidden" {...registerPartner("role")} value={role} />
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function SaleOrderFormDialog({ open, sale, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = sale !== null && sale.order_status === "DRAFT"
  const [activeTab, setActiveTab] = useState(SALES_ORDER_TABS[0].id)
  const [productSearch, setProductSearch] = useState("")
  const [tabErrors, setTabErrors] = useState<Set<string>>(new Set())

  const form = useForm<SaleOrderFormValues>({
    resolver: zodResolver(saleOrderFormSchema) as Resolver<SaleOrderFormValues>,
    defaultValues: defaultSaleOrderFormValues,
  })

  const { register, handleSubmit, control, watch, setValue, formState } = form
  const { fields, append, remove } = useFieldArray({ control, name: "items" })
  const { append: appendPartner, replace: replacePartners } = useFieldArray({
    control,
    name: "partners",
  })
  const { fields: attachmentFields, append: appendAttachment, remove: removeAttachment } =
    useFieldArray({ control, name: "attachments" })
  const watched = watch()
  const partners = watched.partners ?? []
  const customerId = watch("customer_id")

  const customersQuery = useQuery({
    queryKey: ["customers", "list", ""],
    queryFn: () => fetchCustomers({ limit: 200 }),
    enabled: open,
  })

  const lookupsQuery = useQuery({
    queryKey: ["sales", "lookups"],
    queryFn: fetchSaleLookups,
    enabled: open,
  })

  const productsQuery = useQuery({
    queryKey: ["sales", "products", productSearch],
    queryFn: () => fetchPosProducts({ search: productSearch || undefined, limit: 15 }),
    enabled: open && productSearch.length > 0,
  })

  const preview = useMemo(
    () => computePreviewSummary(watched, lookupsQuery.data?.tax_rates ?? []),
    [watched, lookupsQuery.data?.tax_rates],
  )

  const warehouses = lookupsQuery.data?.warehouses ?? []
  const users = lookupsQuery.data?.users ?? []
  const taxRates = lookupsQuery.data?.tax_rates ?? []
  const paymentMethods = lookupsQuery.data?.payment_methods ?? []
  const customers = customersQuery.data?.items ?? []

  useEffect(() => {
    if (!open) return
    form.reset(sale ? saleToFormValues(sale) : defaultSaleOrderFormValues)
    setActiveTab("header")
    setTabErrors(new Set())
  }, [open, sale, form])

  useEffect(() => {
    if (!customerId || !open) return
    void fetchCustomer(customerId).then((c) => {
      const snap = customerToSnapshotFields(c)
      setValue("customer_snapshot", snap)
      if (!watch("payment_terms")) setValue("payment_terms", c.payment_terms ?? "")
      if (!watch("currency_code")) setValue("currency_code", c.currency_code)
      if (!watch("incoterms")) setValue("incoterms", c.incoterms ?? "")
      if (!watch("price_group")) setValue("price_group", c.customer_group ?? "")
      replacePartners([
        { role: "SOLD_TO", customer_id: customerId },
        { role: "SHIP_TO", customer_id: customerId },
        { role: "BILL_TO", customer_id: customerId },
        { role: "PAYER", customer_id: customerId },
      ])
    })
  }, [customerId, open, setValue, watch, replacePartners])

  const saveMutation = useMutation({
    mutationFn: async (values: SaleOrderFormValues) => {
      const payload = formValuesToPayload(values, false)
      if (isEdit && sale) return updateSaleOrder(sale.id, payload)
      return createSaleOrder(payload)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sales"] })
      toast.success(isEdit ? "Sales order updated" : "Sales order saved as draft")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save order"
      toast.error(typeof detail === "string" ? detail : "Could not save order")
    },
  })

  const onInvalid = () => {
    const errors = form.formState.errors
    const tabs = new Set<string>()
    const visit = (obj: Record<string, unknown>, path: string[] = []) => {
      for (const [key, val] of Object.entries(obj)) {
        const nextPath = [...path, key]
        if (val && typeof val === "object" && "message" in (val as object)) {
          const fieldPath = nextPath.join(".")
          const tabId =
            fieldPath.startsWith("items") ? "lines" : SALES_FIELD_TAB_MAP[fieldPath] ?? "header"
          tabs.add(tabId)
        } else if (val && typeof val === "object") {
          visit(val as Record<string, unknown>, nextPath)
        }
      }
    }
    visit(errors as Record<string, unknown>)
    setTabErrors(tabs)
    if (tabs.size > 0) {
      setActiveTab([...tabs][0]!)
      toast.error("Please fix validation errors in highlighted tabs")
    }
  }

  if (!open) return null

  const activeTabDef = SALES_ORDER_TABS.find((t) => t.id === activeTab) ?? SALES_ORDER_TABS[0]
  const currency = watched.currency_code || "USD"

  let lastSection: string | undefined
  const renderDeclarativeFields = () =>
    activeTabDef.fields.map((field) => {
      const sectionHeader =
        field.section && field.section !== lastSection ? (
          (() => {
            lastSection = field.section
            return (
              <h3
                key={`section-${field.section}`}
                className="mt-4 border-t border-border pt-3 text-sm font-semibold first:mt-0 first:border-0 first:pt-0 sm:col-span-2"
              >
                {field.section}
              </h3>
            )
          })()
        ) : null

      if (field.path.startsWith("_display.")) {
        return (
          <div key={field.path}>
            {sectionHeader}
            <div className={field.colSpan === 2 ? "sm:col-span-2" : ""}>
              <Label>{field.label}</Label>
              <Input value={displayFieldValue(field.path, sale)} disabled readOnly />
            </div>
          </div>
        )
      }

      return (
        <div key={field.path}>
          {sectionHeader}
          <div className={field.colSpan === 2 ? "sm:col-span-2" : ""}>
            {field.path === "customer_id" ? (
              <>
                <Label>{field.label}</Label>
                <Select
                  {...register("customer_id", { valueAsNumber: true })}
                  onChange={(e) => {
                    const v = e.target.value
                    setValue("customer_id", v ? Number(v) : null)
                  }}
                >
                  <option value="">Walk-in / none</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.customer_code ? `${c.customer_code} — ` : ""}
                      {c.name}
                    </option>
                  ))}
                </Select>
              </>
            ) : field.type === "checkbox" ? (
              <FieldInput
                field={field}
                register={register}
                readOnly={Boolean(field.readOnly)}
                warehouses={warehouses}
                users={users}
                paymentMethods={paymentMethods}
              />
            ) : (
              <>
                <Label>{field.label}</Label>
                <FieldInput
                  field={field}
                  register={register}
                  readOnly={Boolean(field.readOnly)}
                  warehouses={warehouses}
                  users={users}
                  paymentMethods={paymentMethods}
                />
              </>
            )}
          </div>
        </div>
      )
    })

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4">
      <form
        className="my-4 flex w-full max-w-6xl flex-col rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values) => saveMutation.mutate(values), onInvalid)}
      >
        <header className="border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">
            {isEdit ? `Edit order ${sale?.order_number}` : "New sales order"}
          </h2>
          <p className="text-sm text-muted-foreground">
            Ten-tab B2B order entry. Required: customer, PO number, payment terms, sales organization,
            and line items with unit price. Order number auto-generates unless overridden.
          </p>
        </header>

        <div className="flex flex-wrap gap-1 border-b border-border px-2 py-2">
          {SALES_ORDER_TABS.map((tab) => (
            <Button
              key={tab.id}
              type="button"
              size="sm"
              variant={activeTab === tab.id ? "default" : "ghost"}
              className={tabErrors.has(tab.id) ? "ring-2 ring-destructive" : undefined}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.title}
            </Button>
          ))}
        </div>

        <div className="max-h-[65vh] overflow-y-auto p-4">
          {activeTabDef.description ? (
            <p className="mb-3 text-sm text-muted-foreground">{activeTabDef.description}</p>
          ) : null}

          {activeTabDef.isSummary ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <SummaryCard label="Total items" value={String(preview.total_items)} />
              <SummaryCard label="Total quantity" value={String(preview.total_quantity)} />
              <SummaryCard label="Net value (est.)" value={formatMoney(preview.total_net, currency)} />
              <SummaryCard label="Tax (est.)" value={formatMoney(preview.total_tax, currency)} />
              <SummaryCard
                label="Total discount (est.)"
                value={formatMoney(preview.total_discount, currency)}
              />
              <SummaryCard label="Freight" value={formatMoney(preview.freight, currency)} />
              <SummaryCard label="Insurance" value={formatMoney(preview.insurance, currency)} />
              <SummaryCard label="Handling" value={formatMoney(preview.handling, currency)} />
              <SummaryCard label="Grand total (est.)" value={formatMoney(preview.grand_total, currency)} />
              {sale?.summary ? (
                <>
                  <SummaryCard
                    label="Saved net"
                    value={formatMoney(sale.summary.total_net, currency)}
                  />
                  <SummaryCard label="Saved tax" value={formatMoney(sale.summary.total_tax, currency)} />
                  <SummaryCard
                    label="Saved grand total"
                    value={formatMoney(sale.summary.grand_total, currency)}
                  />
                </>
              ) : null}
            </div>
          ) : null}

          {activeTabDef.isPartners ? (
            <PartnersSection
              partners={partners}
              customerId={customerId}
              watchedSalespersonId={watched.salesperson_id}
              customers={customers}
              users={users}
              register={register}
              appendPartner={appendPartner}
            />
          ) : null}

          {activeTabDef.isLineItems ? (
            <div className="space-y-4">
              <Input
                placeholder="Search products by SKU or name"
                value={productSearch}
                onChange={(e) => setProductSearch(e.target.value)}
              />
              {productsQuery.data?.items.length ? (
                <ul className="rounded border border-border text-sm">
                  {productsQuery.data.items.map((p) => (
                    <li key={p.id}>
                      <button
                        type="button"
                        className="flex w-full justify-between px-3 py-2 hover:bg-muted"
                        onClick={() => {
                          append({
                            product_id: p.id,
                            quantity: 1,
                            unit_price: p.price,
                            gross_price: p.price,
                            description: p.name,
                          })
                          setProductSearch("")
                        }}
                      >
                        <span>
                          {p.sku} — {p.name}
                        </span>
                        <span className="text-muted-foreground">Stock: {p.stock}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
              {fields.map((field, index) => (
                <div
                  key={field.id}
                  className="grid gap-2 rounded border border-border p-3 sm:grid-cols-4 lg:grid-cols-6"
                >
                  <div>
                    <Label>Line #</Label>
                    <Input value={index + 1} disabled />
                  </div>
                  <div>
                    <Label>Material / product ID</Label>
                    <Input type="number" {...register(`items.${index}.product_id`)} />
                  </div>
                  <div className="sm:col-span-2 lg:col-span-2">
                    <Label>Item description</Label>
                    <Input {...register(`items.${index}.description`)} />
                  </div>
                  <div>
                    <Label>Quantity ordered</Label>
                    <Input type="number" {...register(`items.${index}.quantity`)} />
                  </div>
                  <div>
                    <Label>Unit of measure</Label>
                    <Input {...register(`items.${index}.uom`)} placeholder="EA, KG, …" />
                  </div>
                  <div>
                    <Label>Alternate UOM</Label>
                    <Input {...register(`items.${index}.alternate_uom`)} placeholder="CS, PAL, …" />
                  </div>
                  <div>
                    <Label>UOM conversion factor</Label>
                    <Input {...register(`items.${index}.uom_conversion_factor`)} />
                  </div>
                  <div>
                    <Label>Item category</Label>
                    <Input {...register(`items.${index}.item_category`)} />
                  </div>
                  <div>
                    <Label>Product category</Label>
                    <Input {...register(`items.${index}.product_category`)} />
                  </div>
                  <div>
                    <Label>List / unit price</Label>
                    <Input {...register(`items.${index}.unit_price`)} />
                  </div>
                  <div>
                    <Label>Base / gross price</Label>
                    <Input {...register(`items.${index}.gross_price`)} />
                  </div>
                  <div>
                    <Label>Discount %</Label>
                    <Input {...register(`items.${index}.discount_percent`)} />
                  </div>
                  <div>
                    <Label>Discount amount</Label>
                    <Input {...register(`items.${index}.discount_amount`)} />
                  </div>
                  <div>
                    <Label>Tax code</Label>
                    <Input {...register(`items.${index}.tax_code`)} />
                  </div>
                  <div>
                    <Label>Tax rate</Label>
                    <Select {...register(`items.${index}.tax_rate_id`, { valueAsNumber: true })}>
                      <option value="">—</option>
                      {taxRates.map((t) => (
                        <option key={t.id} value={t.id}>
                          {t.code} ({t.rate_percent}%)
                        </option>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <Label>Plant / warehouse</Label>
                    <Select {...register(`items.${index}.warehouse_id`, { valueAsNumber: true })}>
                      <option value="">—</option>
                      {warehouses.map((w) => (
                        <option key={w.id} value={w.id}>
                          {w.code}
                        </option>
                      ))}
                    </Select>
                  </div>
                  <div>
                    <Label>Storage location ID</Label>
                    <Input
                      type="number"
                      {...register(`items.${index}.storage_location_id`, { valueAsNumber: true })}
                    />
                  </div>
                  <div>
                    <Label>Requested delivery</Label>
                    <Input type="date" {...register(`items.${index}.requested_delivery_date`)} />
                  </div>
                  <div>
                    <Label>Confirmed delivery</Label>
                    <Input type="date" {...register(`items.${index}.confirmed_delivery_date`)} />
                  </div>
                  <div>
                    <Label>Batch number</Label>
                    <Input {...register(`items.${index}.batch_number`)} />
                  </div>
                  <div>
                    <Label>Serial number</Label>
                    <Input {...register(`items.${index}.serial_number`)} />
                  </div>
                  <div>
                    <Label>Line status</Label>
                    <Input {...register(`items.${index}.line_status`)} placeholder="OPEN, …" />
                  </div>
                  <div>
                    <Label>Delivery block</Label>
                    <Input {...register(`items.${index}.delivery_block`)} />
                  </div>
                  <div>
                    <Label>Billing block</Label>
                    <Input {...register(`items.${index}.billing_block`)} />
                  </div>
                  <div>
                    <Label>Rejection reason</Label>
                    <Input {...register(`items.${index}.rejection_reason`)} />
                  </div>
                  <div>
                    <Label>Net weight</Label>
                    <Input {...register(`items.${index}.net_weight`)} />
                  </div>
                  <div>
                    <Label>Gross weight</Label>
                    <Input {...register(`items.${index}.gross_weight`)} />
                  </div>
                  <div>
                    <Label>Volume</Label>
                    <Input {...register(`items.${index}.volume`)} />
                  </div>
                  <div>
                    <Label>Substitute product ID</Label>
                    <Input
                      type="number"
                      {...register(`items.${index}.substitute_product_id`, { valueAsNumber: true })}
                    />
                  </div>
                  <div className="sm:col-span-2 lg:col-span-4">
                    <Label>Line text / notes</Label>
                    <Input {...register(`items.${index}.line_text`)} />
                  </div>
                  <div className="flex items-end">
                    <Button type="button" variant="ghost" size="sm" onClick={() => remove(index)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => append({ product_id: 0, quantity: 1 })}
              >
                <Plus className="mr-1 h-4 w-4" /> Add line
              </Button>
            </div>
          ) : null}

          {activeTabDef.isAttachments ? (
            <div className="mb-6 space-y-3">
              <h3 className="text-sm font-semibold">File attachments (metadata)</h3>
              <p className="text-sm text-muted-foreground">
                Record filename and URL for customer PO, drawings, or specifications.
              </p>
              {attachmentFields.map((field, index) => (
                <div key={field.id} className="grid gap-2 rounded border border-border p-3 sm:grid-cols-3">
                  <div>
                    <Label>Filename</Label>
                    <Input {...register(`attachments.${index}.filename`)} />
                  </div>
                  <div>
                    <Label>URL / location</Label>
                    <Input {...register(`attachments.${index}.url`)} />
                  </div>
                  <div className="flex items-end">
                    <Button type="button" variant="ghost" size="sm" onClick={() => removeAttachment(index)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => appendAttachment({ filename: "", url: "" })}
              >
                <Plus className="mr-1 h-4 w-4" /> Add attachment
              </Button>
            </div>
          ) : null}

          {activeTabDef.isWorkflowHistory && sale?.workflow_history?.length ? (
            <div className="mb-6">
              <h3 className="mb-2 text-sm font-semibold">Workflow history</h3>
              <ul className="space-y-2 text-sm">
                {sale.workflow_history.map((ev, i) => (
                  <li key={i} className="rounded border border-border px-3 py-2">
                    <span className="font-medium">{String(ev.status ?? "—")}</span>
                    {ev.at ? (
                      <span className="text-muted-foreground"> · {String(ev.at)}</span>
                    ) : null}
                    {ev.user_email ? (
                      <span className="text-muted-foreground"> · {String(ev.user_email)}</span>
                    ) : null}
                    {ev.note ? <p className="mt-1 text-muted-foreground">{String(ev.note)}</p> : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {!activeTabDef.isLineItems &&
          !activeTabDef.isSummary &&
          !activeTabDef.isAttachments &&
          activeTabDef.fields.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2">{renderDeclarativeFields()}</div>
          ) : null}
          {formState.errors.items?.message ? (
            <p className="mt-2 text-sm text-destructive">{formState.errors.items.message}</p>
          ) : null}
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-border px-4 py-3">
          <p className="text-sm text-muted-foreground">
            Est. {formatMoney(preview.grand_total, currency)} · {preview.total_items} line(s)
          </p>
          <div className="flex gap-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              data-testid="save-draft"
              disabled={saveMutation.isPending || (sale !== null && sale.order_status !== "DRAFT")}
            >
              {saveMutation.isPending ? "Saving…" : "Save draft"}
            </Button>
          </div>
        </footer>
      </form>
    </div>
  )
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-border bg-muted/30 px-3 py-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium">{value}</p>
    </div>
  )
}
