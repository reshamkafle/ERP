import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { createSupplier, updateSupplier } from "@/features/suppliers/suppliers-api"
import { supplierFormSchema, type SupplierFormValues } from "@/lib/supplier-schema"
import type { Supplier } from "@/types/supplier"

const defaultValues: SupplierFormValues = {
  name: "",
  phone: "",
  email: "",
  notes: "",
}

function supplierToForm(supplier: Supplier): SupplierFormValues {
  return {
    name: supplier.name,
    phone: supplier.phone ?? "",
    email: supplier.email ?? "",
    notes: supplier.notes ?? "",
  }
}

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
    defaultValues,
  })

  useEffect(() => {
    if (!open) return
    form.reset(supplier ? supplierToForm(supplier) : defaultValues)
  }, [open, supplier, form])

  const saveMutation = useMutation({
    mutationFn: (values: SupplierFormValues) =>
      isEdit && supplier ? updateSupplier(supplier.id, values) : createSupplier(values),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      toast.success(isEdit ? "Supplier updated" : "Supplier created")
      onClose()
    },
    onError: (err: unknown) => {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Could not save supplier"
      toast.error(typeof detail === "string" ? detail : "Could not save supplier")
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
        className="w-full max-w-md rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((values) => saveMutation.mutate(values))}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">{isEdit ? "Edit supplier" : "New supplier"}</h2>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
        <div className="space-y-4 p-4">
          <Field label="Name" error={formState.errors.name?.message}>
            <Input {...register("name")} autoFocus />
          </Field>
          <Field label="Phone">
            <Input {...register("phone")} inputMode="tel" placeholder="+1 555 0100" />
          </Field>
          <Field label="Email" error={formState.errors.email?.message}>
            <Input {...register("email")} type="email" placeholder="supplier@example.com" />
          </Field>
          <Field label="Notes">
            <Textarea {...register("notes")} rows={3} placeholder="Payment terms, lead times…" />
          </Field>
        </div>
        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create supplier"}
          </Button>
        </div>
      </form>
    </div>
  )
}

function Field({
  label,
  error,
  children,
}: {
  label: string
  error?: string
  children: React.ReactNode
}) {
  return (
    <div>
      <Label className="mb-1 block">{label}</Label>
      {children}
      {error ? <p className="mt-1 text-xs text-destructive">{error}</p> : null}
    </div>
  )
}
