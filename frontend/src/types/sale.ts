export type SaleOrderStatus =
  | "DRAFT"
  | "CREATED"
  | "RELEASED"
  | "IN_PROCESS"
  | "DELIVERED"
  | "INVOICED"
  | "CLOSED"
  | "CANCELLED"

export type SaleOrderType = "STANDARD" | "RUSH" | "SAMPLE" | "RETURN" | "EXPORT"
export type SaleChannel = "DIRECT" | "DISTRIBUTOR" | "ECOMMERCE" | "RETAIL"
export type SaleOrderSource = "PHONE" | "EMAIL" | "PORTAL" | "WEBSITE" | "EDI" | "MOBILE"
export type OrderPriority = "HIGH" | "MEDIUM" | "LOW"
export type SaleLineStatus =
  | "OPEN"
  | "ALLOCATED"
  | "PARTIAL"
  | "DELIVERED"
  | "INVOICED"
  | "CANCELLED"
export type CreditCheckStatus = "NOT_RUN" | "PASSED" | "FAILED" | "OVERRIDE"
export type AtpCheckStatus = "NOT_RUN" | "AVAILABLE" | "PARTIAL" | "UNAVAILABLE"
export type DocumentPaymentStatus = "UNPAID" | "PARTIAL" | "PAID"
export type DeliveryStatus = "NOT_STARTED" | "PENDING" | "PARTIAL" | "COMPLETE" | "BLOCKED"
export type BillingStatus = "NOT_INVOICED" | "PARTIAL" | "INVOICED" | "COMPLETE"
export type SalePartnerRole =
  | "SOLD_TO"
  | "SHIP_TO"
  | "BILL_TO"
  | "PAYER"
  | "FORWARDING_AGENT"
  | "SALES_EMPLOYEE"

export type AddressBlock = {
  line1?: string | null
  line2?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  country?: string | null
}

export type CustomerSnapshot = {
  customer_id?: number | null
  customer_code?: string | null
  name?: string | null
  billing_address?: AddressBlock | null
  shipping_address?: AddressBlock | null
  contact_name?: string | null
  contact_phone?: string | null
  contact_email?: string | null
  customer_group?: string | null
  credit_limit?: string | null
  credit_status?: string | null
  payment_terms?: string | null
  tax_id?: string | null
  gst_number?: string | null
  vat_number?: string | null
  shipping_preference?: string | null
  incoterms?: string | null
}

export type SalePartnerInput = {
  role: SalePartnerRole
  customer_id?: number | null
  supplier_id?: number | null
  user_id?: number | null
  name_override?: string | null
  address?: AddressBlock | null
}

export type SalePartner = SalePartnerInput & {
  id: number
  customer_name?: string | null
  supplier_name?: string | null
  user_email?: string | null
}

export type SaleOrderSummary = {
  total_items: number
  total_quantity: number
  total_net: string
  total_tax: string
  total_discount: string
  freight: string
  insurance: string
  handling: string
  grand_total: string
}

export type SaleItemLine = {
  id?: number
  product_id: number
  quantity: number
  unit_price?: string | null
  description?: string | null
  uom?: string | null
  alternate_uom?: string | null
  uom_conversion_factor?: string | null
  discount_percent?: string
  discount_amount?: string
  tax_code?: string | null
  tax_rate_id?: number | null
  requested_delivery_date?: string | null
  confirmed_delivery_date?: string | null
  product_category?: string | null
  item_category?: string | null
  gross_price?: string | null
  warehouse_id?: number | null
  storage_location_id?: number | null
  batch_number?: string | null
  serial_number?: string | null
  delivery_block?: string | null
  billing_block?: string | null
  rejection_reason?: string | null
  net_weight?: string | null
  gross_weight?: string | null
  volume?: string | null
  substitute_product_id?: number | null
  line_text?: string | null
  line_status?: SaleLineStatus | null
}

export type SaleItem = {
  id: number
  line_number: number
  product_id: number
  product_name: string
  product_sku: string
  description: string | null
  quantity: number
  uom: string | null
  alternate_uom: string | null
  uom_conversion_factor: string | null
  unit_price: string
  price_at_sale: string
  gross_price: string | null
  discount_percent: string
  discount_amount: string
  tax_code: string | null
  tax_rate_id: number | null
  tax_amount: string
  net_amount: string
  line_total: string
  requested_delivery_date: string | null
  confirmed_delivery_date: string | null
  confirmed_quantity: number
  delivered_quantity: number
  line_status: SaleLineStatus
  backorder_quantity: number
  product_category: string | null
  item_category: string | null
  warehouse_id: number | null
  warehouse_name: string | null
  storage_location_id: number | null
  batch_number: string | null
  serial_number: string | null
  delivery_block: string | null
  billing_block: string | null
  rejection_reason: string | null
  net_weight: string | null
  gross_weight: string | null
  volume: string | null
  substitute_product_id: number | null
  substitute_product_sku: string | null
  line_text: string | null
}

