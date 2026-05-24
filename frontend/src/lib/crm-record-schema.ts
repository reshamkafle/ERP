import { z } from "zod"

import type { ModuleRecord } from "@/types/module"

export const CRM_MODULE_CODE = "crm"

export const CRM_STATUS_OPTIONS = [
  "DRAFT",
  "ACTIVE",
  "IN_PROGRESS",
  "COMPLETED",
  "APPROVED",
  "CANCELLED",
] as const

const optionalStr = z.string().optional()

export const crmModuleRecordSchema = z.object({
  feature_code: z.string().min(1),
  reference: optionalStr,
  title: z.string().min(1, "Title is required"),
  status: z.enum(CRM_STATUS_OPTIONS).default("DRAFT"),
  description: optionalStr,
  party_name: optionalStr,
  amount: optionalStr,
  quantity: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  campaign_channel: optionalStr,
  campaign_segment: optionalStr,
  case_type: optionalStr,
  sla_hours: optionalStr,
  ticket_category: optionalStr,
})

export type CrmModuleRecordFormValues = z.infer<typeof crmModuleRecordSchema>

export function crmRecordToForm(record: ModuleRecord): CrmModuleRecordFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, Record<string, unknown>>
  const campaign = extra.campaign ?? {}
  const caseData = extra.case ?? {}
  const ticket = extra.ticket ?? {}
  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: (CRM_STATUS_OPTIONS.includes(record.status as (typeof CRM_STATUS_OPTIONS)[number])
      ? record.status
      : "DRAFT") as CrmModuleRecordFormValues["status"],
    description: record.description ?? "",
    party_name: record.party_name ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    quantity: record.quantity != null ? String(record.quantity) : "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    campaign_channel: String(campaign.channel ?? ""),
    campaign_segment: String(campaign.segment ?? ""),
    case_type: String(caseData.case_type ?? ""),
    sla_hours: String(caseData.sla_hours ?? ""),
    ticket_category: String(ticket.category ?? ""),
  }
}

export function crmFormToExtraData(values: CrmModuleRecordFormValues): Record<string, unknown> {
  if (values.feature_code === "marketing_campaigns") {
    return {
      campaign: {
        channel: values.campaign_channel,
        segment: values.campaign_segment,
        budget: values.amount,
      },
    }
  }
  if (values.feature_code === "customer_service") {
    return {
      case: {
        case_type: values.case_type,
        sla_hours: values.sla_hours,
        priority: values.status,
      },
    }
  }
  if (values.feature_code === "support_tickets") {
    return {
      ticket: {
        category: values.ticket_category,
        sla_due: values.end_date,
      },
    }
  }
  return { seed: false, module: CRM_MODULE_CODE, feature: values.feature_code }
}
