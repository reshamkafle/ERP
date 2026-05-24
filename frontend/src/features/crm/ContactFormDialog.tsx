import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { createCustomerContact, updateCustomerContact } from "@/features/crm/crm-api"
import type { CustomerContact } from "@/types/crm"

const schema = z.object({
  contact_code: z.string().optional(),
  salutation: z.string().optional(),
  first_name: z.string().optional(),
  middle_name: z.string().optional(),
  last_name: z.string().optional(),
  name: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  email_secondary: z.string().email().optional().or(z.literal("")),
  phone: z.string().optional(),
  phone_secondary: z.string().optional(),
  title: z.string().optional(),
  department: z.string().optional(),
  role: z.string().optional(),
  preferred_language: z.string().optional(),
  linkedin_url: z.string().optional(),
  birthday: z.string().optional(),
  anniversary: z.string().optional(),
  notes: z.string().optional(),
  is_primary: z.boolean().optional(),
})

type FormValues = z.infer<typeof schema>

type Props = {
  open: boolean
  customerId: number
  contact: CustomerContact | null
  onClose: () => void
}

export function ContactFormDialog({ open, customerId, contact, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = contact !== null
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {},
  })

  useEffect(() => {
    if (!open) return
    form.reset(
      contact
        ? {
            contact_code: contact.contact_code ?? "",
            salutation: contact.salutation ?? "",
            first_name: contact.first_name ?? "",
            middle_name: contact.middle_name ?? "",
            last_name: contact.last_name ?? "",
            name: contact.name,
            email: contact.email ?? "",
            email_secondary: contact.email_secondary ?? "",
            phone: contact.phone ?? "",
            phone_secondary: contact.phone_secondary ?? "",
            title: contact.title ?? "",
            department: contact.department ?? "",
            role: contact.role ?? "",
            preferred_language: contact.preferred_language ?? "",
            linkedin_url: contact.linkedin_url ?? "",
            birthday: contact.birthday ?? "",
            anniversary: contact.anniversary ?? "",
            notes: contact.notes ?? "",
            is_primary: contact.is_primary,
          }
        : { is_primary: false },
    )
  }, [open, contact, form])

  const saveMutation = useMutation({
    mutationFn: (values: FormValues) => {
      const body = {
        ...values,
        email: values.email || null,
        email_secondary: values.email_secondary || null,
        birthday: values.birthday || null,
        anniversary: values.anniversary || null,
      }
      return isEdit && contact
        ? updateCustomerContact(customerId, contact.id, body)
        : createCustomerContact(customerId, body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["customers", customerId, "contacts"] })
      void queryClient.invalidateQueries({ queryKey: ["crm", "contacts"] })
      toast.success(isEdit ? "Contact updated" : "Contact created")
      onClose()
    },
    onError: () => toast.error("Could not save contact"),
  })

  if (!open) return null

  const { register, handleSubmit } = form

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form
        className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="text-lg font-semibold">{isEdit ? "Edit contact" : "New contact"}</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div>
            <Label className="text-xs">Contact ID</Label>
            <Input {...register("contact_code")} />
          </div>
          <div>
            <Label className="text-xs">Salutation</Label>
            <Input {...register("salutation")} />
          </div>
          <div>
            <Label className="text-xs">First name</Label>
            <Input {...register("first_name")} />
          </div>
          <div>
            <Label className="text-xs">Last name</Label>
            <Input {...register("last_name")} />
          </div>
          <div className="sm:col-span-2">
            <Label className="text-xs">Display name</Label>
            <Input {...register("name")} />
          </div>
          <div>
            <Label className="text-xs">Email</Label>
            <Input type="email" {...register("email")} />
          </div>
          <div>
            <Label className="text-xs">Secondary email</Label>
            <Input type="email" {...register("email_secondary")} />
          </div>
          <div>
            <Label className="text-xs">Phone</Label>
            <Input {...register("phone")} />
          </div>
          <div>
            <Label className="text-xs">Title / role</Label>
            <Input {...register("title")} />
          </div>
          <div className="sm:col-span-2">
            <Label className="text-xs">LinkedIn</Label>
            <Input {...register("linkedin_url")} />
          </div>
          <div className="sm:col-span-2">
            <Label className="text-xs">Notes</Label>
            <Textarea rows={2} {...register("notes")} />
          </div>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input type="checkbox" {...register("is_primary")} />
            Primary contact
          </label>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </div>
      </form>
    </div>
  )
}
