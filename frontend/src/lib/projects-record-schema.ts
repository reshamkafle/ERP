import { z } from "zod"

import type { ModuleRecord } from "@/types/module"
import {
  type ProjectsRepeatableKey,
  REPEATABLE_FIELD_MAP,
} from "@/lib/projects-field-groups"

const optionalStr = z.string()

export const PROJECTS_MODULE_CODE = "projects"
export const PROJECTS_FEATURE_CODE = "project_planning"

const masterDataSchema = z.object({
  project_code: optionalStr,
  project_type: optionalStr,
  project_category: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  expected_duration_days: optionalStr,
  project_manager: optionalStr,
  project_sponsor: optionalStr,
  client_name: optionalStr,
  client_contact: optionalStr,
  client_email: optionalStr,
  objectives: optionalStr,
  scope_statement: optionalStr,
  priority_level: optionalStr,
  strategic_alignment: optionalStr,
})

const planningSchema = z.object({
  wbs_root: optionalStr,
  critical_path_summary: optionalStr,
  gantt_notes: optionalStr,
  schedule_baseline: optionalStr,
})

export const projectTaskSchema = z.object({
  wbs_code: optionalStr,
  task_name: optionalStr,
  description: optionalStr,
  dependency_type: optionalStr,
  predecessor_task: optionalStr,
  estimated_duration_days: optionalStr,
  estimated_effort_hours: optionalStr,
  planned_start: optionalStr,
  planned_end: optionalStr,
  status: optionalStr,
  percent_complete: optionalStr,
})

export const projectMilestoneSchema = z.object({
  milestone_code: optionalStr,
  milestone_name: optionalStr,
  due_date: optionalStr,
  deliverable_description: optionalStr,
  acceptance_criteria: optionalStr,
  status: optionalStr,
})

const resourcesSchema = z.object({
  resource_calendar: optionalStr,
  utilization_report_notes: optionalStr,
})

export const projectResourceSchema = z.object({
  resource_type: optionalStr,
  resource_name: optionalStr,
  allocation_percent: optionalStr,
  available_from: optionalStr,
  available_to: optionalStr,
  skills_required: optionalStr,
  cost_rate: optionalStr,
})

export const projectTeamMemberSchema = z.object({
  member_name: optionalStr,
  role: optionalStr,
  responsibilities: optionalStr,
  email: optionalStr,
  allocation_percent: optionalStr,
})

const budgetSchema = z.object({
  total_budget: optionalStr,
  budgeted_labor: optionalStr,
  budgeted_material: optionalStr,
  budgeted_overhead: optionalStr,
  budgeted_travel: optionalStr,
  actual_cost: optionalStr,
  cost_variance: optionalStr,
  variance_analysis: optionalStr,
  billing_milestones: optionalStr,
  invoicing_schedule: optionalStr,
  revenue_recognition: optionalStr,
  forecast_cost_to_complete: optionalStr,
})

export const projectCostLineSchema = z.object({
  cost_category: optionalStr,
  description: optionalStr,
  budgeted_amount: optionalStr,
  actual_amount: optionalStr,
  variance: optionalStr,
})

const financialSchema = z.object({
  chart_of_accounts: optionalStr,
  gl_account: optionalStr,
  cost_center: optionalStr,
  purchase_requisitions: optionalStr,
  expense_tracking: optionalStr,
  timesheet_integration: optionalStr,
  progress_billing: optionalStr,
})

const riskHeaderSchema = z.object({
  change_request_process: optionalStr,
})

export const projectRiskSchema = z.object({
  risk_id: optionalStr,
  description: optionalStr,
  probability: optionalStr,
  impact: optionalStr,
  mitigation_plan: optionalStr,
  owner: optionalStr,
  status: optionalStr,
})

export const projectIssueSchema = z.object({
  issue_id: optionalStr,
  description: optionalStr,
  status: optionalStr,
  resolution: optionalStr,
  owner: optionalStr,
  reported_date: optionalStr,
  resolved_date: optionalStr,
})

const executionSchema = z.object({
  overall_percent_complete: optionalStr,
  earned_value: optionalStr,
  planned_value: optionalStr,
  actual_cost: optionalStr,
  spi: optionalStr,
  cpi: optionalStr,
  dashboard_kpis: optionalStr,
  alerts_notifications: optionalStr,
})

const qualitySchema = z.object({
  checklists: optionalStr,
  standards: optionalStr,
  audit_trail: optionalStr,
  compliance_status: optionalStr,
})

