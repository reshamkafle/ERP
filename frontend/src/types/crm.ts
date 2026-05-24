export type LeadStatus =
  | "NEW"
  | "CONTACTED"
  | "QUALIFIED"
  | "UNQUALIFIED"
  | "CONVERTED"
  | "LOST"

export type OpportunityStage =
  | "PROSPECTING"
  | "QUALIFICATION"
  | "PROPOSAL"
  | "NEGOTIATION"
  | "CLOSED_WON"
  | "CLOSED_LOST"

export type CrmActivityType =
  | "CALL"
  | "EMAIL"
  | "MEETING"
  | "NOTE"
  | "VISIT"
  | "TASK"
  | "DEMO"
  | "SITE_VISIT"

export type CommunicationChannel = "EMAIL" | "PHONE" | "SMS" | "IN_PERSON" | "PORTAL"

export type InfluenceLevel = "LOW" | "MEDIUM" | "HIGH" | "DECISION_MAKER"

export type CustomerContact = {
  id: number
  customer_id: number
  contact_code: string | null
  salutation: string | null
  first_name: string | null
  middle_name: string | null
  last_name: string | null
  name: string
  email: string | null
  email_secondary: string | null
  phone: string | null
  phone_secondary: string | null
  title: string | null
  department: string | null
  role: string | null
  is_primary: boolean
  preferred_channel: CommunicationChannel | null
  influence_level: InfluenceLevel | null
  relationship_strength: string | null
  linkedin_url: string | null
  social_profiles: Record<string, string> | null
  birthday: string | null
  anniversary: string | null
  preferred_language: string | null
  reports_to_id: number | null
  notes: string | null
  created_at: string
}

export type CrmActivity = {
  id: number
  customer_id: number
  contact_id: number | null
  activity_type: CrmActivityType
  subject: string
  body: string | null
  occurred_at: string
  duration_minutes: number | null
  outcome: string | null
  next_follow_up_at: string | null
  attachments: { name: string; url: string; mime?: string }[] | null
  created_by_id: number | null
  created_at: string
}

export type CrmLead = {
  id: number
  customer_id: number | null
  company_name: string
  contact_name: string | null
  email: string | null
  phone: string | null
  source: string | null
  status: LeadStatus
  owner_id: number | null
  lead_score: number | null
  campaign_source: string | null
  expected_close_date: string | null
  bant_budget: string | null
  bant_authority: string | null
  bant_need: string | null
  bant_timeline: string | null
  description: string | null
  created_at: string
  updated_at: string
}

export type CrmLeadListResponse = {
  items: CrmLead[]
  total: number
}

export type CrmOpportunityStageHistory = {
  id: number
  opportunity_id: number
  from_stage: string | null
  to_stage: string
  changed_at: string
  changed_by_id: number | null
}

export type CrmOpportunity = {
  id: number
  customer_id: number
  lead_id: number | null
  title: string
  stage: OpportunityStage
  probability: number
  expected_value: string | null
  close_date: string | null
  win_loss_reason: string | null
  competitor_info: string | null
  sale_id: number | null
  owner_id: number | null
  description: string | null
  created_at: string
  updated_at: string
  stage_history?: CrmOpportunityStageHistory[]
}

export type CrmOpportunityListResponse = {
  items: CrmOpportunity[]
  total: number
}

export type PipelineStageSummary = {
  stage: OpportunityStage
  count: number
  total_value: string
}

export type PipelineSummary = {
  stages: PipelineStageSummary[]
  open_lead_count: number
  total_open_value: string
}
