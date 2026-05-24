import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createCustomerActivity,
  fetchCustomerContacts,
  updateCustomerActivity,
} from "@/features/crm/crm-api"
import type { CrmActivity, CrmActivityType } from "@/types/crm"

const ACTIVITY_TYPES: CrmActivityType[] = [
  "CALL",
  "EMAIL",
  "MEETING",
  "NOTE",
  "VISIT",
  "TASK",
  "DEMO",
  "SITE_VISIT",
]

const schema = z.object({
  activity_type: z.enum(ACTIVITY_TYPES as [CrmActivityType, ...CrmActivityType[]]),
  subject: z.string().min(1),
  body: z.string().optional(),
  occurred_at: z.string().min(1),
  contact_id: z.string().optional(),
  duration_minutes: z.string().optional(),
  outcome: z.string().optional(),
  next_follow_up_at: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

type Props = {
  open: boolean
  customerId: number
  activity: CrmActivity | null
  onClose: () => void
}

function toLocalInput(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export function ActivityFormDialog({ open, customerId, activity, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = activity !== null
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { activity_type: "CALL", occurred_at: toLocalInput(new Date().toISOString()) },
  })

  const contactsQuery = useQuery({
    queryKey: ["customers", customerId, "contacts"],
    queryFn: () => fetchCustomerContacts(customerId),
    enabled: open,
  })

  useEffect(() => {
    if (!open) return
    form.reset(
      activity
        ? {
            activity_type: activity.activity_type,
            subject: activity.subject,
            body: activity.body ?? "",
            occurred_at: toLocalInput(activity.occurred_at),
            contact_id: activity.contact_id ? String(activity.contact_id) : "",
            duration_minutes: activity.duration_minutes != null ? String(activity.duration_minutes) : "",
            outcome: activity.outcome ?? "",
            next_follow_up_at: activity.next_follow_up_at
              ? toLocalInput(activity.next_follow_up_at)
              : "",
          }
        : {
            activity_type: "CALL",
            subject: "",
            occurred_at: toLocalInput(new Date().toISOString()),
          },
    )
  }, [open, activity, form])

  const saveMutation = useMutation({
    mutationFn: (values: FormValues) => {
      const body = {
        activity_type: values.activity_type,
        subject: values.subject,
        body: values.body || null,
        occurred_at: new Date(values.occurred_at).toISOString(),
        contact_id: values.contact_id ? Number(values.contact_id) : null,
        duration_minutes: values.duration_minutes ? Number(values.duration_minutes) : null,
        outcome: values.outcome || null,
        next_follow_up_at: values.next_follow_up_at
          ? new Date(values.next_follow_up_at).toISOString()
          : null,
      }
      return isEdit && activity
        ? updateCustomerActivity(customerId, activity.id, body)
        : createCustomerActivity(customerId, body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["customers", customerId, "activities"] })
      toast.success(isEdit ? "Activity updated" : "Activity logged")
      onClose()
    },
    onError: () => toast.error("Could not save activity"),
  })

  if (!open) return null

  const { register, handleSubmit } = form

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form
        className="w-full max-w-lg rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="text-lg font-semibold">{isEdit ? "Edit activity" : "Log activity"}</h2>
        <div className="mt-4 space-y-3">
          <div>
            <Label className="text-xs">Type</Label>
            <Select {...register("activity_type")}>
              {ACTIVITY_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label className="text-xs">Subject *</Label>
            <Input {...register("subject")} />
          </div>
          <div>
            <Label className="text-xs">Date & time *</Label>
            <Input type="datetime-local" {...register("occurred_at")} />
          </div>
          <div>
            <Label className="text-xs">Duration (minutes)</Label>
            <Input type="number" {...register("duration_minutes")} />
          </div>
          <div>
            <Label className="text-xs">Contact</Label>
            <Select {...register("contact_id")}>
              <option value="">—</option>
              {(contactsQuery.data ?? []).map((c) => (
                <option key={c.id} value={String(c.id)}>
                  {c.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label className="text-xs">Outcome</Label>
            <Input {...register("outcome")} />
          </div>
          <div>
            <Label className="text-xs">Next follow-up</Label>
            <Input type="datetime-local" {...register("next_follow_up_at")} />
          </div>
          <div>
            <Label className="text-xs">Notes</Label>
            <Textarea rows={3} {...register("body")} />
          </div>
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
