import { z } from "zod"

const addressSchema = z.object({
  line1: z.string().optional(),
  line2: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  postal_code: z.string().optional(),
  country: z.string().optional(),
})

const partnerSchema = z.object({
  role: z.enum([
    "SOLD_TO",
    "SHIP_TO",
    "BILL_TO",
    "PAYER",
    "FORWARDING_AGENT",
    "SALES_EMPLOYEE",
  ]),
  customer_id: z.coerce.number().optional().nullable(),
  supplier_id: z.coerce.number().optional().nullable(),
  user_id: z.coerce.number().optional().nullable(),
  name_override: z.string().optional(),
})

const attachmentSchema = z.object({
  filename: z.string().min(1),
  url: z.string().optional(),
  content_type: z.string().optional(),
})

export const saleItemLineSchema = z.object({
  product_id: z.coerce.number().int(),
  quantity: z.coerce.number().int().min(1),
  unit_price: z.string().optional(),
  description: z.string().optional(),
  uom: z.string().optional(),
  alternate_uom: z.string().optional(),
  uom_conversion_factor: z.string().optional(),
  discount_percent: z.string().optional(),
  discount_amount: z.string().optional(),
  tax_code: z.string().optional(),
  tax_rate_id: z.coerce.number().optional().nullable(),
  requested_delivery_date: z.string().optional(),
  confirmed_delivery_date: z.string().optional(),
  product_category: z.string().optional(),
  item_category: z.string().optional(),
  gross_price: z.string().optional(),
  warehouse_id: z.coerce.number().optional().nullable(),
  storage_location_id: z.coerce.number().optional().nullable(),
  batch_number: z.string().optional(),
  serial_number: z.string().optional(),
  delivery_block: z.string().optional(),
  billing_block: z.string().optional(),
  rejection_reason: z.string().optional(),
  net_weight: z.string().optional(),
  gross_weight: z.string().optional(),
  volume: z.string().optional(),
  substitute_product_id: z.coerce.number().optional().nullable(),
  line_text: z.string().optional(),
  line_status: z.string().optional(),
})

const pricingConditionsSchema = z.object({
  contract_ref: z.string().optional(),
  special_pricing_agreement: z.string().optional(),
  line_discount_notes: z.string().optional(),
  total_before_tax: z.string().optional(),
  total_after_tax: z.string().optional(),
  pricing_date: z.string().optional(),
  manual_price_override_reason: z.string().optional(),
  list_price_notes: z.string().optional(),
})

const deliveryLogisticsSchema = z.object({
  delivery_number: z.string().optional(),
  carrier_name: z.string().optional(),
  tracking_number: z.string().optional(),
  transport_mode: z.string().optional(),
  route: z.string().optional(),
  bill_of_lading: z.string().optional(),
  promised_date: z.string().optional(),
  actual_date: z.string().optional(),
  expected_shipment_date: z.string().optional(),
  warehouse_assignment: z.string().optional(),
  shipping_instructions: z.string().optional(),
  packaging_details: z.string().optional(),
  ship_to_override: addressSchema.optional(),
})

const billingFinancialSchema = z.object({
  invoice_number: z.string().optional(),
  invoice_date: z.string().optional(),
  billing_type: z.string().optional(),
  billing_block: z.string().optional(),
  split_billing: z.boolean().optional(),
  taxable_amount: z.string().optional(),
  tax_amount: z.string().optional(),
  total_amount: z.string().optional(),
  accounting_document_number: z.string().optional(),
  cost_center: z.string().optional(),
  profit_center: z.string().optional(),
  project_code: z.string().optional(),
  wbs_element: z.string().optional(),
  payment_method_label: z.string().optional(),
  payment_receipt_number: z.string().optional(),
  amount_received: z.string().optional(),
  outstanding_amount: z.string().optional(),
  credit_debit_note_ref: z.string().optional(),
  bank_details: z.string().optional(),
  card_last_four: z.string().optional(),
})