export const projectDocumentSchema = z.object({
  document_type: optionalStr,
  document_name: optionalStr,
  version: optionalStr,
  file_reference: optionalStr,
  approval_status: optionalStr,
  approved_by: optionalStr,
  approval_date: optionalStr,
  notes: optionalStr,
})

const reportingSchema = z.object({
  status_report_notes: optionalStr,
  resource_utilization: optionalStr,
  profitability: optionalStr,
  burndown_burnup: optionalStr,
  historical_performance: optionalStr,
  custom_dashboards: optionalStr,
})

const integrationSchema = z.object({
  finance_accounting: optionalStr,
  procurement: optionalStr,
  hr_payroll: optionalStr,
  inventory: optionalStr,
  crm: optionalStr,
  service_management: optionalStr,
})

const closureSchema = z.object({
  closure_checklist: optionalStr,
  final_settlement: optionalStr,
  lessons_learned: optionalStr,
  archive_reference: optionalStr,
  closure_date: optionalStr,
  closure_approved_by: optionalStr,
  ready_for_archive: optionalStr,
})

export const projectsFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  master_data: masterDataSchema,
  planning: planningSchema,
  tasks: z.array(projectTaskSchema),
  milestones: z.array(projectMilestoneSchema),
  resources: resourcesSchema,
  resource_allocations: z.array(projectResourceSchema),
  team_members: z.array(projectTeamMemberSchema),
  budget: budgetSchema,
  cost_lines: z.array(projectCostLineSchema),
  financial: financialSchema,
  risk: riskHeaderSchema,
  risks: z.array(projectRiskSchema),
  issues: z.array(projectIssueSchema),
  execution: executionSchema,
  quality: qualitySchema,
  documents: z.array(projectDocumentSchema),
  reporting: reportingSchema,
  integration: integrationSchema,
  closure: closureSchema,
})

export type ProjectsFormValues = z.infer<typeof projectsFormSchema>
export type ProjectTask = z.infer<typeof projectTaskSchema>
export type ProjectMilestone = z.infer<typeof projectMilestoneSchema>
export type ProjectResource = z.infer<typeof projectResourceSchema>
export type ProjectTeamMember = z.infer<typeof projectTeamMemberSchema>
export type ProjectCostLine = z.infer<typeof projectCostLineSchema>
export type ProjectRisk = z.infer<typeof projectRiskSchema>
export type ProjectIssue = z.infer<typeof projectIssueSchema>
export type ProjectDocument = z.infer<typeof projectDocumentSchema>

function emptyMasterData(): ProjectsFormValues["master_data"] {
  return {
    project_code: "",
    project_type: "",
    project_category: "",
    start_date: "",
    end_date: "",
    expected_duration_days: "",
    project_manager: "",
    project_sponsor: "",
    client_name: "",
    client_contact: "",
    client_email: "",
    objectives: "",
    scope_statement: "",
    priority_level: "",
    strategic_alignment: "",
  }
}

function emptyPlanning(): ProjectsFormValues["planning"] {
  return {
    wbs_root: "",
    critical_path_summary: "",
    gantt_notes: "",
    schedule_baseline: "",
  }
}

function emptyResources(): ProjectsFormValues["resources"] {
  return {
    resource_calendar: "",
    utilization_report_notes: "",
  }
}

function emptyBudget(): ProjectsFormValues["budget"] {
  return {
    total_budget: "",
    budgeted_labor: "",
    budgeted_material: "",
    budgeted_overhead: "",
    budgeted_travel: "",
    actual_cost: "",
    cost_variance: "",
    variance_analysis: "",
    billing_milestones: "",
    invoicing_schedule: "",
    revenue_recognition: "",
    forecast_cost_to_complete: "",
  }
}

function emptyFinancial(): ProjectsFormValues["financial"] {
  return {
    chart_of_accounts: "",
    gl_account: "",
    cost_center: "",
    purchase_requisitions: "",
    expense_tracking: "",
    timesheet_integration: "",
    progress_billing: "",
  }
}

function emptyRiskHeader(): ProjectsFormValues["risk"] {
  return { change_request_process: "" }
}

function emptyExecution(): ProjectsFormValues["execution"] {
  return {
    overall_percent_complete: "",
    earned_value: "",
    planned_value: "",
    actual_cost: "",
    spi: "",
    cpi: "",
    dashboard_kpis: "",
    alerts_notifications: "",
  }
}

function emptyQuality(): ProjectsFormValues["quality"] {
  return {
    checklists: "",
    standards: "",
    audit_trail: "",
    compliance_status: "",
  }
}

function emptyReporting(): ProjectsFormValues["reporting"] {
  return {
    status_report_notes: "",
    resource_utilization: "",
    profitability: "",
    burndown_burnup: "",
    historical_performance: "",
    custom_dashboards: "",
  }
}

