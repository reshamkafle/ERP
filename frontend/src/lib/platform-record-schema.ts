import { z } from "zod"

import type { ModuleRecord } from "@/types/module"

const optionalStr = z.string()

export const PLATFORM_MODULE_CODE = "platform"

export const PLATFORM_DEFAULT_FEATURE = "business_intelligence"

const identitySchema = z.object({
  example_title: optionalStr,
})

const industrySchema = z.object({
  vertical: optionalStr,
  core_gap_rationale: optionalStr,
})

const featuresSchema = z.object({
  key_features: optionalStr,
})

const processesSchema = z.object({
  business_processes: optionalStr,
})

const dataRequirementsSchema = z.object({
  entities: optionalStr,
  core_integrations: optionalStr,
})

const integrationSchema = z.object({
  erp_modules: optionalStr,
  third_party: optionalStr,
  apis: optionalStr,
})

const complianceSchema = z.object({
  standards: optionalStr,
  audit_trails: optionalStr,
})

const reportingSchema = z.object({
  dashboards_kpis: optionalStr,
})

const rolesSchema = z.object({
  user_roles: optionalStr,
  access_controls: optionalStr,
})

const customizationSchema = z.object({
  configuration_needs: optionalStr,
  low_code_tools: optionalStr,
})

const scalabilitySchema = z.object({
  transaction_volume: optionalStr,
  multi_site: optionalStr,
})

const mobileSchema = z.object({
  field_access: optionalStr,
})

const implementationSchema = z.object({
  effort_estimate: optionalStr,
  migration: optionalStr,
  training: optionalStr,
  go_live_dependencies: optionalStr,
})

const costsSchema = z.object({
  licensing: optionalStr,
  implementation: optionalStr,
  maintenance: optionalStr,
  infrastructure: optionalStr,
})

const benefitsSchema = z.object({
  expected_outcomes: optionalStr,
  roi_kpis: optionalStr,
})

const risksSchema = z.object({
  challenges: optionalStr,
  prerequisites: optionalStr,
})

const vendorSchema = z.object({
  platform_fit: optionalStr,
  vendor_expertise: optionalStr,
  references: optionalStr,
})

export const platformFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  amount: optionalStr,
  identity: identitySchema,
  industry: industrySchema,
  features: featuresSchema,
  processes: processesSchema,
  data_requirements: dataRequirementsSchema,
  integration: integrationSchema,
  compliance: complianceSchema,
  reporting: reportingSchema,
  roles: rolesSchema,
  customization: customizationSchema,
  scalability: scalabilitySchema,
  mobile: mobileSchema,
  implementation: implementationSchema,
  costs: costsSchema,
  benefits: benefitsSchema,
  risks: risksSchema,
  vendor: vendorSchema,
})

export type PlatformFormValues = z.infer<typeof platformFormSchema>

function emptyIdentity(): PlatformFormValues["identity"] {
  return { example_title: "" }
}

function emptyIndustry(): PlatformFormValues["industry"] {
  return { vertical: "", core_gap_rationale: "" }
}

function emptyFeatures(): PlatformFormValues["features"] {
  return { key_features: "" }
}

function emptyProcesses(): PlatformFormValues["processes"] {
  return { business_processes: "" }
}

function emptyDataRequirements(): PlatformFormValues["data_requirements"] {
  return { entities: "", core_integrations: "" }
}

function emptyIntegration(): PlatformFormValues["integration"] {
  return { erp_modules: "", third_party: "", apis: "" }
}

function emptyCompliance(): PlatformFormValues["compliance"] {
  return { standards: "", audit_trails: "" }
}

function emptyReporting(): PlatformFormValues["reporting"] {
  return { dashboards_kpis: "" }
}

function emptyRoles(): PlatformFormValues["roles"] {
  return { user_roles: "", access_controls: "" }
}

function emptyCustomization(): PlatformFormValues["customization"] {
  return { configuration_needs: "", low_code_tools: "" }
}

function emptyScalability(): PlatformFormValues["scalability"] {
  return { transaction_volume: "", multi_site: "" }
}

function emptyMobile(): PlatformFormValues["mobile"] {
  return { field_access: "" }
}

function emptyImplementation(): PlatformFormValues["implementation"] {
  return {
    effort_estimate: "",
    migration: "",
    training: "",
    go_live_dependencies: "",
  }
}

function emptyCosts(): PlatformFormValues["costs"] {
  return {
    licensing: "",
    implementation: "",
    maintenance: "",
    infrastructure: "",
  }
}

function emptyBenefits(): PlatformFormValues["benefits"] {
  return { expected_outcomes: "", roi_kpis: "" }
}

