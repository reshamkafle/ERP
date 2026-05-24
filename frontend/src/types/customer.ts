export type CustomerSegment = "VIP" | "REGULAR" | "NEW" | "PROSPECT" | "INACTIVE"
export type CustomerStatus = "ACTIVE" | "INACTIVE" | "PROSPECT" | "BLOCKED"
export type CustomerType =
  | "INDIVIDUAL"
  | "COMPANY"
  | "GOVERNMENT"
  | "DISTRIBUTOR"
  | "RETAIL"
  | "OTHER"
export type CustomerAddressType =
  | "PRIMARY"
  | "BILLING"
  | "SHIPPING"
  | "HEAD_OFFICE"
  | "BRANCH"
  | "FACTORY"
  | "OTHER"

export type BankDetails = {
  bank_name?: string | null
  account_number?: string | null
  iban?: string | null
  swift?: string | null
}

export type ExtendedData = {
  integration_ids?: {
    crm_id?: string | null
    ecommerce_id?: string | null
    legacy_id?: string | null
  }
  consent_flags?: {
    marketing?: boolean
    gdpr?: boolean
    ccpa?: boolean
  }
  custom_fields?: { key: string; value?: string | null }[]
  risk_rating?: string | null
  loyalty?: { tier?: string | null; points?: number | null }
  marketing?: {
    journey_stage?: string | null
    last_marketing_touch?: string | null
    campaign_membership?: string | null
    email_opt_in?: boolean | null
    marketing_source?: string | null
  }
  analytics?: {
    churn_risk_score?: number | string | null
    behavior_tags?: string[]
    labels?: string[]
  }
  service?: {
    contract_number?: string | null
    sla_tier?: string | null
    last_csat?: number | string | null
    last_nps?: number | null
    last_service_date?: string | null
    warranty_info?: string | null
    installed_base?: string | null
  }
}

export type CustomerContactRow = {
  id?: number
  customer_id?: number
  contact_code?: string | null
  salutation?: string | null
  first_name?: string | null
  middle_name?: string | null
  last_name?: string | null
  name: string
  email?: string | null
  email_secondary?: string | null
  phone?: string | null
  phone_secondary?: string | null
  title?: string | null
  department?: string | null
  role?: string | null
  is_primary?: boolean
  preferred_language?: string | null
  linkedin_url?: string | null
  birthday?: string | null
  anniversary?: string | null
  notes?: string | null
}

export type CustomerAddressRow = {
  id?: number
  customer_id?: number
  address_type: CustomerAddressType
  label?: string | null
  line1?: string | null
  line2?: string | null
  house_no?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  country?: string | null
  latitude?: string | null
  longitude?: string | null
  is_default?: boolean
}

export type CustomerSalesAreaRow = {
  id?: number
  customer_id?: number
  sales_org: string
  distribution_channel?: string | null
  division?: string | null
  credit_limit?: string | null
  payment_terms?: string | null
  pricing_procedure?: string | null
}

export type Customer = {
  id: number
  customer_code: string | null
  name: string
  legal_name: string | null
  trade_name: string | null
  search_terms: string | null
  status: CustomerStatus | null
  customer_type: CustomerType | null
  parent_customer_id: number | null
  phone: string | null
  mobile_phone: string | null
  fax: string | null
  email: string | null
  contact_name: string | null
  contact_phone: string | null
  contact_email: string | null
  timezone: string | null
  language: string | null
  latitude: string | null
  longitude: string | null
  billing_address_line1: string | null
  billing_address_line2: string | null
  billing_city: string | null
  billing_state: string | null
  billing_postal_code: string | null
  billing_country: string | null
  shipping_address_line1: string | null
  shipping_address_line2: string | null
  shipping_city: string | null
  shipping_state: string | null
  shipping_postal_code: string | null
  shipping_country: string | null
  industry: string | null
  company_size: string | null
  annual_revenue: string | null
  website: string | null
  segment: CustomerSegment | null
  customer_group: string | null
  credit_limit: string | null
  credit_status: string | null
  payment_terms: string | null
  reconciliation_account_id: number | null
  tax_id: string | null
  tax_registration_type: string | null
  tax_classification: string | null
  tax_exempt: boolean | null
  gst_number: string | null
  vat_number: string | null
  billing_preference: string | null
  bank_details: BankDetails | null
  dunning_procedure: string | null
  withholding_tax: string | null
  incoterms: string | null
  currency_code: string
  sales_rep: string | null
  price_group: string | null
  shipping_conditions: string | null
  delivering_plant: string | null
  order_probability: string | null
  lead_source: string | null
  year_founded: number | null
  ownership_type: string | null
  territory: string | null
  employee_count: number | null
  account_owner_id: number | null
  shipping_preference: string | null
  preferred_carrier: string | null
  receiving_hours: string | null
  freight_terms: string | null
  transport_zone: string | null
  extended_data: ExtendedData | null
  notes: string | null
  created_at: string
  updated_at: string
  contacts?: CustomerContactRow[]
  addresses?: CustomerAddressRow[]
  sales_areas?: CustomerSalesAreaRow[]
}

export type CustomerListResponse = {
  items: Customer[]
  total: number
}

export type CustomerSaleSummary = {
  id: number
  order_number: string
  created_at: string
  item_count: number
  total: string
  order_status: string
}

export type CustomerDetail = Customer & {
  recent_sales: CustomerSaleSummary[]
}

export type CustomerOverview = {
  customer_id: number
  total_revenue: string
  lifetime_value: string
  revenue_ytd: string
  revenue_last_year: string
  open_balance: string
  open_receivables: string
  sale_count: number
  last_purchase_date: string | null
  average_order_value: string
  purchase_frequency_per_year: string
  open_opportunity_count: number
  open_opportunity_value: string
  activity_count: number
  contact_count: number
  document_count: number
  payment_count: number
}

export type CustomerAuditLogEntry = {
  id: number
  customer_id: number
  user_id: number | null
  field_name: string
  old_value: Record<string, unknown> | null
  new_value: Record<string, unknown> | null
  change_summary: string | null
  created_at: string
}

export type ChartOfAccountOption = {
  id: number
  code: string
  name: string
}
