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
import { fetchCustomers } from "@/features/customers/customers-api"
import { createLead, createOpportunity, fetchLeads, updateLead, updateOpportunity } from "@/features/crm/crm-api"
import { fetchSaleLookups } from "@/features/sales/sales-api"
import type { CrmLead, CrmOpportunity, LeadStatus, OpportunityStage } from "@/types/crm"

const LEAD_STATUSES: LeadStatus[] = [
  "NEW",
  "CONTACTED",
  "QUALIFIED",
  "UNQUALIFIED",
  "CONVERTED",
  "LOST",
]

const OPP_STAGES: OpportunityStage[] = [
  "PROSPECTING",
  "QUALIFICATION",
  "PROPOSAL",
  "NEGOTIATION",
  "CLOSED_WON",
  "CLOSED_LOST",
]

const leadSchema = z.object({
  company_name: z.string().min(1),
  contact_name: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  source: z.string().optional(),
  status: z.enum(LEAD_STATUSES as [LeadStatus, ...LeadStatus[]]),
  owner_id: z.string().optional(),
  lead_score: z.string().optional(),
  campaign_source: z.string().optional(),
  expected_close_date: z.string().optional(),
  bant_budget: z.string().optional(),
  bant_authority: z.string().optional(),
  bant_need: z.string().optional(),
  bant_timeline: z.string().optional(),
  description: z.string().optional(),
})

const oppSchema = z.object({
  customer_id: z.coerce.number().min(1, "Customer is required"),
  title: z.string().min(1),
  stage: z.enum(OPP_STAGES as [OpportunityStage, ...OpportunityStage[]]),
  probability: z.coerce.number().min(0).max(100),
  expected_value: z.string().optional(),
  close_date: z.string().optional(),
  owner_id: z.string().optional(),
  lead_id: z.string().optional(),
  win_loss_reason: z.string().optional(),
  competitor_info: z.string().optional(),
  description: z.string().optional(),
})

type LeadFormValues = z.infer<typeof leadSchema>
type OppFormValues = z.infer<typeof oppSchema>

type LeadDialogProps = {
  open: boolean
  lead: CrmLead | null
  onClose: () => void
}

