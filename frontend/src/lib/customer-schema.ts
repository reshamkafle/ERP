import { z } from "zod"

const optionalStr = z.string().optional().or(z.literal(""))

export const CUSTOMER_SEGMENTS = [
  "VIP",
  "REGULAR",
  "NEW",
  "PROSPECT",
  "INACTIVE",
] as const

export const CUSTOMER_STATUSES = ["ACTIVE", "INACTIVE", "PROSPECT", "BLOCKED"] as const

export const CUSTOMER_TYPES = [
  "INDIVIDUAL",
  "COMPANY",
  "GOVERNMENT",
  "DISTRIBUTOR",
  "RETAIL",
  "OTHER",
] as const

export const CUSTOMER_ADDRESS_TYPES = [
  "PRIMARY",
  "BILLING",
  "SHIPPING",
  "HEAD_OFFICE",
  "BRANCH",
  "FACTORY",
  "OTHER",
] as const

export const OWNERSHIP_TYPES = ["PUBLIC", "PRIVATE", "GOVERNMENT", "NON_PROFIT", "PARTNERSHIP", "OTHER"] as const

export const CREDIT_STATUS_OPTIONS = [
  { value: "", label: "—" },
  { value: "GOOD", label: "Good" },
  { value: "HOLD", label: "On hold" },
  { value: "BLOCKED", label: "Blocked" },
  { value: "REVIEW", label: "Under review" },
] as const

export const PAYMENT_TERMS_OPTIONS = [
  { value: "", label: "—" },
  { value: "Net 30", label: "Net 30" },
  { value: "Net 60", label: "Net 60" },
  { value: "COD", label: "COD" },
  { value: "Prepaid", label: "Prepaid" },
] as const

export const INCOTERMS_OPTIONS = [
  { value: "", label: "—" },
  { value: "EXW", label: "EXW" },
  { value: "FOB", label: "FOB" },
  { value: "CIF", label: "CIF" },
  { value: "DDP", label: "DDP" },
] as const

export const bankDetailsSchema = z.object({
  bank_name: optionalStr,
  account_number: optionalStr,
  iban: optionalStr,
  swift: optionalStr,
})

export const integrationIdsSchema = z.object({
  crm_id: optionalStr,
  ecommerce_id: optionalStr,
  legacy_id: optionalStr,
})

export const consentFlagsSchema = z.object({
  marketing: z.boolean().optional(),
  gdpr: z.boolean().optional(),
  ccpa: z.boolean().optional(),
})

export const customFieldSchema = z.object({
  key: z.string(),
  value: optionalStr,
})

export const loyaltySchema = z.object({
  tier: optionalStr,
  points: optionalStr,
})

export const marketingSchema = z.object({
  journey_stage: optionalStr,
  last_marketing_touch: optionalStr,
  campaign_membership: optionalStr,
  email_opt_in: z.boolean().optional(),
  marketing_source: optionalStr,
})

export const analyticsSchema = z.object({
  churn_risk_score: optionalStr,
  behavior_tags: optionalStr,
  labels: optionalStr,
})

export const serviceSchema = z.object({
  contract_number: optionalStr,
  sla_tier: optionalStr,
  last_csat: optionalStr,
  last_nps: optionalStr,
  last_service_date: optionalStr,
  warranty_info: optionalStr,
  installed_base: optionalStr,
})

export const extendedDataSchema = z.object({
  integration_ids: integrationIdsSchema,
  consent_flags: consentFlagsSchema,
  custom_fields: z.array(customFieldSchema),
  risk_rating: optionalStr,
  loyalty: loyaltySchema,
  marketing: marketingSchema,
  analytics: analyticsSchema,
  service: serviceSchema,
})

