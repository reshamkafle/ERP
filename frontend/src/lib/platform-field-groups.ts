export type PlatformFieldType =
  | "text"
  | "number"
  | "date"
  | "textarea"
  | "select"

export type PlatformFieldDef = {
  path: string
  label: string
  type?: PlatformFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type PlatformTabDef = {
  id: string
  title: string
  description?: string
  fields?: PlatformFieldDef[]
}

const emptyOption = { value: "", label: "—" }

export const PLATFORM_INDUSTRY_VERTICALS = [
  "Manufacturing",
  "Retail",
  "Healthcare",
  "Construction",
  "Distribution",
  "Professional Services",
  "Other",
] as const

export const PLATFORM_STATUS_OPTIONS = [
  "DRAFT",
  "IN_REVIEW",
  "APPROVED",
  "IN_IMPLEMENTATION",
  "LIVE",
  "RETIRED",
] as const

export const PLATFORM_FEATURE_OPTIONS = [
  { value: "business_intelligence", label: "Business Intelligence" },
  { value: "ecommerce", label: "E-commerce Integration" },
  { value: "field_service", label: "Service Management" },
  { value: "retail_pos", label: "Retail / POS" },
  { value: "plant_maintenance", label: "Plant Maintenance" },
  { value: "compliance_risk", label: "Compliance & Risk" },
] as const

export const PLATFORM_LINKED_ROUTES = ["/reports", "/pos"] as const

const industryOptions = [
  emptyOption,
  ...PLATFORM_INDUSTRY_VERTICALS.map((v) => ({ value: v, label: v })),
]

const statusOptions = [
  emptyOption,
  ...PLATFORM_STATUS_OPTIONS.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase().replace(/_/g, " "),
  })),
]

const featureOptions = [
  emptyOption,
  ...PLATFORM_FEATURE_OPTIONS.map((f) => ({ value: f.value, label: f.label })),
]

export const PLATFORM_CORE_FIELDS: PlatformFieldDef[] = [
  { path: "reference", label: "Reference *" },
  {
    path: "feature_code",
    label: "Platform feature *",
    type: "select",
    options: featureOptions,
    colSpan: 2,
  },
  {
    path: "status",
    label: "Status *",
    type: "select",
    options: statusOptions,
  },
]

