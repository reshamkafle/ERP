import { z } from "zod"

const optionalStr = z.string()

export const bankDetailsSchema = z.object({
  account_number: optionalStr,
  ifsc: optionalStr,
  swift: optionalStr,
  beneficiary_name: optionalStr,
})

export const vendorDocumentsSchema = z.object({
  w9: optionalStr,
  certificate_of_incorporation: optionalStr,
  insurance: optionalStr,
  other: optionalStr,
})

export const supplierFormSchema = z.object({
  vendor_code: z.string().min(1, "Vendor code is required").max(32),
  name: z.string().min(1, "Vendor name is required").max(255),
  legal_name: optionalStr.max(255),
  dba: optionalStr.max(255),
  address_line1: optionalStr.max(255),
  address_line2: optionalStr.max(255),
  city: optionalStr.max(120),
  state: optionalStr.max(120),
  postal_code: optionalStr.max(32),
  country: optionalStr.max(64),
  phone: optionalStr.max(64),
  email: z
    .string()
    .email("Enter a valid email")
    .optional()
    .or(z.literal("")),
  website: optionalStr.max(255),
  tax_id: optionalStr.max(64),
  payment_terms: optionalStr.max(120),
  incoterms: optionalStr.max(32),
  bank_details: bankDetailsSchema,
  vendor_category: optionalStr.max(64),
  vendor_type: optionalStr.max(64),
  approval_status: optionalStr.max(32),
  performance_rating: optionalStr,
  lead_time_days: optionalStr,
  moq: optionalStr,
  currency_code: z.string().min(3).max(3),
  pricing_currency: optionalStr.max(3),
  documents: vendorDocumentsSchema,
})

export type SupplierFormValues = z.infer<typeof supplierFormSchema>

export const APPROVAL_STATUS_OPTIONS = [
  { value: "", label: "—" },
  { value: "PREFERRED", label: "Preferred" },
  { value: "APPROVED", label: "Approved" },
  { value: "PENDING", label: "Pending approval" },
  { value: "BLACKLISTED", label: "Blacklisted" },
] as const

export const VENDOR_TYPE_OPTIONS = [
  { value: "", label: "—" },
  { value: "LOCAL", label: "Local" },
  { value: "INTERNATIONAL", label: "International" },
  { value: "STRATEGIC", label: "Strategic" },
] as const

export const defaultSupplierFormValues: SupplierFormValues = {
  vendor_code: "",
  name: "",
  legal_name: "",
  dba: "",
  address_line1: "",
  address_line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
  phone: "",
  email: "",
  website: "",
  tax_id: "",
  payment_terms: "",
  incoterms: "",
  bank_details: {
    account_number: "",
    ifsc: "",
    swift: "",
    beneficiary_name: "",
  },
  vendor_category: "",
  vendor_type: "",
  approval_status: "",
  performance_rating: "",
  lead_time_days: "",
  moq: "",
  currency_code: "USD",
  pricing_currency: "",
  documents: {
    w9: "",
    certificate_of_incorporation: "",
    insurance: "",
    other: "",
  },
}

export function supplierToForm(supplier: {
  vendor_code: string
  name: string
  legal_name: string | null
  dba: string | null
  address_line1: string | null
  address_line2: string | null
  city: string | null
  state: string | null
  postal_code: string | null
  country: string | null
  phone: string | null
  email: string | null
  website: string | null
  tax_id: string | null
  payment_terms: string | null
  incoterms: string | null
  bank_details: Record<string, string | null | undefined> | null
  vendor_category: string | null
  vendor_type: string | null
  approval_status: string | null
  performance_rating: string | null
  lead_time_days: number | null
  moq: string | null
  currency_code: string
  pricing_currency: string | null
  documents: Record<string, string | null | undefined> | null
}): SupplierFormValues {
  const bank = supplier.bank_details ?? {}
  const docs = supplier.documents ?? {}
  return {
    vendor_code: supplier.vendor_code,
    name: supplier.name,
    legal_name: supplier.legal_name ?? "",
    dba: supplier.dba ?? "",
    address_line1: supplier.address_line1 ?? "",
    address_line2: supplier.address_line2 ?? "",
    city: supplier.city ?? "",
    state: supplier.state ?? "",
    postal_code: supplier.postal_code ?? "",
    country: supplier.country ?? "",
    phone: supplier.phone ?? "",
    email: supplier.email ?? "",
    website: supplier.website ?? "",
    tax_id: supplier.tax_id ?? "",
    payment_terms: supplier.payment_terms ?? "",
    incoterms: supplier.incoterms ?? "",
    bank_details: {
      account_number: bank.account_number ?? "",
      ifsc: bank.ifsc ?? "",
      swift: bank.swift ?? "",
      beneficiary_name: bank.beneficiary_name ?? "",
    },
    vendor_category: supplier.vendor_category ?? "",
    vendor_type: supplier.vendor_type ?? "",
    approval_status: supplier.approval_status ?? "",
    performance_rating:
      supplier.performance_rating != null ? String(supplier.performance_rating) : "",
    lead_time_days:
      supplier.lead_time_days != null ? String(supplier.lead_time_days) : "",
    moq: supplier.moq != null ? String(supplier.moq) : "",
    currency_code: supplier.currency_code,
    pricing_currency: supplier.pricing_currency ?? "",
    documents: {
      w9: docs.w9 ?? "",
      certificate_of_incorporation: docs.certificate_of_incorporation ?? "",
      insurance: docs.insurance ?? "",
      other: docs.other ?? "",
    },
  }
}

function parseOptionalInt(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number.parseInt(t, 10)
  return Number.isFinite(n) ? n : null
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function cleanJsonSection<T extends Record<string, string>>(
  section: T,
): Record<string, string> | null {
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(section)) {
    const t = v.trim()
    if (t) out[k] = t
  }
  return Object.keys(out).length ? out : null
}

export function formToSupplierPayload(values: SupplierFormValues) {
  return {
    vendor_code: values.vendor_code.trim().toUpperCase(),
    name: values.name.trim(),
    legal_name: values.legal_name.trim() || null,
    dba: values.dba.trim() || null,
    address_line1: values.address_line1.trim() || null,
    address_line2: values.address_line2.trim() || null,
    city: values.city.trim() || null,
    state: values.state.trim() || null,
    postal_code: values.postal_code.trim() || null,
    country: values.country.trim() || null,
    phone: values.phone.trim() || null,
    email: (values.email ?? "").trim() || null,
    website: values.website.trim() || null,
    tax_id: values.tax_id.trim() || null,
    payment_terms: values.payment_terms.trim() || null,
    incoterms: values.incoterms.trim() || null,
    bank_details: cleanJsonSection(values.bank_details),
    vendor_category: values.vendor_category.trim() || null,
    vendor_type: values.vendor_type.trim() || null,
    approval_status: values.approval_status.trim() || null,
    performance_rating: parseOptionalNumber(values.performance_rating),
    lead_time_days: parseOptionalInt(values.lead_time_days),
    moq: parseOptionalNumber(values.moq),
    currency_code: values.currency_code.trim().toUpperCase() || "USD",
    pricing_currency: values.pricing_currency.trim().toUpperCase() || null,
    documents: cleanJsonSection(values.documents),
  }
}

export function newVendorCodeSuggestion(): string {
  return `VND-${Date.now().toString(36).toUpperCase().slice(-8)}`
}