export const contactRowSchema = z.object({
  contact_code: optionalStr,
  salutation: optionalStr,
  first_name: optionalStr,
  middle_name: optionalStr,
  last_name: optionalStr,
  name: optionalStr,
  email: z.string().email().optional().or(z.literal("")),
  email_secondary: z.string().email().optional().or(z.literal("")),
  phone: optionalStr,
  phone_secondary: optionalStr,
  title: optionalStr,
  department: optionalStr,
  role: optionalStr,
  is_primary: z.boolean().optional(),
  preferred_language: optionalStr,
  linkedin_url: optionalStr,
  birthday: optionalStr,
  anniversary: optionalStr,
  notes: optionalStr,
})

export const addressRowSchema = z.object({
  address_type: z.enum(CUSTOMER_ADDRESS_TYPES),
  label: optionalStr,
  line1: optionalStr,
  line2: optionalStr,
  house_no: optionalStr,
  city: optionalStr,
  state: optionalStr,
  postal_code: optionalStr,
  country: optionalStr,
  latitude: optionalStr,
  longitude: optionalStr,
  is_default: z.boolean().optional(),
})

export const salesAreaRowSchema = z.object({
  sales_org: z.string().min(1, "Sales org required").max(64),
  distribution_channel: optionalStr,
  division: optionalStr,
  credit_limit: optionalStr,
  payment_terms: optionalStr,
  pricing_procedure: optionalStr,
})

export const customerFormSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  customer_code: optionalStr,
  legal_name: optionalStr,
  trade_name: optionalStr,
  search_terms: optionalStr,
  status: z.enum(CUSTOMER_STATUSES).optional().or(z.literal("")),
  customer_type: z.enum(CUSTOMER_TYPES).optional().or(z.literal("")),
  parent_customer_id: optionalStr,
  phone: z.string().max(64).optional(),
  mobile_phone: optionalStr,
  fax: optionalStr,
  email: z.string().email("Enter a valid email").optional().or(z.literal("")),
  timezone: optionalStr,
  language: optionalStr,
  latitude: optionalStr,
  longitude: optionalStr,
  segment: z.enum(CUSTOMER_SEGMENTS).optional().or(z.literal("")),
  customer_group: optionalStr,
  industry: optionalStr,
  company_size: optionalStr,
  annual_revenue: optionalStr,
  website: optionalStr,
  contact_name: optionalStr,
  contact_phone: optionalStr,
  contact_email: z.string().email("Enter a valid email").optional().or(z.literal("")),
  billing_address_line1: optionalStr,
  billing_address_line2: optionalStr,
  billing_city: optionalStr,
  billing_state: optionalStr,
  billing_postal_code: optionalStr,
  billing_country: optionalStr,
  shipping_address_line1: optionalStr,
  shipping_address_line2: optionalStr,
  shipping_city: optionalStr,
  shipping_state: optionalStr,
  shipping_postal_code: optionalStr,
  shipping_country: optionalStr,
  credit_limit: optionalStr,
  credit_status: optionalStr,
  payment_terms: optionalStr,
  reconciliation_account_id: optionalStr,
  tax_id: optionalStr,
  tax_registration_type: optionalStr,
  tax_classification: optionalStr,
  tax_exempt: z.boolean().optional(),
  gst_number: optionalStr,
  vat_number: optionalStr,
  billing_preference: optionalStr,
  bank_details: bankDetailsSchema,
  dunning_procedure: optionalStr,
  withholding_tax: optionalStr,
  incoterms: optionalStr,
  currency_code: z.string().max(3).default("USD"),
  sales_rep: optionalStr,
  price_group: optionalStr,
  shipping_conditions: optionalStr,
  delivering_plant: optionalStr,
  order_probability: optionalStr,
  lead_source: optionalStr,
  year_founded: optionalStr,
  ownership_type: optionalStr,
  territory: optionalStr,
  employee_count: optionalStr,
  account_owner_id: optionalStr,
  shipping_preference: optionalStr,
  preferred_carrier: optionalStr,
  receiving_hours: optionalStr,
  freight_terms: optionalStr,
  transport_zone: optionalStr,
  extended_data: extendedDataSchema,
  notes: z.string().optional(),
  contacts: z.array(contactRowSchema),
  addresses: z.array(addressRowSchema),
  sales_areas: z.array(salesAreaRowSchema),
})

