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
import {
  createSupplier,
  supplierFormToPayload,
  updateSupplier,
} from "@/features/suppliers/suppliers-api"
import {
  APPROVAL_STATUS_OPTIONS,
  defaultSupplierFormValues,
  newVendorCodeSuggestion,
  supplierFormSchema,
  supplierToForm,
  VENDOR_TYPE_OPTIONS,
  type SupplierFormValues,
} from "@/lib/supplier-schema"
import type { Supplier } from "@/types/supplier"

type Props = {
  open: boolean
  supplier: Supplier | null
  onClose: () => void
}

export function SupplierFormDialog({ open, supplier, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = supplier !== null

  const form = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierFormSchema),
    defaultValues: defaultSupplierFormValues,
  })

  useEffect(() => {
    if (!open) return
    if (supplier) {
      form.reset(supplierToForm(supplier))
      return
    }
    form.reset({
      ...defaultSupplierFormValues,
      vendor_code: newVendorCodeSuggestion(),
    })
  }, [open, supplier, form])

  const saveMutation = useMutation({
    mutationFn: (values: SupplierFormValues) => {
      const payload = supplierFormToPayload(values)
      return isEdit && supplier
        ? updateSupplier(supplier.id, payload)
        : createSupplier(payload)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      toast.success(isEdit ? "Vendor updated" : "Vendor created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save vendor"
      toast.error(typeof detail === "string" ? detail : "Could not save vendor")
    },
  })

  if (!open) return null

  const { register, handleSubmit, formState } = form

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
          <h2 className="text-lg font-semibold">{isEdit ? "Edit vendor" : "New vendor"}</h2>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>

        <div className="max-h-[min(70vh,720px)] overflow-y-auto p-4 space-y-6">
          <Section title="Identity">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Vendor code / ID" error={formState.errors.vendor_code?.message}>
                <Input {...register("vendor_code")} className="font-mono" autoFocus />
              </Field>
              <Field label="Vendor name (display)" error={formState.errors.name?.message}>
                <Input {...register("name")} />
              </Field>
              <Field label="Legal name">
                <Input {...register("legal_name")} />
              </Field>
              <Field label="DBA">
                <Input {...register("dba")} />
              </Field>
            </div>
          </Section>

          <Section title="Contact">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Address line 1" className="sm:col-span-2">
                <Input {...register("address_line1")} />
              </Field>
              <Field label="Address line 2" className="sm:col-span-2">
                <Input {...register("address_line2")} />
              </Field>
              <Field label="City">
                <Input {...register("city")} />
              </Field>
              <Field label="State / Province">
                <Input {...register("state")} />
              </Field>
              <Field label="Postal code">
                <Input {...register("postal_code")} />
              </Field>
              <Field label="Country">
                <Input {...register("country")} />
              </Field>
              <Field label="Phone">
                <Input {...register("phone")} inputMode="tel" />
              </Field>
              <Field label="Email" error={formState.errors.email?.message}>
                <Input {...register("email")} type="email" />
              </Field>
              <Field label="Website" className="sm:col-span-2">
                <Input {...register("website")} type="url" placeholder="https://" />
              </Field>
            </div>
          </Section>

          <Section title="Tax & payment terms">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Tax ID / GST / VAT / PAN">
                <Input {...register("tax_id")} />
              </Field>
              <Field label="Payment terms">
                <Input {...register("payment_terms")} placeholder="Net 30, 2% 10" />
              </Field>
              <Field label="Incoterms">
                <Input {...register("incoterms")} placeholder="FOB, CIF, DDP" />
              </Field>
            </div>
          </Section>

          <Section title="Bank details">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Account number">
                <Input {...register("bank_details.account_number")} />
              </Field>
              <Field label="Beneficiary name">
                <Input {...register("bank_details.beneficiary_name")} />
              </Field>
              <Field label="IFSC">
                <Input {...register("bank_details.ifsc")} />
              </Field>
              <Field label="SWIFT">
                <Input {...register("bank_details.swift")} />
              </Field>
            </div>
          </Section>

          <Section title="Classification & performance">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Vendor category">
                <Input {...register("vendor_category")} placeholder="Raw materials, MRO…" />
              </Field>
              <Field label="Vendor type">
                <Select {...register("vendor_type")}>
                  {VENDOR_TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value || "none"} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Approval status">
                <Select {...register("approval_status")}>
                  {APPROVAL_STATUS_OPTIONS.map((opt) => (
                    <option key={opt.value || "none"} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </Field>
              <Field label="Performance rating (0–100)">
                <Input {...register("performance_rating")} inputMode="decimal" />
              </Field>
            </div>
          </Section>

          <Section title="Operations">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Lead time (days)">
                <Input {...register("lead_time_days")} inputMode="numeric" />
              </Field>
              <Field label="Minimum order quantity (MOQ)">
                <Input {...register("moq")} inputMode="decimal" />
              </Field>
              <Field label="Currency">
                <Input {...register("currency_code")} maxLength={3} className="uppercase" />
              </Field>
              <Field label="Pricing currency">
                <Input {...register("pricing_currency")} maxLength={3} className="uppercase" />
              </Field>
            </div>
          </Section>

          <Section title="Documents">
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="W9 / tax form ref">
                <Input {...register("documents.w9")} />
              </Field>
              <Field label="Certificate of incorporation">
                <Input {...register("documents.certificate_of_incorporation")} />
              </Field>
              <Field label="Insurance">
                <Input {...register("documents.insurance")} />
              </Field>
              <Field label="Other attachment ref">
                <Textarea {...register("documents.other")} rows={2} />
              </Field>
            </div>
          </Section>
        </div>

        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create vendor"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3">
      <h3 className="text-sm font-semibold">{title}</h3>
      {children}
    </section>
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
      <Label className="mb-1 block text-xs">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}