export type SaleOrder = {
  id: number
  order_number: string
  order_status: SaleOrderStatus
  order_date: string
  order_type: SaleOrderType
  sales_channel: SaleChannel | null
  order_source: SaleOrderSource | null
  priority: OrderPriority
  salesperson_id: number | null
  salesperson_email: string | null
  is_pos_checkout: boolean
  customer_id: number | null
  customer_name: string | null
  cashier_email: string | null
  created_at: string
  updated_at: string | null
  updated_by_email: string | null
  items: SaleItem[]
  partners: SalePartner[]
  summary: SaleOrderSummary | null
  gross_total: string
  header_discount_amount: string
  freight_amount: string
  insurance_amount: string
  handling_amount: string
  subtotal: string
  tax: string
  total: string
  amount_paid: string
  payment_status: DocumentPaymentStatus
  currency_code: string
  price_list_code: string | null
  pricing_procedure: string | null
  payment_terms: string | null
  payment_due_date: string | null
  payment_method_id: number | null
  warehouse_id: number | null
  warehouse_name: string | null
  shipping_point_id: number | null
  shipping_point_name: string | null
  partial_delivery_allowed: boolean
  complete_delivery_required: boolean
  planned_ship_date: string | null
  requested_delivery_date: string | null
  shipping_method: string | null
  shipping_conditions: string | null
  transportation_group: string | null
  loading_group: string | null
  incoterms: string | null
  incoterms_location: string | null
  delivery_block: string | null
  sales_organization: string | null
  distribution_channel: string | null
  division: string | null
  sales_office: string | null
  sales_group: string | null
  customer_po_number: string | null
  customer_po_date: string | null
  opportunity_id: number | null
  campaign_id: string | null
  price_group: string | null
  header_text: string | null
  credit_check_status: CreditCheckStatus
  atp_check_status: AtpCheckStatus
  invoice_status: BillingStatus | null
  delivery_status: DeliveryStatus | null
  approval_status: string | null
  customer_snapshot: Record<string, unknown> | null
  pricing_conditions: Record<string, unknown> | null
  delivery_logistics: Record<string, unknown> | null
  billing_financial: Record<string, unknown> | null
  terms_compliance: Record<string, unknown> | null
  references: Record<string, unknown> | null
  attachments: Record<string, unknown>[] | null
  workflow_history: Record<string, unknown>[] | null
}

export type SaleListItem = {
  id: number
  order_number: string
  order_status: SaleOrderStatus
  order_type: SaleOrderType
  customer_id: number | null
  customer_name: string | null
  cashier_email: string | null
  created_at: string
  order_date: string
  item_count: number
  total: string
  payment_status: DocumentPaymentStatus
  currency_code: string
  delivery_status: DeliveryStatus | null
}

export type SaleListResponse = {
  items: SaleListItem[]
  total: number
}

export type SaleLookups = {
  customers: { id: number; customer_code: string | null; name: string }[]
  warehouses: { id: number; code: string; name: string }[]
  users: { id: number; email: string }[]
  tax_rates: { id: number; code: string; name: string; rate_percent: string }[]
  payment_methods: { id: number; code: string; name: string }[]
}

export type SaleOrderPayload = {
  order_number_override?: string | null
  customer_id?: number | null
  order_date?: string | null
  order_type?: SaleOrderType
  sales_channel?: SaleChannel | null
  order_source?: SaleOrderSource | null
  priority?: OrderPriority
  salesperson_id?: number | null
  currency_code?: string | null
  price_list_code?: string | null
  pricing_procedure?: string | null
  payment_terms?: string | null
  payment_due_date?: string | null
  payment_method_id?: number | null
  header_discount_amount?: string
  freight_amount?: string
  insurance_amount?: string
  handling_amount?: string
  warehouse_id?: number | null
  shipping_point_id?: number | null
  partial_delivery_allowed?: boolean
  complete_delivery_required?: boolean
  planned_ship_date?: string | null
  requested_delivery_date?: string | null
  shipping_method?: string | null
  shipping_conditions?: string | null
  transportation_group?: string | null
  loading_group?: string | null
  incoterms?: string | null
  incoterms_location?: string | null
  delivery_block?: string | null
  sales_organization?: string | null
  distribution_channel?: string | null
  division?: string | null
  sales_office?: string | null
  sales_group?: string | null
  customer_po_number?: string | null
  customer_po_date?: string | null
  opportunity_id?: number | null
  campaign_id?: string | null
  price_group?: string | null
  header_text?: string | null
  approval_status?: string | null
  customer_snapshot?: CustomerSnapshot | null
  pricing_conditions?: Record<string, unknown> | null
  delivery_logistics?: Record<string, unknown> | null
  billing_financial?: Record<string, unknown> | null
  terms_compliance?: Record<string, unknown> | null
  references?: Record<string, unknown> | null
  workflow_approval?: Record<string, unknown> | null
  attachments?: { filename: string; url?: string | null; content_type?: string | null }[] | null
  partners?: SalePartnerInput[] | null
  items: SaleItemLine[]
  confirm?: boolean
}

export type SaleCheckoutPayload = {
  customer_id?: number | null
  items: { product_id: number; quantity: number }[]
  confirm?: boolean
}

export type PosProduct = {
  id: number
  sku: string
  name: string
  barcode: string | null
  price: string
  stock: number
  low_stock_threshold: number
}

export type PosProductListResponse = {
  items: PosProduct[]
  total: number
}

/** @deprecated Use SaleOrder */
export type Sale = SaleOrder