const termsComplianceSchema = z.object({
  warranty_terms: z.string().optional(),
  return_policy_ref: z.string().optional(),
  inspection_requirements: z.string().optional(),
  regulatory_compliance: z.string().optional(),
  order_validity_date: z.string().optional(),
  order_expiry_date: z.string().optional(),
  export_license: z.string().optional(),
  hazardous_material_info: z.string().optional(),
  sustainability_data: z.string().optional(),
})

const referencesSchema = z.object({
  quotation_number: z.string().optional(),
  contract_number: z.string().optional(),
  tender_number: z.string().optional(),
  internal_order_number: z.string().optional(),
  remarks: z.string().optional(),
  internal_notes: z.string().optional(),
  reason_code: z.string().optional(),
  order_reason: z.string().optional(),
  attachments_note: z.string().optional(),
  atp_check_notes: z.string().optional(),
  crm_opportunity_link: z.string().optional(),
  forecast_vs_actual: z.string().optional(),
  forecast_category: z.string().optional(),
  closing_probability: z.string().optional(),
  expected_revenue: z.string().optional(),
  lead_source: z.string().optional(),
  order_confirmation_date: z.string().optional(),
  returns_cancellation_reason: z.string().optional(),
  fulfillment_lead_time_days: z.string().optional(),
  profitability_analysis: z.string().optional(),
})

const workflowApprovalSchema = z.object({
  approver_name: z.string().optional(),
  approver_date: z.string().optional(),
  credit_approval_status: z.string().optional(),
  margin_approval_status: z.string().optional(),
  legal_approval_status: z.string().optional(),
  note: z.string().optional(),
})

export const saleOrderFormSchema = z
  .object({
    order_number_override: z.string().optional(),
    customer_id: z.coerce.number().optional().nullable(),
    order_date: z.string().optional(),
    order_type: z.enum(["STANDARD", "RUSH", "SAMPLE", "RETURN", "EXPORT"]).default("STANDARD"),
    sales_channel: z.string().optional(),
    order_source: z.string().optional(),
    priority: z.enum(["HIGH", "MEDIUM", "LOW"]).default("MEDIUM"),
    salesperson_id: z.coerce.number().optional().nullable(),
    currency_code: z.string().max(3).default("USD"),
    price_list_code: z.string().optional(),
    pricing_procedure: z.string().optional(),
    payment_terms: z.string().optional(),
    payment_due_date: z.string().optional(),
    payment_method_id: z.coerce.number().optional().nullable(),
    header_discount_amount: z.string().optional(),
    freight_amount: z.string().optional(),
    insurance_amount: z.string().optional(),
    handling_amount: z.string().optional(),
    warehouse_id: z.coerce.number().optional().nullable(),
    shipping_point_id: z.coerce.number().optional().nullable(),
    partial_delivery_allowed: z.boolean().default(true),
    complete_delivery_required: z.boolean().default(false),
    planned_ship_date: z.string().optional(),
    requested_delivery_date: z.string().optional(),
    shipping_method: z.string().optional(),
    shipping_conditions: z.string().optional(),
    transportation_group: z.string().optional(),
    loading_group: z.string().optional(),
    incoterms: z.string().optional(),
    incoterms_location: z.string().optional(),
    delivery_block: z.string().optional(),
    sales_organization: z.string().optional(),
    distribution_channel: z.string().optional(),
    division: z.string().optional(),
    sales_office: z.string().optional(),
    sales_group: z.string().optional(),
    customer_po_number: z.string().optional(),
    customer_po_date: z.string().optional(),
    opportunity_id: z.coerce.number().optional().nullable(),
    campaign_id: z.string().optional(),
    price_group: z.string().optional(),
    header_text: z.string().optional(),
    approval_status: z.string().optional(),
    order_status: z.string().optional(),
    credit_check_status: z.string().optional(),
    atp_check_status: z.string().optional(),
    delivery_status: z.string().optional(),
    invoice_status: z.string().optional(),
    payment_status: z.string().optional(),
    customer_snapshot: z
      .object({
        customer_code: z.string().optional(),
        name: z.string().optional(),
        contact_name: z.string().optional(),
        contact_phone: z.string().optional(),
        contact_email: z.string().optional(),
        customer_group: z.string().optional(),
        credit_limit: z.string().optional(),
        credit_status: z.string().optional(),
        payment_terms: z.string().optional(),
        tax_id: z.string().optional(),
        gst_number: z.string().optional(),
        vat_number: z.string().optional(),
        shipping_preference: z.string().optional(),
        incoterms: z.string().optional(),
        billing_address: addressSchema.optional(),
        shipping_address: addressSchema.optional(),
      })
      .optional(),
    partners: z.array(partnerSchema).optional(),
    pricing_conditions: pricingConditionsSchema.optional(),
    delivery_logistics: deliveryLogisticsSchema.optional(),
    billing_financial: billingFinancialSchema.optional(),
    terms_compliance: termsComplianceSchema.optional(),
    references: referencesSchema.optional(),
    workflow_approval: workflowApprovalSchema.optional(),
    attachments: z.array(attachmentSchema).optional(),
    items: z.array(saleItemLineSchema).min(1, "Add at least one line item"),
    confirm: z.boolean().optional(),
  })
  .superRefine((data, ctx) => {
    if (!data.customer_id || data.customer_id < 1) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Customer is required for B2B orders",
        path: ["customer_id"],
      })
    }
    if (!data.customer_po_number?.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Customer PO number is required",
        path: ["customer_po_number"],
      })
    }
    if (!data.payment_terms?.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Payment terms are required",
        path: ["payment_terms"],
      })
    }
    if (!data.sales_organization?.trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Sales organization is required",
        path: ["sales_organization"],
      })
    }
    const validLines = data.items.filter((l) => l.product_id > 0)
    if (validLines.length === 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Add at least one line with a product",
        path: ["items"],
      })
    }
    data.items.forEach((line, index) => {
      if (line.product_id > 0) {
        if (!line.unit_price?.trim()) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: "Unit price is required",
            path: ["items", index, "unit_price"],
          })
        }
      }
    })
  })

