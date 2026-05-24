export type ProjectsFieldType =
  | "text"
  | "number"
  | "date"
  | "datetime-local"
  | "textarea"
  | "select"
  | "checkbox"

export type ProjectsFieldDef = {
  path: string
  label: string
  type?: ProjectsFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type ProjectsRepeatableKey =
  | "tasks"
  | "milestones"
  | "resources"
  | "team_members"
  | "cost_lines"
  | "risks"
  | "issues"
  | "documents"

export type ProjectsRepeatableDef = {
  key: ProjectsRepeatableKey
  title: string
  rowLabel: string
}

export type ProjectsTabDef = {
  id: string
  title: string
  description?: string
  fields?: ProjectsFieldDef[]
  repeatables?: ProjectsRepeatableDef[]
}

const emptyOption = { value: "", label: "—" }

export const PROJECT_TYPES = [
  "INTERNAL",
  "EXTERNAL",
  "FIXED_PRICE",
  "TIME_AND_MATERIAL",
  "RETAINER",
  "HYBRID",
] as const

export const PROJECT_CATEGORIES = [
  "CONSTRUCTION",
  "IT_SOFTWARE",
  "CONSULTING",
  "MANUFACTURING",
  "RESEARCH",
  "MARKETING",
  "INFRASTRUCTURE",
  "OTHER",
] as const

export const PROJECT_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const

export const PROJECT_STATUS_OPTIONS = [
  "DRAFT",
  "PLANNING",
  "ACTIVE",
  "ON_HOLD",
  "AT_RISK",
  "COMPLETED",
  "CLOSED",
  "CANCELLED",
] as const

export const TASK_DEPENDENCY_TYPES = [
  "FINISH_TO_START",
  "START_TO_START",
  "FINISH_TO_FINISH",
  "START_TO_FINISH",
] as const

export const TASK_STATUS_OPTIONS = [
  "NOT_STARTED",
  "IN_PROGRESS",
  "COMPLETED",
  "ON_HOLD",
  "BLOCKED",
] as const

export const RESOURCE_TYPES = ["HUMAN", "MATERIAL", "EQUIPMENT", "SUBCONTRACTOR"] as const

export const RISK_PROBABILITY = ["LOW", "MEDIUM", "HIGH"] as const

export const RISK_IMPACT = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const

export const ISSUE_STATUS = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"] as const

const projectTypeOptions = [
  emptyOption,
  ...PROJECT_TYPES.map((v) => ({
    value: v,
    label: v
      .split("_")
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join(" "),
  })),
]

const categoryOptions = [
  emptyOption,
  ...PROJECT_CATEGORIES.map((v) => ({
    value: v,
    label: v
      .split("_")
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join(" "),
  })),
]

const priorityOptions = [
  emptyOption,
  ...PROJECT_PRIORITIES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const statusOptions = PROJECT_STATUS_OPTIONS.map((v) => ({
  value: v,
  label: v
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" "),
}))

const dependencyOptions = [
  emptyOption,
  ...TASK_DEPENDENCY_TYPES.map((v) => ({
    value: v,
    label: v
      .split("_")
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join("-"),
  })),
]

const taskStatusOptions = [
  emptyOption,
  ...TASK_STATUS_OPTIONS.map((v) => ({
    value: v,
    label: v
      .split("_")
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join(" "),
  })),
]

const resourceTypeOptions = [
  emptyOption,
  ...RESOURCE_TYPES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const riskLevelOptions = [
  emptyOption,
  ...RISK_PROBABILITY.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const issueStatusOptions = [
  emptyOption,
  ...ISSUE_STATUS.map((v) => ({
    value: v,
    label: v
      .split("_")
      .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
      .join(" "),
  })),
]

const yesNoOptions = [
  emptyOption,
  { value: "YES", label: "Yes" },
  { value: "NO", label: "No" },
]

const masterDataFields: ProjectsFieldDef[] = [
  { path: "reference", label: "Record reference" },
  { path: "title", label: "Project name", colSpan: 2 },
  { path: "master_data.project_code", label: "Project ID / code (unique identifier)" },
  {
    path: "master_data.project_type",
    label: "Project type",
    type: "select",
    options: projectTypeOptions,
  },
  {
    path: "master_data.project_category",
    label: "Project category / classification",
    type: "select",
    options: categoryOptions,
  },
  { path: "master_data.start_date", label: "Start date", type: "date" },
  { path: "master_data.end_date", label: "End date", type: "date" },
  { path: "master_data.expected_duration_days", label: "Expected duration (days)", type: "number" },
  { path: "master_data.project_manager", label: "Project manager" },
  { path: "master_data.project_sponsor", label: "Project sponsor" },
  { path: "master_data.client_name", label: "Client / customer name" },
  { path: "master_data.client_contact", label: "Client contact" },
  { path: "master_data.client_email", label: "Client email" },
  {
    path: "master_data.objectives",
    label: "Project objectives",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "master_data.scope_statement",
    label: "Scope statement",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "master_data.priority_level",
    label: "Priority level",
    type: "select",
    options: priorityOptions,
  },
  {
    path: "master_data.strategic_alignment",
    label: "Strategic alignment",
    type: "textarea",
    colSpan: 2,
  },
  { path: "status", label: "Project status", type: "select", options: statusOptions },
  { path: "description", label: "Description / notes", type: "textarea", colSpan: 2 },
]

const planningFields: ProjectsFieldDef[] = [
  { path: "planning.wbs_root", label: "Work breakdown structure (WBS) root code" },
  {
    path: "planning.critical_path_summary",
    label: "Critical path identification",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "planning.gantt_notes",
    label: "Gantt chart & timeline notes",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "planning.schedule_baseline",
    label: "Schedule baseline reference",
  },
]

export const projectTaskFields: ProjectsFieldDef[] = [
  { path: "wbs_code", label: "WBS code" },
  { path: "task_name", label: "Task / activity name", colSpan: 2 },
  { path: "description", label: "Task description", type: "textarea", colSpan: 2 },
  {
    path: "dependency_type",
    label: "Dependency type",
    type: "select",
    options: dependencyOptions,
  },
  { path: "predecessor_task", label: "Predecessor task" },
  { path: "estimated_duration_days", label: "Estimated duration (days)", type: "number" },
  { path: "estimated_effort_hours", label: "Estimated effort (man-hours)", type: "number" },
  { path: "planned_start", label: "Planned start date", type: "date" },
  { path: "planned_end", label: "Planned end date", type: "date" },
  {
    path: "status",
    label: "Task status",
    type: "select",
    options: taskStatusOptions,
  },
  { path: "percent_complete", label: "Percent complete", type: "number" },
]

export const projectMilestoneFields: ProjectsFieldDef[] = [
  { path: "milestone_code", label: "Milestone code" },
  { path: "milestone_name", label: "Milestone / deliverable name", colSpan: 2 },
  { path: "due_date", label: "Due date", type: "date" },
  { path: "deliverable_description", label: "Deliverable description", type: "textarea", colSpan: 2 },
  {
    path: "acceptance_criteria",
    label: "Acceptance criteria",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "status",
    label: "Status",
    type: "select",
    options: taskStatusOptions,
  },
]

const resourceFields: ProjectsFieldDef[] = [
  {
    path: "resources.resource_calendar",
    label: "Resource availability & calendar",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "resources.utilization_report_notes",
    label: "Resource utilization report notes",
    type: "textarea",
    colSpan: 2,
  },
]

export const projectResourceFields: ProjectsFieldDef[] = [
  {
    path: "resource_type",
    label: "Resource type",
    type: "select",
    options: resourceTypeOptions,
  },
  { path: "resource_name", label: "Resource name" },
  { path: "allocation_percent", label: "Allocation (%)", type: "number" },
  { path: "available_from", label: "Available from", type: "date" },
  { path: "available_to", label: "Available to", type: "date" },
  { path: "skills_required", label: "Skill / competency requirements", colSpan: 2 },
  { path: "cost_rate", label: "Cost rate", type: "number" },
]

export const projectTeamMemberFields: ProjectsFieldDef[] = [
  { path: "member_name", label: "Team member name" },
  { path: "role", label: "Role" },
  { path: "responsibilities", label: "Responsibilities", type: "textarea", colSpan: 2 },
  { path: "email", label: "Email" },
  { path: "allocation_percent", label: "Allocation (%)", type: "number" },
]

const budgetFields: ProjectsFieldDef[] = [
  { path: "budget.total_budget", label: "Total project budget", type: "number" },
  { path: "budget.budgeted_labor", label: "Budgeted labor cost", type: "number" },
  { path: "budget.budgeted_material", label: "Budgeted material cost", type: "number" },
  { path: "budget.budgeted_overhead", label: "Budgeted overhead", type: "number" },
  { path: "budget.budgeted_travel", label: "Budgeted travel", type: "number" },
  { path: "budget.actual_cost", label: "Actual cost to date", type: "number" },
  { path: "budget.cost_variance", label: "Cost variance (budget vs actual)", type: "number" },
  {
    path: "budget.variance_analysis",
    label: "Cost variance analysis notes",
    type: "textarea",
    colSpan: 2,
  },
  { path: "budget.billing_milestones", label: "Billing milestones schedule", type: "textarea", colSpan: 2 },
  { path: "budget.invoicing_schedule", label: "Invoicing schedule", type: "textarea", colSpan: 2 },
  { path: "budget.revenue_recognition", label: "Revenue recognition method", colSpan: 2 },
  { path: "budget.forecast_cost_to_complete", label: "Forecasted cost to complete", type: "number" },
]

export const projectCostLineFields: ProjectsFieldDef[] = [
  { path: "cost_category", label: "Cost category (Labor, Material, Overhead, Travel, etc.)" },
  { path: "description", label: "Description", colSpan: 2 },
  { path: "budgeted_amount", label: "Budgeted amount", type: "number" },
  { path: "actual_amount", label: "Actual amount", type: "number" },
  { path: "variance", label: "Variance", type: "number" },
]

const financialFields: ProjectsFieldDef[] = [
  { path: "financial.chart_of_accounts", label: "Chart of accounts linkage" },
  { path: "financial.gl_account", label: "GL account code" },
  { path: "financial.cost_center", label: "Cost center" },
  {
    path: "financial.purchase_requisitions",
    label: "Purchase requisitions & orders",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "financial.expense_tracking",
    label: "Expense tracking & approval workflow",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "financial.timesheet_integration",
    label: "Timesheet integration (labor cost)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "financial.progress_billing",
    label: "Progress billing & revenue recognition",
    type: "textarea",
    colSpan: 2,
  },
]

const riskHeaderFields: ProjectsFieldDef[] = [
  {
    path: "risk.change_request_process",
    label: "Change request management process",
    type: "textarea",
    colSpan: 2,
  },
]

export const projectRiskFields: ProjectsFieldDef[] = [
  { path: "risk_id", label: "Risk ID" },
  { path: "description", label: "Risk description", colSpan: 2 },
  {
    path: "probability",
    label: "Probability",
    type: "select",
    options: riskLevelOptions,
  },
  {
    path: "impact",
    label: "Impact",
    type: "select",
    options: [
      emptyOption,
      ...RISK_IMPACT.map((v) => ({
        value: v,
        label: v.charAt(0) + v.slice(1).toLowerCase(),
      })),
    ],
  },
  { path: "mitigation_plan", label: "Mitigation plan", type: "textarea", colSpan: 2 },
  { path: "owner", label: "Risk owner" },
  {
    path: "status",
    label: "Status",
    type: "select",
    options: issueStatusOptions,
  },
]

export const projectIssueFields: ProjectsFieldDef[] = [
  { path: "issue_id", label: "Issue ID" },
  { path: "description", label: "Issue description", colSpan: 2 },
  {
    path: "status",
    label: "Status",
    type: "select",
    options: issueStatusOptions,
  },
  { path: "resolution", label: "Resolution", type: "textarea", colSpan: 2 },
  { path: "owner", label: "Issue owner" },
  { path: "reported_date", label: "Reported date", type: "date" },
  { path: "resolved_date", label: "Resolved date", type: "date" },
]

const executionFields: ProjectsFieldDef[] = [
  {
    path: "execution.overall_percent_complete",
    label: "Overall project completion (%)",
    type: "number",
  },
  { path: "execution.earned_value", label: "Earned value (EV)", type: "number" },
  { path: "execution.planned_value", label: "Planned value (PV)", type: "number" },
  { path: "execution.actual_cost", label: "Actual cost (AC)", type: "number" },
  { path: "execution.spi", label: "Schedule performance index (SPI)", type: "number" },
  { path: "execution.cpi", label: "Cost performance index (CPI)", type: "number" },
  {
    path: "execution.dashboard_kpis",
    label: "Real-time dashboard & KPI tracking",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "execution.alerts_notifications",
    label: "Alerts & notifications (delays, budget overruns)",
    type: "textarea",
    colSpan: 2,
  },
]

const qualityFields: ProjectsFieldDef[] = [
  {
    path: "quality.checklists",
    label: "Quality checklists & inspection points",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "quality.standards",
    label: "Quality standards & acceptance criteria",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "quality.audit_trail",
    label: "Audit trail & compliance documentation",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "quality.compliance_status",
    label: "Compliance status",
    type: "select",
    options: [
      emptyOption,
      { value: "COMPLIANT", label: "Compliant" },
      { value: "PARTIAL", label: "Partially compliant" },
      { value: "NON_COMPLIANT", label: "Non-compliant" },
      { value: "PENDING_REVIEW", label: "Pending review" },
    ],
  },
]

export const projectDocumentFields: ProjectsFieldDef[] = [
  { path: "document_type", label: "Document type (SOW, Contract, Drawing, Report, etc.)" },
  { path: "document_name", label: "Document name", colSpan: 2 },
  { path: "version", label: "Version" },
  { path: "file_reference", label: "File / repository reference" },
  { path: "approval_status", label: "Approval status" },
  { path: "approved_by", label: "Approved by" },
  { path: "approval_date", label: "Approval date", type: "date" },
  { path: "notes", label: "Notes", type: "textarea", colSpan: 2 },
]

const reportingFields: ProjectsFieldDef[] = [
  {
    path: "reporting.status_report_notes",
    label: "Project status reports",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "reporting.resource_utilization",
    label: "Resource utilization reports",
    type: "textarea",
    colSpan: 2,
  },
  { path: "reporting.profitability", label: "Profitability analysis (per project)", type: "textarea", colSpan: 2 },
  {
    path: "reporting.burndown_burnup",
    label: "Burn-down / burn-up chart notes",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "reporting.historical_performance",
    label: "Historical project performance data",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "reporting.custom_dashboards",
    label: "Custom dashboards configuration",
    type: "textarea",
    colSpan: 2,
  },
]

const integrationFields: ProjectsFieldDef[] = [
  {
    path: "integration.finance_accounting",
    label: "Finance & accounting (costing, billing, GL posting)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "integration.procurement",
    label: "Procurement / supply chain (material & vendor management)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "integration.hr_payroll",
    label: "HR & payroll (timesheets, resource costing)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "integration.inventory",
    label: "Inventory (material issue for projects)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "integration.crm",
    label: "CRM (customer projects & opportunities)",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "integration.service_management",
    label: "Service management (post-project support)",
    type: "textarea",
    colSpan: 2,
  },
]

const closureFields: ProjectsFieldDef[] = [
  {
    path: "closure.closure_checklist",
    label: "Project closure checklist",
    type: "textarea",
    colSpan: 2,
  },
  { path: "closure.final_settlement", label: "Final financial settlement & invoice", type: "textarea", colSpan: 2 },
  {
    path: "closure.lessons_learned",
    label: "Lessons learned documentation",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "closure.archive_reference",
    label: "Project archive & knowledge base reference",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "closure.closure_date",
    label: "Closure date",
    type: "date",
  },
  {
    path: "closure.closure_approved_by",
    label: "Closure approved by",
  },
  {
    path: "closure.ready_for_archive",
    label: "Ready for archive",
    type: "select",
    options: yesNoOptions,
  },
]

export const PROJECT_FORM_TABS: ProjectsTabDef[] = [
  {
    id: "master_data",
    title: "Master Data",
    description: "Project identification, type, dates, stakeholders, objectives, and priority.",
    fields: masterDataFields,
  },
  {
    id: "planning",
    title: "Planning & Scheduling",
    description: "WBS, tasks, dependencies, critical path, Gantt, and milestones.",
    fields: planningFields,
    repeatables: [
      { key: "tasks", title: "Tasks / activities", rowLabel: "Task" },
      { key: "milestones", title: "Milestones & deliverables", rowLabel: "Milestone" },
    ],
  },
  {
    id: "resources",
    title: "Resource Management",
    description: "Resource allocation, availability, skills, and team assignments.",
    fields: resourceFields,
    repeatables: [
      { key: "resources", title: "Resource allocation", rowLabel: "Resource" },
      { key: "team_members", title: "Team members", rowLabel: "Team member" },
    ],
  },
  {
    id: "budget",
    title: "Budget & Cost",
    description: "Total budget, cost breakdown, variance, billing, and forecasts.",
    fields: budgetFields,
    repeatables: [{ key: "cost_lines", title: "Cost breakdown lines", rowLabel: "Cost line" }],
  },
  {
    id: "financial",
    title: "Financial Integration",
    description: "Chart of accounts, procurement, expenses, timesheets, and billing.",
    fields: financialFields,
  },
  {
    id: "risk",
    title: "Risk & Issues",
    description: "Risk register, mitigation plans, issue log, and change requests.",
    fields: riskHeaderFields,
    repeatables: [
      { key: "risks", title: "Risk register", rowLabel: "Risk" },
      { key: "issues", title: "Issue log", rowLabel: "Issue" },
    ],
  },
  {
    id: "execution",
    title: "Execution & Monitoring",
    description: "Task status, EVM metrics, dashboards, and alerts.",
    fields: executionFields,
  },
  {
    id: "quality",
    title: "Quality & Compliance",
    description: "Checklists, standards, acceptance criteria, and audit trail.",
    fields: qualityFields,
  },
  {
    id: "documents",
    title: "Documents",
    description: "Project document repository, version control, and approvals.",
    repeatables: [{ key: "documents", title: "Project documents", rowLabel: "Document" }],
  },
  {
    id: "reporting",
    title: "Reporting & Analytics",
    description: "Status reports, utilization, profitability, and dashboards.",
    fields: reportingFields,
  },
  {
    id: "integration",
    title: "ERP Integration",
    description: "Links to finance, procurement, HR, inventory, CRM, and service modules.",
    fields: integrationFields,
  },
  {
    id: "closure",
    title: "Closure & Archiving",
    description: "Closure checklist, final settlement, lessons learned, and archive.",
    fields: closureFields,
  },
]

export const PROJECTS_PHASE1_FEATURES = new Set(["project_planning"])

export const PROJECTS_LINKED_ROUTES = [
  "/finance",
  "/crm",
  "/procurement",
  "/sales",
  "/customers",
] as const

export const REPEATABLE_FIELD_MAP: Record<ProjectsRepeatableKey, ProjectsFieldDef[]> = {
  tasks: projectTaskFields,
  milestones: projectMilestoneFields,
  resources: projectResourceFields,
  team_members: projectTeamMemberFields,
  cost_lines: projectCostLineFields,
  risks: projectRiskFields,
  issues: projectIssueFields,
  documents: projectDocumentFields,
}
