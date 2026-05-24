import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"
import { useFieldArray, useForm, type UseFormRegister } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createCustomer,
  customerToForm,
  fetchChartOfAccounts,
  fetchCustomers,
  updateCustomer,
} from "@/features/customers/customers-api"
import { fetchSaleLookups } from "@/features/sales/sales-api"
import {
  CUSTOMER_FORM_TABS,
  type CustomerFieldDef,
} from "@/lib/customer-field-groups"
import {
  CUSTOMER_ADDRESS_TYPES,
  customerFormSchema,
  defaultCustomerFormValues,
  newCustomerCodeSuggestion,
  type CustomerFormValues,
} from "@/lib/customer-schema"
import { cn } from "@/lib/utils"
import type { Customer } from "@/types/customer"

type Props = {
  open: boolean
  customer: Customer | null
  onClose: () => void
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      {children}
    </div>
  )
}

function Field({
  label,
  error,
  children,
  className,
}: {
  label: string
  error?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={className}>
      <Label className="text-xs text-muted-foreground">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}

function TabFieldInput({
  field,
  register,
  errors,
}: {
  field: CustomerFieldDef
  register: UseFormRegister<CustomerFormValues>
  errors: Record<string, { message?: string } | undefined>
}) {
  const path = field.path as keyof CustomerFormValues
  const err = errors[path as string]

  if (field.type === "checkbox") {
    return (
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" {...register(path as "tax_exempt")} />
        {field.label}
      </label>
    )
  }
  if (field.type === "textarea") {
    return <Textarea {...register(path)} rows={3} />
  }
  if (field.type === "select" && field.options) {
    return (
      <Select {...register(path)}>
        {field.options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </Select>
    )
  }
  if (String(field.path).includes(".")) {
    return (
      <Input
        type={field.type === "number" ? "number" : "text"}
        {...register(field.path as Parameters<typeof register>[0])}
        placeholder={field.placeholder}
      />
    )
  }
  return (
    <Input
      type={field.type === "number" ? "number" : "text"}
      {...register(path)}
      placeholder={field.placeholder}
      className={path === "customer_code" ? "font-mono" : undefined}
    />
  )
}

export function CustomerFormDialog({ open, customer, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = customer !== null
  const [activeTab, setActiveTab] = useState(CUSTOMER_FORM_TABS[0].id)

  const form = useForm<CustomerFormValues>({
    resolver: zodResolver(customerFormSchema),
    defaultValues: defaultCustomerFormValues,
  })

  const { register, handleSubmit, control, setValue, formState, getValues } = form
  const contactsArray = useFieldArray({ control, name: "contacts" })
  const addressesArray = useFieldArray({ control, name: "addresses" })
  const salesAreasArray = useFieldArray({ control, name: "sales_areas" })
  const customFieldsArray = useFieldArray({ control, name: "extended_data.custom_fields" })

  const customersQuery = useQuery({
    queryKey: ["customers", "list", "picker"],
    queryFn: () => fetchCustomers({ limit: 200 }),
    enabled: open,
  })

  const coaQuery = useQuery({
    queryKey: ["chart-of-accounts"],
    queryFn: fetchChartOfAccounts,
    enabled: open && activeTab === "commercial",
  })

  useEffect(() => {
    if (!open) return
    if (customer) {
      form.reset(customerToForm(customer))
    } else {
      form.reset({
        ...defaultCustomerFormValues,
        customer_code: newCustomerCodeSuggestion(),
      })
    }
    setActiveTab("account")
  }, [open, customer, form])

  const lookupsQuery = useQuery({
    queryKey: ["sales", "lookups"],
    queryFn: fetchSaleLookups,
    enabled: open,
  })
  const users = lookupsQuery.data?.users ?? []

  const saveMutation = useMutation({
    mutationFn: (values: CustomerFormValues) =>
      isEdit && customer ? updateCustomer(customer.id, values) : createCustomer(values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["customers"] })
      toast.success(isEdit ? "Customer updated" : "Customer created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save customer"
      toast.error(typeof detail === "string" ? detail : "Could not save customer")
    },
  })

  const copyBillingToShipping = () => {
    const v = getValues()
    setValue("shipping_address_line1", v.billing_address_line1)
    setValue("shipping_address_line2", v.billing_address_line2)
    setValue("shipping_city", v.billing_city)
    setValue("shipping_state", v.billing_state)
    setValue("shipping_postal_code", v.billing_postal_code)
    setValue("shipping_country", v.billing_country)
    toast.success("Copied billing address to shipping")
  }

  if (!open) return null

  const tab = CUSTOMER_FORM_TABS.find((t) => t.id === activeTab)
  const parentOptions = (customersQuery.data?.items ?? []).filter(
    (c) => !customer || c.id !== customer.id,
  )

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
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">{isEdit ? "Edit customer" : "New customer"}</h2>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>

        <div className="flex flex-wrap gap-1 border-b border-border px-4 py-2">
          {CUSTOMER_FORM_TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={cn(
                "rounded-md px-3 py-1.5 text-sm",
                activeTab === t.id
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted",
              )}
              onClick={() => setActiveTab(t.id)}
            >
              {t.title}
            </button>
          ))}
        </div>

        <div className="max-h-[min(70vh,720px)] overflow-y-auto p-4 space-y-6">
          {tab &&
          !["contact_address", "integrations", "marketing", "service", "analytics", "sales"].includes(
            activeTab,
          ) ? (
            <Section title={tab.title}>
              {tab.description ? (
                <p className="text-xs text-muted-foreground">{tab.description}</p>
              ) : null}
              <div className="grid gap-3 sm:grid-cols-2">
                {tab.fields.map((field) => {
                  if (field.path === "parent_customer_id") {
                    return (
                      <Field key={field.path} label="Parent company" className="sm:col-span-2">
                        <Select {...register("parent_customer_id")}>
                          <option value="">— None —</option>
                          {parentOptions.map((c) => (
                            <option key={c.id} value={String(c.id)}>
                              {c.customer_code ? `${c.customer_code} · ` : ""}
                              {c.name}
                            </option>
                          ))}
                        </Select>
                      </Field>
                    )
                  }
                  if (field.path === "account_owner_id") {
                    return (
                      <Field key={field.path} label="Account owner">
                        <Select {...register("account_owner_id")}>
                          <option value="">—</option>
                          {users.map((u) => (
                            <option key={u.id} value={String(u.id)}>
                              {u.email}
                            </option>
                          ))}
                        </Select>
                      </Field>
                    )
                  }
                  if (field.path === "reconciliation_account_id") {
                    return (
                      <Field key={field.path} label="Reconciliation account (AR)">
                        <Select {...register("reconciliation_account_id")}>
                          <option value="">—</option>
                          {(coaQuery.data ?? []).map((a) => (
                            <option key={a.id} value={String(a.id)}>
                              {a.code} — {a.name}
                            </option>
                          ))}
                        </Select>
                      </Field>
                    )
                  }
                  const path = field.path as keyof CustomerFormValues
                  const err = formState.errors[path as string]
                  return (
                    <Field
                      key={field.path}
                      label={field.label}
                      error={err?.message as string | undefined}
                      className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                    >
                      <TabFieldInput field={field} register={register} errors={formState.errors} />
                    </Field>
                  )
                })}
              </div>
            </Section>
          ) : null}

          {activeTab === "contact_address" ? (
            <>
              <Section title="Contact & Address">
                <div className="grid gap-3 sm:grid-cols-2">
                  {CUSTOMER_FORM_TABS.find((t) => t.id === "contact_address")!.fields.map((field) => {
                    const path = field.path as keyof CustomerFormValues
                    const err = formState.errors[path as string]
                    return (
                      <Field
                        key={field.path}
                        label={field.label}
                        error={err?.message as string | undefined}
                        className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                      >
                        <TabFieldInput
                          field={field}
                          register={register}
                          errors={formState.errors}
                        />
                      </Field>
                    )
                  })}
                </div>
                <Button type="button" variant="outline" size="sm" onClick={copyBillingToShipping}>
                  Copy billing → shipping
                </Button>
              </Section>

              <Section title="Contact persons">
                {contactsArray.fields.map((row, index) => (
                  <div
                    key={row.id}
                    className="grid gap-2 rounded-md border border-border p-3 sm:grid-cols-2"
                  >
                    <Input placeholder="Contact ID" {...register(`contacts.${index}.contact_code`)} />
                    <Input placeholder="Salutation" {...register(`contacts.${index}.salutation`)} />
                    <Input placeholder="First name" {...register(`contacts.${index}.first_name`)} />
                    <Input placeholder="Middle name" {...register(`contacts.${index}.middle_name`)} />
                    <Input placeholder="Last name" {...register(`contacts.${index}.last_name`)} />
                    <Input placeholder="Display name" {...register(`contacts.${index}.name`)} />
                    <Input placeholder="Email" {...register(`contacts.${index}.email`)} />
                    <Input placeholder="Secondary email" {...register(`contacts.${index}.email_secondary`)} />
                    <Input placeholder="Phone" {...register(`contacts.${index}.phone`)} />
                    <Input placeholder="Secondary phone" {...register(`contacts.${index}.phone_secondary`)} />
                    <Input placeholder="Title" {...register(`contacts.${index}.title`)} />
                    <Input placeholder="Department" {...register(`contacts.${index}.department`)} />
                    <Input placeholder="Contact type / role" {...register(`contacts.${index}.role`)} />
                    <Input placeholder="LinkedIn URL" {...register(`contacts.${index}.linkedin_url`)} />
                    <Input placeholder="Preferred language" {...register(`contacts.${index}.preferred_language`)} />
                    <Input placeholder="Birthday (YYYY-MM-DD)" {...register(`contacts.${index}.birthday`)} />
                    <Input placeholder="Anniversary" {...register(`contacts.${index}.anniversary`)} />
                    <Input placeholder="Notes" className="sm:col-span-2" {...register(`contacts.${index}.notes`)} />
                    <div className="flex items-center gap-2 sm:col-span-2">
                      <label className="flex items-center gap-1 text-xs">
                        <input type="checkbox" {...register(`contacts.${index}.is_primary`)} />
                        Primary
                      </label>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => contactsArray.remove(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    contactsArray.append({
                      contact_code: "",
                      salutation: "",
                      first_name: "",
                      middle_name: "",
                      last_name: "",
                      name: "",
                      email: "",
                      email_secondary: "",
                      phone: "",
                      phone_secondary: "",
                      title: "",
                      department: "",
                      role: "",
                      preferred_language: "",
                      linkedin_url: "",
                      birthday: "",
                      anniversary: "",
                      notes: "",
                      is_primary: contactsArray.fields.length === 0,
                    })
                  }
                >
                  <Plus className="mr-1 h-4 w-4" />
                  Add contact
                </Button>
              </Section>

              <Section title="Additional addresses">
                {addressesArray.fields.map((row, index) => (
                  <div
                    key={row.id}
                    className="space-y-2 rounded-md border border-border p-3"
                  >
                    <div className="grid gap-2 sm:grid-cols-3">
                      <Select {...register(`addresses.${index}.address_type`)}>
                        {CUSTOMER_ADDRESS_TYPES.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </Select>
                      <Input placeholder="Label" {...register(`addresses.${index}.label`)} />
                      <label className="flex items-center gap-1 text-xs">
                        <input
                          type="checkbox"
                          {...register(`addresses.${index}.is_default`)}
                        />
                        Default
                      </label>
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      <Input placeholder="Line 1" {...register(`addresses.${index}.line1`)} />
                      <Input placeholder="House no." {...register(`addresses.${index}.house_no`)} />
                      <Input placeholder="City" {...register(`addresses.${index}.city`)} />
                      <Input placeholder="State" {...register(`addresses.${index}.state`)} />
                      <Input
                        placeholder="Postal code"
                        {...register(`addresses.${index}.postal_code`)}
                      />
                      <Input placeholder="Country" {...register(`addresses.${index}.country`)} />
                      <Input placeholder="Latitude" {...register(`addresses.${index}.latitude`)} />
                      <Input placeholder="Longitude" {...register(`addresses.${index}.longitude`)} />
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => addressesArray.remove(index)}
                    >
                      <Trash2 className="mr-1 h-4 w-4" />
                      Remove address
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    addressesArray.append({
                      address_type: "SHIPPING",
                      label: "",
                      line1: "",
                      line2: "",
                      house_no: "",
                      city: "",
                      state: "",
                      postal_code: "",
                      country: "",
                      latitude: "",
                      longitude: "",
                      is_default: false,
                    })
                  }
                >
                  <Plus className="mr-1 h-4 w-4" />
                  Add address
                </Button>
              </Section>
            </>
          ) : null}

          {activeTab === "sales" ? (
            <Section title="Sales areas">
              <p className="text-xs text-muted-foreground">
                Organizational sales data (sales org, channel, division). Header fields are on the
                Sales Area tab above.
              </p>
              {salesAreasArray.fields.map((row, index) => (
                <div
                  key={row.id}
                  className="grid gap-2 rounded-md border border-border p-3 sm:grid-cols-2"
                >
                  <Input
                    placeholder="Sales org *"
                    {...register(`sales_areas.${index}.sales_org`)}
                  />
                  <Input
                    placeholder="Distribution channel"
                    {...register(`sales_areas.${index}.distribution_channel`)}
                  />
                  <Input placeholder="Division" {...register(`sales_areas.${index}.division`)} />
                  <Input
                    placeholder="Credit limit"
                    type="number"
                    {...register(`sales_areas.${index}.credit_limit`)}
                  />
                  <Input
                    placeholder="Payment terms"
                    {...register(`sales_areas.${index}.payment_terms`)}
                  />
                  <Input
                    placeholder="Pricing procedure"
                    {...register(`sales_areas.${index}.pricing_procedure`)}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => salesAreasArray.remove(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() =>
                  salesAreasArray.append({
                    sales_org: "",
                    distribution_channel: "",
                    division: "",
                    credit_limit: "",
                    payment_terms: "",
                    pricing_procedure: "",
                  })
                }
              >
                <Plus className="mr-1 h-4 w-4" />
                Add sales area
              </Button>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {CUSTOMER_FORM_TABS.find((t) => t.id === "sales")!.fields.map((field) => (
                  <Field key={field.path} label={field.label}>
                    <TabFieldInput
                      field={field}
                      register={register}
                      errors={formState.errors}
                    />
                  </Field>
                ))}
              </div>
            </Section>
          ) : null}

          {activeTab === "integrations" ? (
            <Section title="System & integrations">
              <div className="grid gap-3 sm:grid-cols-2">
                {CUSTOMER_FORM_TABS.find((t) => t.id === "integrations")!.fields.map((field) => (
                  <Field
                    key={field.path}
                    label={field.label}
                    className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                  >
                    <TabFieldInput field={field} register={register} errors={formState.errors} />
                  </Field>
                ))}
              </div>
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Consent / privacy</p>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.marketing")} />
                  Marketing consent
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.gdpr")} />
                  GDPR consent recorded
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.ccpa")} />
                  CCPA consent recorded
                </label>
              </div>
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Custom fields</p>
                {customFieldsArray.fields.map((row, index) => (
                  <div key={row.id} className="flex gap-2">
                    <Input placeholder="Key" {...register(`extended_data.custom_fields.${index}.key`)} />
                    <Input
                      placeholder="Value"
                      {...register(`extended_data.custom_fields.${index}.value`)}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => customFieldsArray.remove(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => customFieldsArray.append({ key: "", value: "" })}
                >
                  <Plus className="mr-1 h-4 w-4" />
                  Add custom field
                </Button>
              </div>
            </Section>
          ) : null}

          {activeTab === "marketing" ? (
            <Section title="Marketing & consent">
              <div className="grid gap-3 sm:grid-cols-2">
                {CUSTOMER_FORM_TABS.find((t) => t.id === "marketing")!.fields.map((field) => (
                  <Field
                    key={field.path}
                    label={field.label}
                    className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                  >
                    <TabFieldInput field={field} register={register} errors={formState.errors} />
                  </Field>
                ))}
              </div>
              <div className="space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Consent / privacy</p>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.marketing")} />
                  Marketing consent
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.gdpr")} />
                  GDPR consent recorded
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" {...register("extended_data.consent_flags.ccpa")} />
                  CCPA consent recorded
                </label>
              </div>
            </Section>
          ) : null}

          {activeTab === "service" ? (
            <Section title="Service & support">
              <div className="grid gap-3 sm:grid-cols-2">
                {CUSTOMER_FORM_TABS.find((t) => t.id === "service")!.fields.map((field) => (
                  <Field
                    key={field.path}
                    label={field.label}
                    className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                  >
                    <TabFieldInput field={field} register={register} errors={formState.errors} />
                  </Field>
                ))}
              </div>
            </Section>
          ) : null}

          {activeTab === "analytics" ? (
            <Section title="Segmentation & analytics">
              <div className="grid gap-3 sm:grid-cols-2">
                {CUSTOMER_FORM_TABS.find((t) => t.id === "analytics")!.fields.map((field) => (
                  <Field
                    key={field.path}
                    label={field.label}
                    className={field.colSpan === 2 ? "sm:col-span-2" : undefined}
                  >
                    <TabFieldInput field={field} register={register} errors={formState.errors} />
                  </Field>
                ))}
              </div>
            </Section>
          ) : null}
        </div>

        <footer className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save" : "Create"}
          </Button>
        </footer>
      </form>
    </div>
  )
}
