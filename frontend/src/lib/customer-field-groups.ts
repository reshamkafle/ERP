import type { CustomerFormValues } from "@/lib/customer-schema"
import {
  CREDIT_STATUS_OPTIONS,
  CUSTOMER_SEGMENTS,
  CUSTOMER_STATUSES,
  CUSTOMER_TYPES,
  INCOTERMS_OPTIONS,
  OWNERSHIP_TYPES,
  PAYMENT_TERMS_OPTIONS,
} from "@/lib/customer-schema"

export type CustomerFieldType = "text" | "number" | "textarea" | "select" | "checkbox"

export type CustomerFieldDef = {
  path: keyof CustomerFormValues | string
  label: string
  type?: CustomerFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type CustomerTabDef = {
  id: string
  title: string
  description?: string
  fields: CustomerFieldDef[]
}

const emptyOption = { value: "", label: "—" }

const segmentOptions = [
  emptyOption,
  ...CUSTOMER_SEGMENTS.map((s) => ({ value: s, label: s })),
]

const statusOptions = [
  emptyOption,
  ...CUSTOMER_STATUSES.map((s) => ({
    value: s,
    label: s === "BLOCKED" ? "Blacklisted" : s.charAt(0) + s.slice(1).toLowerCase(),
  })),
]

const typeOptions = [
  emptyOption,
  ...CUSTOMER_TYPES.map((t) => ({ value: t, label: t.replace(/_/g, " ") })),
]

const ownershipOptions = [
  emptyOption,
  ...OWNERSHIP_TYPES.map((o) => ({ value: o, label: o.replace(/_/g, " ") })),
]

const billingPrefOptions = [
  emptyOption,
  { value: "email", label: "Email" },
  { value: "portal", label: "Customer portal" },
  { value: "paper", label: "Paper invoice" },
]

export const CUSTOMER_FORM_TABS: CustomerTabDef[] = [
  {
    id: "account",
    title: "Account Master",
    fields: [
      { path: "customer_code", label: "Customer ID / code" },
      { path: "name", label: "Customer / company name *", colSpan: 2 },
      { path: "legal_name", label: "Legal / registered name" },
      { path: "trade_name", label: "Trade name / DBA" },
      { path: "customer_type", label: "Customer type", type: "select", options: [...typeOptions] },
      { path: "segment", label: "Segment", type: "select", options: segmentOptions },
      { path: "status", label: "Account status", type: "select", options: statusOptions },
      { path: "parent_customer_id", label: "Parent company ID" },
      { path: "industry", label: "Industry / sector" },
      { path: "company_size", label: "Company size (revenue band)" },
      { path: "employee_count", label: "No. of employees", type: "number" },
      { path: "annual_revenue", label: "Annual revenue", type: "number" },
      { path: "website", label: "Website", colSpan: 2 },
      { path: "year_founded", label: "Year founded", type: "number" },
      { path: "ownership_type", label: "Ownership type", type: "select", options: ownershipOptions },
      { path: "search_terms", label: "Search terms", colSpan: 2 },
      { path: "notes", label: "Notes", type: "textarea", colSpan: 2 },
    ],
  },
  {
    id: "contact_address",
    title: "Contact & Address",
    description: "Primary communication and billing/shipping addresses.",
    fields: [
      { path: "phone", label: "Main phone" },
      { path: "mobile_phone", label: "Mobile" },
      { path: "fax", label: "Fax" },
      { path: "email", label: "Email", colSpan: 2 },
      { path: "timezone", label: "Time zone" },
      { path: "language", label: "Language" },
      { path: "latitude", label: "GPS latitude" },
      { path: "longitude", label: "GPS longitude" },
      { path: "billing_address_line1", label: "Billing street line 1", colSpan: 2 },
      { path: "billing_address_line2", label: "Billing street line 2", colSpan: 2 },
      { path: "billing_city", label: "Billing city" },
      { path: "billing_state", label: "Billing state" },
      { path: "billing_postal_code", label: "Billing ZIP / postcode" },
      { path: "billing_country", label: "Billing country" },
      { path: "shipping_address_line1", label: "Shipping street line 1", colSpan: 2 },
      { path: "shipping_address_line2", label: "Shipping street line 2", colSpan: 2 },
      { path: "shipping_city", label: "Shipping city" },
      { path: "shipping_state", label: "Shipping state" },
      { path: "shipping_postal_code", label: "Shipping ZIP / postcode" },
      { path: "shipping_country", label: "Shipping country" },
      { path: "shipping_preference", label: "Shipping preference", colSpan: 2 },
    ],
  },
  {
    id: "commercial",
    title: "Credit & Terms",
    fields: [
      { path: "currency_code", label: "Currency" },
      { path: "credit_limit", label: "Credit limit", type: "number" },
      {
        path: "credit_status",
        label: "Credit status",
        type: "select",
        options: [...CREDIT_STATUS_OPTIONS],
      },
      {
        path: "payment_terms",
        label: "Payment / credit terms",
        type: "select",
        options: [...PAYMENT_TERMS_OPTIONS],
      },
      { path: "extended_data.risk_rating", label: "Risk / credit rating" },
      { path: "tax_id", label: "Tax ID" },
      { path: "gst_number", label: "GST number" },
      { path: "vat_number", label: "VAT number" },
      { path: "tax_registration_type", label: "Tax registration type" },
      { path: "tax_classification", label: "Tax classification" },
      { path: "tax_exempt", label: "Tax exempt", type: "checkbox" },
      { path: "reconciliation_account_id", label: "Reconciliation account ID" },
      {
        path: "billing_preference",
        label: "Billing preference",
        type: "select",
        options: billingPrefOptions,
      },
      { path: "incoterms", label: "Incoterms", type: "select", options: [...INCOTERMS_OPTIONS] },
      { path: "bank_details.bank_name", label: "Bank name" },
      { path: "bank_details.account_number", label: "Account number" },
      { path: "bank_details.iban", label: "IBAN" },
      { path: "bank_details.swift", label: "SWIFT" },
      { path: "dunning_procedure", label: "Dunning procedure" },
      { path: "withholding_tax", label: "Withholding tax" },
    ],
  },
  {
    id: "sales",
    title: "Sales & Acquisition",
    fields: [
      { path: "account_owner_id", label: "Account owner" },
      { path: "sales_rep", label: "Sales representative" },
      { path: "territory", label: "Territory / region" },
      { path: "lead_source", label: "Acquisition source" },
      { path: "customer_group", label: "Customer group" },
      { path: "price_group", label: "Price group" },
      { path: "shipping_conditions", label: "Shipping conditions" },
      { path: "delivering_plant", label: "Delivering plant" },
      { path: "order_probability", label: "Order probability %", type: "number" },
    ],
  },
  {
    id: "logistics",
    title: "Logistics",
    fields: [
      { path: "preferred_carrier", label: "Preferred carrier" },
      { path: "receiving_hours", label: "Receiving hours", colSpan: 2 },
      { path: "freight_terms", label: "Freight terms" },
      { path: "transport_zone", label: "Transport zone" },
    ],
  },
  {
    id: "marketing",
    title: "Marketing & Consent",
    fields: [
      { path: "extended_data.marketing.marketing_source", label: "Marketing source" },
      { path: "extended_data.marketing.campaign_membership", label: "Campaign membership" },
      { path: "extended_data.marketing.journey_stage", label: "Customer journey stage" },
      { path: "extended_data.marketing.last_marketing_touch", label: "Last marketing touch (ISO date)" },
      { path: "extended_data.marketing.email_opt_in", label: "Email opt-in", type: "checkbox" },
    ],
  },
  {
    id: "service",
    title: "Service & Support",
    fields: [
      { path: "extended_data.service.contract_number", label: "Service contract number" },
      { path: "extended_data.service.sla_tier", label: "SLA tier (Gold/Silver/Bronze)" },
      { path: "extended_data.service.last_csat", label: "Last CSAT", type: "number" },
      { path: "extended_data.service.last_nps", label: "Last NPS", type: "number" },
      { path: "extended_data.service.last_service_date", label: "Last service date (YYYY-MM-DD)" },
      { path: "extended_data.service.warranty_info", label: "Warranty information", type: "textarea", colSpan: 2 },
      { path: "extended_data.service.installed_base", label: "Product ownership / installed base", colSpan: 2 },
    ],
  },
  {
    id: "analytics",
    title: "Segmentation & Analytics",
    fields: [
      { path: "extended_data.analytics.churn_risk_score", label: "Churn risk score", type: "number" },
      { path: "extended_data.loyalty.tier", label: "Loyalty tier" },
      { path: "extended_data.loyalty.points", label: "Loyalty points", type: "number" },
      { path: "extended_data.analytics.behavior_tags", label: "Buying behavior tags (comma-separated)", colSpan: 2 },
      { path: "extended_data.analytics.labels", label: "Custom labels (comma-separated)", colSpan: 2 },
    ],
  },
  {
    id: "integrations",
    title: "System & Integrations",
    fields: [
      { path: "extended_data.integration_ids.crm_id", label: "CRM integration ID" },
      { path: "extended_data.integration_ids.ecommerce_id", label: "E-commerce ID" },
      { path: "extended_data.integration_ids.legacy_id", label: "Legacy / accounting ID" },
    ],
  },
]

export const CUSTOMER_TABS: CustomerTabDef[] = [
  {
    id: "profile",
    title: "Profile",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "account")!.fields.slice(0, 8),
  },
  {
    id: "company",
    title: "Company",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "account")!.fields.slice(8, 14),
  },
  {
    id: "contacts",
    title: "Primary contact",
    fields: [
      { path: "contact_name", label: "Contact name" },
      { path: "contact_phone", label: "Contact phone" },
      { path: "contact_email", label: "Contact email", colSpan: 2 },
    ],
  },
  {
    id: "billing",
    title: "Billing address",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "contact_address")!.fields.filter((f) =>
      String(f.path).startsWith("billing"),
    ),
  },
  {
    id: "shipping",
    title: "Shipping",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "contact_address")!.fields.filter((f) =>
      String(f.path).startsWith("shipping"),
    ),
  },
  {
    id: "commercial",
    title: "Commercial",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "commercial")!.fields.slice(0, 6),
  },
  {
    id: "tax",
    title: "Tax",
    fields: CUSTOMER_FORM_TABS.find((t) => t.id === "commercial")!.fields.slice(6, 12),
  },
  {
    id: "notes",
    title: "Notes",
    fields: [{ path: "notes", label: "Notes", type: "textarea", colSpan: 2 }],
  },
]