export type CustomerFormValues = z.infer<typeof customerFormSchema>

export const defaultBankDetails = {
  bank_name: "",
  account_number: "",
  iban: "",
  swift: "",
}

export const defaultExtendedData: CustomerFormValues["extended_data"] = {
  integration_ids: { crm_id: "", ecommerce_id: "", legacy_id: "" },
  consent_flags: { marketing: false, gdpr: false, ccpa: false },
  custom_fields: [],
  risk_rating: "",
  loyalty: { tier: "", points: "" },
  marketing: {
    journey_stage: "",
    last_marketing_touch: "",
    campaign_membership: "",
    email_opt_in: false,
    marketing_source: "",
  },
  analytics: { churn_risk_score: "", behavior_tags: "", labels: "" },
  service: {
    contract_number: "",
    sla_tier: "",
    last_csat: "",
    last_nps: "",
    last_service_date: "",
    warranty_info: "",
    installed_base: "",
  },
}

export const defaultCustomerFormValues: CustomerFormValues = {
  name: "",
  customer_code: "",
  legal_name: "",
  trade_name: "",
  search_terms: "",
  status: "",
  customer_type: "",
  parent_customer_id: "",
  phone: "",
  mobile_phone: "",
  fax: "",
  email: "",
  timezone: "",
  language: "",
  latitude: "",
  longitude: "",
  segment: "",
  customer_group: "",
  industry: "",
  company_size: "",
  annual_revenue: "",
  website: "",
  contact_name: "",
  contact_phone: "",
  contact_email: "",
  billing_address_line1: "",
  billing_address_line2: "",
  billing_city: "",
  billing_state: "",
  billing_postal_code: "",
  billing_country: "",
  shipping_address_line1: "",
  shipping_address_line2: "",
  shipping_city: "",
  shipping_state: "",
  shipping_postal_code: "",
  shipping_country: "",
  credit_limit: "",
  credit_status: "",
  payment_terms: "",
  reconciliation_account_id: "",
  tax_id: "",
  tax_registration_type: "",
  tax_classification: "",
  tax_exempt: false,
  gst_number: "",
  vat_number: "",
  billing_preference: "",
  bank_details: defaultBankDetails,
  dunning_procedure: "",
  withholding_tax: "",
  incoterms: "",
  currency_code: "USD",
  sales_rep: "",
  price_group: "",
  shipping_conditions: "",
  delivering_plant: "",
  order_probability: "",
  lead_source: "",
  year_founded: "",
  ownership_type: "",
  territory: "",
  employee_count: "",
  account_owner_id: "",
  shipping_preference: "",
  preferred_carrier: "",
  receiving_hours: "",
  freight_terms: "",
  transport_zone: "",
  extended_data: defaultExtendedData,
  notes: "",
  contacts: [],
  addresses: [],
  sales_areas: [],
}

export function newCustomerCodeSuggestion(): string {
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, "")
  const suffix = String(Math.floor(Math.random() * 900) + 100)
  return `CUST-${day}-${suffix}`
}

function parseOptionalNumber(raw: string | undefined): number | null {
  if (!raw?.trim()) return null
  const n = Number(raw)
  return Number.isNaN(n) ? null : n
}