export function CrmLeadFormDialog({ open, lead, onClose }: LeadDialogProps) {
  const queryClient = useQueryClient()
  const isEdit = lead !== null
  const form = useForm<LeadFormValues>({
    resolver: zodResolver(leadSchema),
    defaultValues: { company_name: "", status: "NEW" },
  })

  const lookupsQuery = useQuery({
    queryKey: ["sales", "lookups"],
    queryFn: fetchSaleLookups,
    enabled: open,
  })

  useEffect(() => {
    if (!open) return
    form.reset(
      lead
        ? {
            company_name: lead.company_name,
            contact_name: lead.contact_name ?? "",
            email: lead.email ?? "",
            phone: lead.phone ?? "",
            source: lead.source ?? "",
            status: lead.status,
            owner_id: lead.owner_id ? String(lead.owner_id) : "",
            lead_score: lead.lead_score != null ? String(lead.lead_score) : "",
            campaign_source: lead.campaign_source ?? "",
            expected_close_date: lead.expected_close_date ?? "",
            bant_budget: lead.bant_budget ?? "",
            bant_authority: lead.bant_authority ?? "",
            bant_need: lead.bant_need ?? "",
            bant_timeline: lead.bant_timeline ?? "",
            description: lead.description ?? "",
          }
        : { company_name: "", status: "NEW" },
    )
  }, [open, lead, form])

  const saveMutation = useMutation({
    mutationFn: (values: LeadFormValues) => {
      const body = {
        ...values,
        email: values.email || null,
        phone: values.phone || null,
        owner_id: values.owner_id ? Number(values.owner_id) : null,
        lead_score: values.lead_score ? Number(values.lead_score) : null,
        expected_close_date: values.expected_close_date?.trim() || null,
      }
      return isEdit && lead ? updateLead(lead.id, body) : createLead(body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["crm", "leads"] })
      toast.success(isEdit ? "Lead updated" : "Lead created")
      onClose()
    },
    onError: () => toast.error("Could not save lead"),
  })

  if (!open) return null
  const { register, handleSubmit } = form
  const users = lookupsQuery.data?.users ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/40 p-4">
      <form
        className="my-4 w-full max-w-lg rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="mb-3 text-lg font-semibold">{isEdit ? "Edit lead" : "New lead"}</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Label>Company *</Label>
            <Input {...register("company_name")} />
          </div>
          <div>
            <Label>Contact name</Label>
            <Input {...register("contact_name")} />
          </div>
          <div>
            <Label>Lead owner</Label>
            <Select {...register("owner_id")}>
              <option value="">—</option>
              {users.map((u) => (
                <option key={u.id} value={String(u.id)}>
                  {u.email}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Email</Label>
            <Input {...register("email")} />
          </div>
          <div>
            <Label>Phone</Label>
            <Input {...register("phone")} />
          </div>
          <div>
            <Label>Lead source</Label>
            <Input {...register("source")} />
          </div>
          <div>
            <Label>Campaign source</Label>
            <Input {...register("campaign_source")} />
          </div>
          <div>
            <Label>Lead score</Label>
            <Input type="number" {...register("lead_score")} />
          </div>
          <div>
            <Label>Expected close date</Label>
            <Input type="date" {...register("expected_close_date")} />
          </div>
          <div>
            <Label>Status</Label>
            <Select {...register("status")}>
              {LEAD_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>BANT — Budget</Label>
            <Input {...register("bant_budget")} />
          </div>
          <div>
            <Label>BANT — Authority</Label>
            <Input {...register("bant_authority")} />
          </div>
          <div>
            <Label>BANT — Need</Label>
            <Input {...register("bant_need")} />
          </div>
          <div>
            <Label>BANT — Timeline</Label>
            <Input {...register("bant_timeline")} />
          </div>
          <div className="sm:col-span-2">
            <Label>Description</Label>
            <Textarea {...register("description")} rows={2} />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            Save
          </Button>
        </div>
      </form>
    </div>
  )
}

type OppDialogProps = {
  open: boolean
  opportunity: CrmOpportunity | null
  onClose: () => void
}

export function CrmOpportunityFormDialog({ open, opportunity, onClose }: OppDialogProps) {
  const queryClient = useQueryClient()
  const isEdit = opportunity !== null
  const customersQuery = useQuery({
    queryKey: ["customers", "list", "crm-opp"],
    queryFn: () => fetchCustomers({ limit: 200 }),
    enabled: open,
  })
  const lookupsQuery = useQuery({
    queryKey: ["sales", "lookups"],
    queryFn: fetchSaleLookups,
    enabled: open,
  })

  const form = useForm<OppFormValues>({
    resolver: zodResolver(oppSchema),
    defaultValues: { customer_id: 0, title: "", stage: "PROSPECTING", probability: 10 },
  })

  const customerId = form.watch("customer_id")
  const leadsQuery = useQuery({
    queryKey: ["crm", "leads", "for-opp", customerId],
    queryFn: () => fetchLeads({ limit: 100 }),
    enabled: open && customerId > 0,
  })

  useEffect(() => {
    if (!open) return
    form.reset(
      opportunity
        ? {
            customer_id: opportunity.customer_id,
            title: opportunity.title,
            stage: opportunity.stage,
            probability: opportunity.probability,
            expected_value: opportunity.expected_value ?? "",
            close_date: opportunity.close_date ?? "",
            owner_id: opportunity.owner_id ? String(opportunity.owner_id) : "",
            lead_id: opportunity.lead_id ? String(opportunity.lead_id) : "",
            win_loss_reason: opportunity.win_loss_reason ?? "",
            competitor_info: opportunity.competitor_info ?? "",
            description: opportunity.description ?? "",
          }
        : { customer_id: 0, title: "", stage: "PROSPECTING", probability: 10 },
    )
  }, [open, opportunity, form])

  const expectedValue = form.watch("expected_value")
  const probability = form.watch("probability")
  const weighted =
    expectedValue && probability
      ? ((Number(expectedValue) * Number(probability)) / 100).toFixed(2)
      : "—"

  const saveMutation = useMutation({
    mutationFn: (values: OppFormValues) => {
      const body = {
        customer_id: values.customer_id,
        title: values.title,
        stage: values.stage,
        probability: values.probability,
        expected_value: values.expected_value?.trim() || null,
        close_date: values.close_date?.trim() || null,
        owner_id: values.owner_id ? Number(values.owner_id) : null,
        lead_id: values.lead_id ? Number(values.lead_id) : null,
        win_loss_reason: values.win_loss_reason?.trim() || null,
        competitor_info: values.competitor_info?.trim() || null,
        description: values.description?.trim() || null,
      }
      return isEdit && opportunity
        ? updateOpportunity(opportunity.id, body)
        : createOpportunity(body)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["crm", "opportunities"] })
      toast.success(isEdit ? "Opportunity updated" : "Opportunity created")
      onClose()
    },
    onError: () => toast.error("Could not save opportunity"),
  })

  if (!open) return null
  const { register, handleSubmit } = form
  const customers = customersQuery.data?.items ?? []
  const users = lookupsQuery.data?.users ?? []
  const leads = leadsQuery.data?.items ?? []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/40 p-4">
      <form
        className="my-4 w-full max-w-lg rounded-xl border border-border bg-card p-4 shadow-lg"
        onSubmit={handleSubmit((v) => saveMutation.mutate(v))}
      >
        <h2 className="mb-3 text-lg font-semibold">
          {isEdit ? "Edit opportunity" : "New opportunity"}
        </h2>
        <div className="space-y-3">
          <div>
            <Label>Customer *</Label>
            <Select {...register("customer_id")}>
              <option value={0}>Select customer</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Opportunity name *</Label>
            <Input {...register("title")} />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label>Stage</Label>
              <Select {...register("stage")}>
                {OPP_STAGES.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Probability %</Label>
              <Input type="number" {...register("probability")} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label>Expected revenue</Label>
              <Input {...register("expected_value")} />
            </div>
            <div>
              <Label>Weighted revenue</Label>
              <Input value={weighted} readOnly className="bg-muted" />
            </div>
          </div>
          <div>
            <Label>Close date</Label>
            <Input type="date" {...register("close_date")} />
          </div>
          <div>
            <Label>Owner</Label>
            <Select {...register("owner_id")}>
              <option value="">—</option>
              {users.map((u) => (
                <option key={u.id} value={String(u.id)}>
                  {u.email}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Related lead</Label>
            <Select {...register("lead_id")}>
              <option value="">—</option>
              {leads.map((l) => (
                <option key={l.id} value={String(l.id)}>
                  {l.company_name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label>Win / loss reason</Label>
            <Input {...register("win_loss_reason")} />
          </div>
          <div>
            <Label>Competitor information</Label>
            <Textarea {...register("competitor_info")} rows={2} />
          </div>
          <div>
            <Label>Description</Label>
            <Textarea {...register("description")} rows={2} />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saveMutation.isPending}>
            Save
          </Button>
        </div>
      </form>
    </div>
  )
}