function emptyIntegration(): ProjectsFormValues["integration"] {
  return {
    finance_accounting: "",
    procurement: "",
    hr_payroll: "",
    inventory: "",
    crm: "",
    service_management: "",
  }
}

function emptyClosure(): ProjectsFormValues["closure"] {
  return {
    closure_checklist: "",
    final_settlement: "",
    lessons_learned: "",
    archive_reference: "",
    closure_date: "",
    closure_approved_by: "",
    ready_for_archive: "",
  }
}

export function emptyProjectTask(): ProjectTask {
  return {
    wbs_code: "",
    task_name: "",
    description: "",
    dependency_type: "",
    predecessor_task: "",
    estimated_duration_days: "",
    estimated_effort_hours: "",
    planned_start: "",
    planned_end: "",
    status: "",
    percent_complete: "",
  }
}

export function emptyProjectMilestone(): ProjectMilestone {
  return {
    milestone_code: "",
    milestone_name: "",
    due_date: "",
    deliverable_description: "",
    acceptance_criteria: "",
    status: "",
  }
}

export function emptyProjectResource(): ProjectResource {
  return {
    resource_type: "",
    resource_name: "",
    allocation_percent: "",
    available_from: "",
    available_to: "",
    skills_required: "",
    cost_rate: "",
  }
}

export function emptyProjectTeamMember(): ProjectTeamMember {
  return {
    member_name: "",
    role: "",
    responsibilities: "",
    email: "",
    allocation_percent: "",
  }
}

export function emptyProjectCostLine(): ProjectCostLine {
  return {
    cost_category: "",
    description: "",
    budgeted_amount: "",
    actual_amount: "",
    variance: "",
  }
}

export function emptyProjectRisk(): ProjectRisk {
  return {
    risk_id: "",
    description: "",
    probability: "",
    impact: "",
    mitigation_plan: "",
    owner: "",
    status: "",
  }
}

export function emptyProjectIssue(): ProjectIssue {
  return {
    issue_id: "",
    description: "",
    status: "",
    resolution: "",
    owner: "",
    reported_date: "",
    resolved_date: "",
  }
}

export function emptyProjectDocument(): ProjectDocument {
  return {
    document_type: "",
    document_name: "",
    version: "",
    file_reference: "",
    approval_status: "",
    approved_by: "",
    approval_date: "",
    notes: "",
  }
}

export const REPEATABLE_ARRAY_PATH: Record<ProjectsRepeatableKey, keyof ProjectsFormValues> = {
  tasks: "tasks",
  milestones: "milestones",
  resources: "resource_allocations",
  team_members: "team_members",
  cost_lines: "cost_lines",
  risks: "risks",
  issues: "issues",
  documents: "documents",
}

export const EMPTY_BY_REPEATABLE_KEY: Record<ProjectsRepeatableKey, () => unknown> = {
  tasks: emptyProjectTask,
  milestones: emptyProjectMilestone,
  resources: emptyProjectResource,
  team_members: emptyProjectTeamMember,
  cost_lines: emptyProjectCostLine,
  risks: emptyProjectRisk,
  issues: emptyProjectIssue,
  documents: emptyProjectDocument,
}

export const defaultProjectsFormValues: ProjectsFormValues = {
  feature_code: PROJECTS_FEATURE_CODE,
  reference: "",
  title: "",
  status: "PLANNING",
  description: "",
  master_data: emptyMasterData(),
  planning: emptyPlanning(),
  tasks: [],
  milestones: [],
  resources: emptyResources(),
  resource_allocations: [],
  team_members: [],
  budget: emptyBudget(),
  cost_lines: [],
  financial: emptyFinancial(),
  risk: emptyRiskHeader(),
  risks: [],
  issues: [],
  execution: emptyExecution(),
  quality: emptyQuality(),
  documents: [],
  reporting: emptyReporting(),
  integration: emptyIntegration(),
  closure: emptyClosure(),
}

function strField(value: unknown): string {
  return typeof value === "string" ? value : value != null ? String(value) : ""
}

function categoryFromExtra<T extends Record<string, string>>(
  extra: Record<string, unknown> | undefined,
  key: string,
  defaults: () => T,
): T {
  const raw = extra?.[key]
  if (!raw || typeof raw !== "object") return defaults()
  const out = { ...defaults() }
  for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
    if (k in out) {
      ;(out as Record<string, string>)[k] = strField(v)
    }
  }
  return out
}

