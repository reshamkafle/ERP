import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { createCustomer, updateCustomer } from "@/features/customers/customers-api"
import { customerFormSchema, type CustomerFormValues } from "@/lib/customer-schema"
import type { Customer } from "@/types/customer"

const defaultValues: CustomerFormValues = {
  name: "",
  phone: "",
  email: "",
  notes: "",
}

function customerToForm(customer: Customer): CustomerFormValues {
  return {
    name: customer.name,
    phone: customer.phone ?? "",
    email: customer.email ?? "",
    notes: customer.notes ?? "",
  }
}

type Props = {
  open: boolean
  customer: Customer | null
  onClose: () => void
}

export function CustomerFormDialog({ open, customer, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = customer !== null

  const form = useForm<CustomerFormValues>({
    resolver: zodResolver(customerFormSchema),
    defaultValues,
  })

  useEffect(() => {
    if (!open) return
    form.reset(customer ? customerToForm(customer) : defaultValues)
  }, [open, customer, form])

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
          <h2 className="text-lg font-semibold">{isEdit ? "Edit customer" : "New customer"}</h2>
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
            <Input {...register("email")} type="email" placeholder="customer@example.com" />
          </Field>
          <Field label="Notes">
            <Textarea {...register("notes")} rows={3} placeholder="Preferences, loyalty notes…" />
          </Field>
        </div>

        <div className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : isEdit ? "Save changes" : "Create customer"}
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