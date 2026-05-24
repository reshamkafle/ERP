import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  createModuleRecord,
  fetchModuleRecord,
  updateModuleRecord,
} from "@/features/modules/modules-api"
import {
  CRM_MODULE_CODE,
  CRM_STATUS_OPTIONS,
  crmFormToExtraData,
  crmModuleRecordSchema,
  crmRecordToForm,
  type CrmModuleRecordFormValues,
} from "@/lib/crm-record-schema"

type Props = {
  open: boolean
  editingId: number | null
  defaultFeatureCode: string
  onClose: () => void
}

const defaultValues: CrmModuleRecordFormValues = {
  feature_code: "marketing_campaigns",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  party_name: "",
  amount: "",
  quantity: "",
  start_date: "",
  end_date: "",
  campaign_channel: "",
  campaign_segment: "",
  case_type: "",
  sla_hours: "",
  ticket_category: "",
}

export function CrmRecordFormDialog({ open, editingId, defaultFeatureCode, onClose }: Props) {
  const queryClient = useQueryClient()
  const isEdit = editingId !== null

  const form = useForm<CrmModuleRecordFormValues>({
    resolver: zodResolver(crmModuleRecordSchema),
    defaultValues: { ...defaultValues, feature_code: defaultFeatureCode },
  })

  const recordQuery = useQuery({
    queryKey: ["erp-modules", CRM_MODULE_CODE, "record", editingId],
    queryFn: () => fetchModuleRecord(CRM_MODULE_CODE, editingId!),
    enabled: open && isEdit,
  })

  useEffect(() => {
    if (!open) return
    if (isEdit && recordQuery.data) {
      form.reset(crmRecordToForm(recordQuery.data))
    } else {
      form.reset({ ...defaultValues, feature_code: defaultFeatureCode })
    }
  }, [open, isEdit, recordQuery.data, defaultFeatureCode, form])

  const saveMutation = useMutation({
    mutationFn: async (values: CrmModuleRecordFormValues) => {
      const body = {
        feature_code: values.feature_code,
        reference: values.reference?.trim() || `CRM-${Date.now()}`,
        title: values.title.trim(),
        status: values.status,
        description: values.description?.trim() || null,
        party_name: values.party_name?.trim() || null,
        amount: values.amount?.trim() ? values.amount.trim() : null,
        quantity: values.quantity?.trim() ? Number(values.quantity) : null,
        start_date: values.start_date?.trim() || null,
        end_date: values.end_date?.trim() || null,
        extra_data: crmFormToExtraData(values),
      }
      if (isEdit && editingId) {
        return updateModuleRecord(CRM_MODULE_CODE, editingId, body)
      }
      return createModuleRecord(CRM_MODULE_CODE, body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["erp-modules", CRM_MODULE_CODE] })
      toast.success(isEdit ? "Record updated" : "Record created")
      onClose()
    },
    onError: () => toast.error("Could not save record"),
  })

  if (!open) return null

  const { register, handleSubmit, watch } = form
  const feature = watch("feature_code")

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4">
      <form
        className="my-8 w-full max-w-lg rounded-xl border border-border bg-card shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <header className="border-b border-border px-4 py-3">
          <h2 className="text-lg font-semibold">{isEdit ? "Edit CRM record" : "New CRM record"}</h2>
        </header>
        <div className="space-y-3 p-4">
          <div>
            <Label>Feature</Label>
            <Select {...register("feature_code")} disabled={isEdit}>
              <option value="marketing_campaigns">Marketing campaign</option>
              <option value="customer_service">Customer service case</option>
              <option value="support_tickets">Support ticket</option>
            </Select>
          </div>
          <div>
            <Label>Title *</Label>
            <Input {...register("title")} />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label>Reference</Label>
              <Input {...register("reference")} />
            </div>
            <div>
              <Label>Status</Label>
              <Select {...register("status")}>
                {CRM_STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </Select>
            </div>
          </div>
          {feature === "marketing_campaigns" ? (
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label>Channel</Label>
                <Input {...register("campaign_channel")} />
              </div>
              <div>
                <Label>Segment</Label>
                <Input {...register("campaign_segment")} />
              </div>
            </div>
          ) : null}
          {feature === "customer_service" ? (
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label>Case type</Label>
                <Input {...register("case_type")} />
              </div>
              <div>
                <Label>SLA (hours)</Label>
                <Input {...register("sla_hours")} />
              </div>
            </div>
          ) : null}
          {feature === "support_tickets" ? (
            <div>
              <Label>Category</Label>
              <Input {...register("ticket_category")} />
            </div>
          ) : null}
          <div>
            <Label>Description</Label>
            <Textarea {...register("description")} rows={3} />
          </div>
        </div>
        <footer className="flex justify-end gap-2 border-t border-border px-4 py-3">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            {saveMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </footer>
      </form>
    </div>
  )
}