function arrayFromExtra<T extends Record<string, string>>(
  extra: Record<string, unknown> | undefined,
  key: string,
  emptyRow: () => T,
): T[] {
  const raw = extra?.[key]
  if (!Array.isArray(raw)) return []
  return raw.map((row) => {
    const base = emptyRow()
    if (!row || typeof row !== "object") return base
    for (const [k, v] of Object.entries(row as Record<string, unknown>)) {
      if (k in base) {
        ;(base as Record<string, string>)[k] = strField(v)
      }
    }
    return base
  })
}

export function recordToForm(record: ModuleRecord): ProjectsFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, unknown>

  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    master_data: {
      ...emptyMasterData(),
      ...categoryFromExtra(extra, "master_data", emptyMasterData),
      project_code:
        categoryFromExtra(extra, "master_data", emptyMasterData).project_code || record.reference,
    },
    planning: categoryFromExtra(extra, "planning", emptyPlanning),
    tasks: arrayFromExtra(extra, "tasks", emptyProjectTask),
    milestones: arrayFromExtra(extra, "milestones", emptyProjectMilestone),
    resources: categoryFromExtra(extra, "resources", emptyResources),
    resource_allocations: arrayFromExtra(extra, "resource_allocations", emptyProjectResource),
    team_members: arrayFromExtra(extra, "team_members", emptyProjectTeamMember),
    budget: categoryFromExtra(extra, "budget", emptyBudget),
    cost_lines: arrayFromExtra(extra, "cost_lines", emptyProjectCostLine),
    financial: categoryFromExtra(extra, "financial", emptyFinancial),
    risk: categoryFromExtra(extra, "risk", emptyRiskHeader),
    risks: arrayFromExtra(extra, "risks", emptyProjectRisk),
    issues: arrayFromExtra(extra, "issues", emptyProjectIssue),
    execution: categoryFromExtra(extra, "execution", emptyExecution),
    quality: categoryFromExtra(extra, "quality", emptyQuality),
    documents: arrayFromExtra(extra, "documents", emptyProjectDocument),
    reporting: categoryFromExtra(extra, "reporting", emptyReporting),
    integration: categoryFromExtra(extra, "integration", emptyIntegration),
    closure: categoryFromExtra(extra, "closure", emptyClosure),
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevel(values: ProjectsFormValues) {
  const clientName = values.master_data.client_name.trim()
  const manager = values.master_data.project_manager.trim()
  const party = clientName || manager || null

  const amount =
    parseOptionalNumber(values.budget.total_budget) ??
    parseOptionalNumber(values.budget.actual_cost)

  const projectName = values.title.trim()
  const projectCode = values.master_data.project_code.trim()
  let title = projectName
  if (!title) {
    title = projectCode || "Project"
  }

  return {
    title,
    party_name: party,
    amount,
    start_date: values.master_data.start_date.trim() || null,
    end_date: values.master_data.end_date.trim() || null,
  }
}

function buildExtraData(values: ProjectsFormValues) {
  const masterData = { ...values.master_data }
  const projectCode = masterData.project_code.trim()
  if (!projectCode) {
    masterData.project_code = values.reference.trim()
  }

  return {
    master_data: masterData,
    planning: values.planning,
    tasks: values.tasks,
    milestones: values.milestones,
    resources: values.resources,
    resource_allocations: values.resource_allocations,
    team_members: values.team_members,
    budget: values.budget,
    cost_lines: values.cost_lines,
    financial: values.financial,
    risk: values.risk,
    risks: values.risks,
    issues: values.issues,
    execution: values.execution,
    quality: values.quality,
    documents: values.documents,
    reporting: values.reporting,
    integration: values.integration,
    closure: values.closure,
  }
}

export function formToCreatePayload(values: ProjectsFormValues) {
  const top = deriveTopLevel(values)
  const reference =
    values.master_data.project_code.trim() || values.reference.trim() || newProjectReference()

  return {
    feature_code: PROJECTS_FEATURE_CODE,
    reference,
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: null,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: buildExtraData({ ...values, reference }),
  }
}

export function formToUpdatePayload(values: ProjectsFormValues) {
  const top = deriveTopLevel(values)

  return {
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: null,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: buildExtraData(values),
  }
}

export function newProjectReference(): string {
  return `PRJ-${Date.now().toString(36).toUpperCase()}`
}

export function keyLabelFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data as Record<string, unknown> | undefined
  const master = (extra?.master_data ?? {}) as Record<string, unknown>
  const code = strField(master.project_code)
  if (code) return code
  return record.reference
}

export function projectsRepeatableFields(key: ProjectsRepeatableKey) {
  return REPEATABLE_FIELD_MAP[key]
}