export type SaleOrderFormValues = z.infer<typeof saleOrderFormSchema>

const emptyAddress = {
  line1: "",
  line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "",
}

export const defaultSaleOrderFormValues: SaleOrderFormValues = {
  order_number_override: "",
  customer_id: null,
  order_date: new Date().toISOString().slice(0, 10),
  order_type: "STANDARD",
  sales_channel: "",
  order_source: "",
  priority: "MEDIUM",
  salesperson_id: null,
  currency_code: "USD",
  price_list_code: "",
  pricing_procedure: "",
  payment_terms: "",
  payment_due_date: "",
  payment_method_id: null,
  header_discount_amount: "0",
  freight_amount: "0",
  insurance_amount: "0",
  handling_amount: "0",
  warehouse_id: null,
  shipping_point_id: null,
  partial_delivery_allowed: true,
  complete_delivery_required: false,
  planned_ship_date: "",
  requested_delivery_date: "",
  shipping_method: "",
  shipping_conditions: "",
  transportation_group: "",
  loading_group: "",
  incoterms: "",
  incoterms_location: "",
  delivery_block: "",
  sales_organization: "",
  distribution_channel: "",
  division: "",
  sales_office: "",
  sales_group: "",
  customer_po_number: "",
  customer_po_date: "",
  opportunity_id: null,
  campaign_id: "",
  price_group: "",
  header_text: "",
  approval_status: "",
  partners: [],
  workflow_approval: {},
  attachments: [],
  customer_snapshot: {
    billing_address: { ...emptyAddress },
    shipping_address: { ...emptyAddress },
  },
  pricing_conditions: {},
  delivery_logistics: {
    ship_to_override: { ...emptyAddress },
  },
  billing_financial: { split_billing: false },
  terms_compliance: {},
  references: {},
  items: [{ product_id: 0, quantity: 1 }],
  confirm: false,
}