export function customerFormToPayload(values: CustomerFormValues): Record<string, unknown> {
  const trim = (s: string | undefined) => (s?.trim() ? s.trim() : null)

  const payload: Record<string, unknown> = {
    name: values.name.trim(),
    customer_code: trim(values.customer_code),
    legal_name: trim(values.legal_name),
    trade_name: trim(values.trade_name),
    search_terms: trim(values.search_terms),
    status: values.status || null,
    customer_type: values.customer_type || null,
    parent_customer_id: values.parent_customer_id
      ? Number(values.parent_customer_id)
      : null,
    phone: trim(values.phone),
    mobile_phone: trim(values.mobile_phone),
    fax: trim(values.fax),
    email: trim(values.email),
    timezone: trim(values.timezone),
    language: trim(values.language),
    latitude: parseOptionalNumber(values.latitude),
    longitude: parseOptionalNumber(values.longitude),
    segment: values.segment || null,
    customer_group: trim(values.customer_group),
    industry: trim(values.industry),
    company_size: trim(values.company_size),
    annual_revenue: parseOptionalNumber(values.annual_revenue),
    website: trim(values.website),
    contact_name: trim(values.contact_name),
    contact_phone: trim(values.contact_phone),
    contact_email: trim(values.contact_email),
    billing_address_line1: trim(values.billing_address_line1),
    billing_address_line2: trim(values.billing_address_line2),
    billing_city: trim(values.billing_city),
    billing_state: trim(values.billing_state),
    billing_postal_code: trim(values.billing_postal_code),
    billing_country: trim(values.billing_country),
    shipping_address_line1: trim(values.shipping_address_line1),
    shipping_address_line2: trim(values.shipping_address_line2),
    shipping_city: trim(values.shipping_city),
    shipping_state: trim(values.shipping_state),
    shipping_postal_code: trim(values.shipping_postal_code),
    shipping_country: trim(values.shipping_country),
    credit_limit: parseOptionalNumber(values.credit_limit),
    credit_status: trim(values.credit_status),
    payment_terms: trim(values.payment_terms),
    reconciliation_account_id: values.reconciliation_account_id
      ? Number(values.reconciliation_account_id)
      : null,
    tax_id: trim(values.tax_id),
    tax_registration_type: trim(values.tax_registration_type),
    tax_classification: trim(values.tax_classification),
    tax_exempt: values.tax_exempt ?? null,
    gst_number: trim(values.gst_number),
    vat_number: trim(values.vat_number),
    billing_preference: trim(values.billing_preference),
    dunning_procedure: trim(values.dunning_procedure),
    withholding_tax: trim(values.withholding_tax),
    incoterms: trim(values.incoterms),
    currency_code: values.currency_code || "USD",
    sales_rep: trim(values.sales_rep),
    price_group: trim(values.price_group),
    shipping_conditions: trim(values.shipping_conditions),
    delivering_plant: trim(values.delivering_plant),
    order_probability: parseOptionalNumber(values.order_probability),
    lead_source: trim(values.lead_source),
    year_founded: values.year_founded ? Number(values.year_founded) : null,
    ownership_type: values.ownership_type || null,
    territory: trim(values.territory),
    employee_count: values.employee_count ? Number(values.employee_count) : null,
    account_owner_id: values.account_owner_id ? Number(values.account_owner_id) : null,
    shipping_preference: trim(values.shipping_preference),
    preferred_carrier: trim(values.preferred_carrier),
    receiving_hours: trim(values.receiving_hours),
    freight_terms: trim(values.freight_terms),
    transport_zone: trim(values.transport_zone),
    notes: trim(values.notes),
  }

  const bank = values.bank_details
  if (bank.bank_name || bank.account_number || bank.iban || bank.swift) {
    payload.bank_details = {
      bank_name: trim(bank.bank_name),
      account_number: trim(bank.account_number),
      iban: trim(bank.iban),
      swift: trim(bank.swift),
    }
  } else {
    payload.bank_details = null
  }

  const ext = values.extended_data
  const behaviorTags = ext.analytics.behavior_tags
    ? ext.analytics.behavior_tags.split(",").map((t) => t.trim()).filter(Boolean)
    : []
  const labels = ext.analytics.labels
    ? ext.analytics.labels.split(",").map((t) => t.trim()).filter(Boolean)
    : []
  const hasExt =
    ext.integration_ids.crm_id ||
    ext.integration_ids.ecommerce_id ||
    ext.integration_ids.legacy_id ||
    ext.risk_rating ||
    ext.loyalty.tier ||
    ext.custom_fields.length > 0 ||
    ext.consent_flags.marketing ||
    ext.consent_flags.gdpr ||
    ext.consent_flags.ccpa ||
    ext.marketing.journey_stage ||
    ext.marketing.campaign_membership ||
    ext.marketing.marketing_source ||
    ext.marketing.last_marketing_touch ||
    ext.marketing.email_opt_in ||
    ext.service.contract_number ||
    ext.service.sla_tier ||
    ext.analytics.churn_risk_score ||
    behaviorTags.length > 0 ||
    labels.length > 0
  if (hasExt) {
    payload.extended_data = {
      integration_ids: {
        crm_id: trim(ext.integration_ids.crm_id),
        ecommerce_id: trim(ext.integration_ids.ecommerce_id),
        legacy_id: trim(ext.integration_ids.legacy_id),
      },
      consent_flags: ext.consent_flags,
      custom_fields: ext.custom_fields
        .filter((f) => f.key.trim())
        .map((f) => ({ key: f.key.trim(), value: trim(f.value) })),
      risk_rating: trim(ext.risk_rating),
      loyalty: {
        tier: trim(ext.loyalty.tier),
        points: ext.loyalty.points ? Number(ext.loyalty.points) : null,
      },
      marketing: {
        journey_stage: trim(ext.marketing.journey_stage),
        last_marketing_touch: trim(ext.marketing.last_marketing_touch) || null,
        campaign_membership: trim(ext.marketing.campaign_membership),
        email_opt_in: ext.marketing.email_opt_in ?? null,
        marketing_source: trim(ext.marketing.marketing_source),
      },
      analytics: {
        churn_risk_score: parseOptionalNumber(ext.analytics.churn_risk_score),
        behavior_tags: behaviorTags,
        labels: labels,
      },
      service: {
        contract_number: trim(ext.service.contract_number),
        sla_tier: trim(ext.service.sla_tier),
        last_csat: parseOptionalNumber(ext.service.last_csat),
        last_nps: ext.service.last_nps ? Number(ext.service.last_nps) : null,
        last_service_date: trim(ext.service.last_service_date) || null,
        warranty_info: trim(ext.service.warranty_info),
        installed_base: trim(ext.service.installed_base),
      },
    }
  } else {
    payload.extended_data = null
  }

  if (values.contacts.length > 0) {
    payload.contacts = values.contacts.map((c) => {
      const parts = [c.salutation, c.first_name, c.middle_name, c.last_name].filter((p) => p?.trim())
      const displayName = parts.length ? parts.join(" ").trim() : (c.name?.trim() || "Contact")
      return {
        contact_code: trim(c.contact_code),
        salutation: trim(c.salutation),
        first_name: trim(c.first_name),
        middle_name: trim(c.middle_name),
        last_name: trim(c.last_name),
        name: displayName,
        email: trim(c.email),
        email_secondary: trim(c.email_secondary),
        phone: trim(c.phone),
        phone_secondary: trim(c.phone_secondary),
        title: trim(c.title),
        department: trim(c.department),
        role: trim(c.role),
        is_primary: c.is_primary ?? false,
        preferred_language: trim(c.preferred_language),
        linkedin_url: trim(c.linkedin_url),
        birthday: trim(c.birthday) || null,
        anniversary: trim(c.anniversary) || null,
        notes: trim(c.notes),
      }
    })
  }

  if (values.addresses.length > 0) {
    payload.addresses = values.addresses.map((a) => ({
      address_type: a.address_type,
      label: trim(a.label),
      line1: trim(a.line1),
      line2: trim(a.line2),
      house_no: trim(a.house_no),
      city: trim(a.city),
      state: trim(a.state),
      postal_code: trim(a.postal_code),
      country: trim(a.country),
      latitude: parseOptionalNumber(a.latitude),
      longitude: parseOptionalNumber(a.longitude),
      is_default: a.is_default ?? false,
    }))
  }

  if (values.sales_areas.length > 0) {
    payload.sales_areas = values.sales_areas.map((s) => ({
      sales_org: s.sales_org.trim(),
      distribution_channel: trim(s.distribution_channel),
      division: trim(s.division),
      credit_limit: parseOptionalNumber(s.credit_limit),
      payment_terms: trim(s.payment_terms),
      pricing_procedure: trim(s.pricing_procedure),
    }))
  }

  return payload
}
