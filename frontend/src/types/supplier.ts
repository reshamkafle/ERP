export type BankDetails = {
  account_number?: string | null
  ifsc?: string | null
  swift?: string | null
  beneficiary_name?: string | null
}

export type VendorDocuments = {
  w9?: string | null
  certificate_of_incorporation?: string | null
  insurance?: string | null
  other?: string | null
}

export type Supplier = {
  id: number
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
  bank_details: BankDetails | null
  vendor_category: string | null
  vendor_type: string | null
  approval_status: string | null
  performance_rating: string | null
  lead_time_days: number | null
  moq: string | null
  currency_code: string
  pricing_currency: string | null
  documents: VendorDocuments | null
}

export type SupplierListItem = Supplier & {
  total_spent: string
  purchase_count: number
}

export type SupplierListResponse = {
  items: SupplierListItem[]
  total: number
}

export type SupplierPurchaseSummary = {
  id: number
  created_at: string
  item_count: number
  total: string
}

export type SupplierDetail = Supplier & {
  total_spent: string
  purchase_count: number
  recent_purchases: SupplierPurchaseSummary[]
}