export const PLATFORM_FORM_TABS: PlatformTabDef[] = [
  {
    id: "identity",
    title: "Module & Purpose",
    description:
      "Clear title and brief description of primary objective and how it addresses industry-specific challenges.",
    fields: [
      { path: "title", label: "Module name *", colSpan: 2 },
      {
        path: "description",
        label: "Primary objective / purpose",
        type: "textarea",
        colSpan: 2,
        placeholder: "Brief description of the module's primary objective…",
      },
      {
        path: "identity.example_title",
        label: "Example title",
        colSpan: 2,
        placeholder: "e.g. Manufacturing Execution System - MES, Healthcare Patient Management",
      },
    ],
  },
  {
    id: "industry",
    title: "Industry Relevance",
    description:
      "Specific industry or vertical supported and why standard core modules are insufficient.",
    fields: [
      {
        path: "industry.vertical",
        label: "Industry / vertical",
        type: "select",
        options: industryOptions,
      },
      {
        path: "industry.core_gap_rationale",
        label: "Why core modules are insufficient",
        type: "textarea",
        colSpan: 2,
        placeholder: "Explain gaps in standard Finance, Inventory, HR, etc. for this vertical…",
      },
    ],
  },
  {
    id: "features",
    title: "Key Features",
    description:
      "Detailed list of capabilities such as BOM, production scheduling, quality control, POS integration, or regulatory compliance tracking.",
    fields: [
      {
        path: "features.key_features",
        label: "Key features and functionalities",
        type: "textarea",
        colSpan: 2,
        placeholder: "Bill of Materials, Production Scheduling, Quality Control, Field Service Management…",
      },
    ],
  },
  {
    id: "processes",
    title: "Business Processes",
    description:
      "Workflows the module automates or optimizes (shop floor control, project costing, patient billing, etc.).",
    fields: [
      {
        path: "processes.business_processes",
        label: "Business processes supported",
        type: "textarea",
        colSpan: 2,
        placeholder: "Shop floor control, project costing, patient billing, inventory traceability…",
      },
    ],
  },
  {
    id: "data_requirements",
    title: "Data & Entities",
    description:
      "Key data fields, master data, and integration points with core modules (Finance, Inventory, HR).",
    fields: [
      {
        path: "data_requirements.entities",
        label: "Key data fields and master data",
        type: "textarea",
        colSpan: 2,
        placeholder: "Items, recipes, patient records, project WBS, lot/serial numbers…",
      },
      {
        path: "data_requirements.core_integrations",
        label: "Integration points with core modules",
        type: "textarea",
        colSpan: 2,
        placeholder: "Finance (GL, AP/AR), Inventory, HR, Manufacturing…",
      },
    ],
  },
  {
    id: "integration",
    title: "Integration",
    description:
      "Connections with other ERP modules, third-party systems, and APIs or middleware.",
    fields: [
      {
        path: "integration.erp_modules",
        label: "ERP module connections",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "integration.third_party",
        label: "Third-party systems (CAD, CRM, IoT, e-commerce)",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "integration.apis",
        label: "APIs and middleware",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "compliance",
    title: "Compliance",
    description:
      "Industry-specific standards (FDA, ISO, GDPR, SOX, HACCP) and audit trails or reporting.",
    fields: [
      {
        path: "compliance.standards",
        label: "Regulatory standards and frameworks",
        type: "textarea",
        colSpan: 2,
        placeholder: "FDA, ISO, GDPR, SOX, HACCP, local tax regulations…",
      },
      {
        path: "compliance.audit_trails",
        label: "Audit trails and compliance reporting",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "reporting",
    title: "Reporting",
    description: "Dashboards, KPIs, and custom reports unique to the industry.",
    fields: [
      {
        path: "reporting.dashboards_kpis",
        label: "Dashboards, KPIs, and custom reports",
        type: "textarea",
        colSpan: 2,
        placeholder: "Yield analysis, project profitability, shelf-life tracking…",
      },
    ],
  },
  {
    id: "roles",
    title: "Roles & Permissions",
    description: "Who will use the module and required access controls.",
    fields: [
      {
        path: "roles.user_roles",
        label: "User roles",
        type: "textarea",
        colSpan: 2,
        placeholder: "Production supervisors, field technicians, clinicians…",
      },
      {
        path: "roles.access_controls",
        label: "Access controls and permissions",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "customization",
    title: "Customization",
    description: "Extent of tailoring, configuration options, and low-code/no-code tools.",
    fields: [
      {
        path: "customization.configuration_needs",
        label: "Configuration and tailoring needs",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "customization.low_code_tools",
        label: "Low-code / no-code tools available",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "scalability",
    title: "Scalability",
    description:
      "Expected transaction volume, users, multi-site support, and future growth projections.",
    fields: [
      {
        path: "scalability.transaction_volume",
        label: "Transaction volume and user count",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "scalability.multi_site",
        label: "Multi-site / multi-company and growth projections",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "mobile",
    title: "Mobile / Field",
    description: "Mobile apps, offline functionality, and field operations support.",
    fields: [
      {
        path: "mobile.field_access",
        label: "Mobile and field access requirements",
        type: "textarea",
        colSpan: 2,
        placeholder: "Offline mobile for technicians, barcode scanning, GPS check-in…",
      },
    ],
  },
  {
    id: "implementation",
    title: "Implementation",
    description: "Estimated effort, data migration, training, and go-live dependencies.",
    fields: [
      {
        path: "implementation.effort_estimate",
        label: "Estimated implementation effort",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "implementation.migration",
        label: "Data migration needs",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "implementation.training",
        label: "Training requirements",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "implementation.go_live_dependencies",
        label: "Go-live dependencies",
        type: "textarea",
        colSpan: 2,
      },
      { path: "start_date", label: "Planned go-live start", type: "date" },
      { path: "end_date", label: "Planned go-live end", type: "date" },
    ],
  },
  {
    id: "costs",
    title: "Cost Breakdown",
    description: "Licensing, implementation, customization, maintenance, and infrastructure costs.",
    fields: [
      {
        path: "costs.licensing",
        label: "Licensing (per user / module)",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "costs.implementation",
        label: "Implementation costs",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "costs.maintenance",
        label: "Maintenance and support",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "costs.infrastructure",
        label: "Hardware / infrastructure",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "amount",
        label: "Estimated total cost",
        type: "number",
        placeholder: "Total estimated cost (numeric)",
      },
    ],
  },
  {
    id: "benefits",
    title: "Benefits & ROI",
    description: "Expected outcomes with measurable KPIs.",
    fields: [
      {
        path: "benefits.expected_outcomes",
        label: "Expected outcomes",
        type: "textarea",
        colSpan: 2,
        placeholder: "Reduced production downtime, improved inventory accuracy, faster project billing…",
      },
      {
        path: "benefits.roi_kpis",
        label: "ROI metrics and KPIs",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "risks",
    title: "Risks",
    description: "Potential challenges and prerequisites for successful deployment.",
    fields: [
      {
        path: "risks.challenges",
        label: "Potential challenges",
        type: "textarea",
        colSpan: 2,
        placeholder: "Data accuracy in legacy systems, user adoption, integration complexity…",
      },
      {
        path: "risks.prerequisites",
        label: "Prerequisites for successful deployment",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "vendor",
    title: "Vendor Fit",
    description: "Compatibility with base ERP, vendor expertise, and reference implementations.",
    fields: [
      {
        path: "vendor.platform_fit",
        label: "Compatibility with base ERP platform",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "vendor.vendor_expertise",
        label: "Vendor industry expertise",
        type: "textarea",
        colSpan: 2,
      },
      {
        path: "vendor.references",
        label: "References from similar implementations",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
]