function emptyRisks(): PlatformFormValues["risks"] {
  return { challenges: "", prerequisites: "" }
}

function emptyVendor(): PlatformFormValues["vendor"] {
  return { platform_fit: "", vendor_expertise: "", references: "" }
}

export const defaultPlatformFormValues: PlatformFormValues = {
  feature_code: PLATFORM_DEFAULT_FEATURE,
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  start_date: "",
  end_date: "",
  amount: "",
  identity: emptyIdentity(),
  industry: emptyIndustry(),
  features: emptyFeatures(),
  processes: emptyProcesses(),
  data_requirements: emptyDataRequirements(),
  integration: emptyIntegration(),
  compliance: emptyCompliance(),
  reporting: emptyReporting(),
  roles: emptyRoles(),
  customization: emptyCustomization(),
  scalability: emptyScalability(),
  mobile: emptyMobile(),
  implementation: emptyImplementation(),
  costs: emptyCosts(),
  benefits: emptyBenefits(),
  risks: emptyRisks(),
  vendor: emptyVendor(),
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

export function recordToForm(record: ModuleRecord): PlatformFormValues {
  const extra = (record.extra_data ?? {}) as Record<string, unknown>
  const industry = categoryFromExtra(extra, "industry", emptyIndustry)

  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    identity: categoryFromExtra(extra, "identity", emptyIdentity),
    industry: {
      ...industry,
      vertical: industry.vertical || record.party_name || "",
    },
    features: categoryFromExtra(extra, "features", emptyFeatures),
    processes: categoryFromExtra(extra, "processes", emptyProcesses),
    data_requirements: categoryFromExtra(extra, "data_requirements", emptyDataRequirements),
    integration: categoryFromExtra(extra, "integration", emptyIntegration),
    compliance: categoryFromExtra(extra, "compliance", emptyCompliance),
    reporting: categoryFromExtra(extra, "reporting", emptyReporting),
    roles: categoryFromExtra(extra, "roles", emptyRoles),
    customization: categoryFromExtra(extra, "customization", emptyCustomization),
    scalability: categoryFromExtra(extra, "scalability", emptyScalability),
    mobile: categoryFromExtra(extra, "mobile", emptyMobile),
    implementation: categoryFromExtra(extra, "implementation", emptyImplementation),
    costs: categoryFromExtra(extra, "costs", emptyCosts),
    benefits: categoryFromExtra(extra, "benefits", emptyBenefits),
    risks: categoryFromExtra(extra, "risks", emptyRisks),
    vendor: categoryFromExtra(extra, "vendor", emptyVendor),
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevel(values: PlatformFormValues) {
  const vertical = values.industry.vertical.trim()
  let title = values.title.trim()
  if (!title) {
    title = values.identity.example_title.trim() || "Industry module"
  }

  return {
    title,
    party_name: vertical || null,
    amount: parseOptionalNumber(values.amount),
    start_date: values.start_date.trim() || null,
    end_date: values.end_date.trim() || null,
  }
}

export function buildExtraData(values: PlatformFormValues) {
  return {
    identity: values.identity,
    industry: values.industry,
    features: values.features,
    processes: values.processes,
    data_requirements: values.data_requirements,
    integration: values.integration,
    compliance: values.compliance,
    reporting: values.reporting,
    roles: values.roles,
    customization: values.customization,
    scalability: values.scalability,
    mobile: values.mobile,
    implementation: values.implementation,
    costs: values.costs,
    benefits: values.benefits,
    risks: values.risks,
    vendor: values.vendor,
  }
}

export function formToCreatePayload(values: PlatformFormValues) {
  const top = deriveTopLevel(values)
  const reference = values.reference.trim() || newPlatformReference()

  return {
    feature_code: values.feature_code,
    reference,
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

export function formToUpdatePayload(values: PlatformFormValues) {
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

export function newPlatformReference(): string {
  return `PLT-${Date.now().toString(36).toUpperCase()}`
}

export function keyLabelFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data as Record<string, unknown> | undefined
  const industry = (extra?.industry ?? {}) as Record<string, unknown>
  const vertical = strField(industry.vertical)
  if (vertical) return vertical
  return record.party_name ?? "—"
}

export function featureLabelFromCode(code: string): string {
  const labels: Record<string, string> = {
    business_intelligence: "Business Intelligence",
    ecommerce: "E-commerce Integration",
    field_service: "Service Management",
    retail_pos: "Retail / POS",
    plant_maintenance: "Plant Maintenance",
    compliance_risk: "Compliance & Risk",
  }
  return labels[code] ?? code
}
