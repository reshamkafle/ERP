import type { SaleOrderFormValues } from "@/lib/sale-order-schema"
import type { SaleOrder, SaleOrderPayload, SalePartnerInput } from "@/types/sale"

function numOrUndefined(v: string | undefined | null): string | undefined {
  if (v === undefined || v === null || v === "") return undefined
  return v
}

function emptyToNull<T extends Record<string, unknown>>(obj: T | undefined): T | null {
  if (!obj) return null
  const cleaned = Object.fromEntries(
    Object.entries(obj).filter(([, val]) => {
      if (val === "" || val === null || val === undefined) return false
      if (typeof val === "object" && val !== null && !Array.isArray(val)) {
        const nested = emptyToNull(val as Record<string, unknown>)
        return nested !== null
      }
      return true
    }),
  )
  for (const [key, val] of Object.entries(cleaned)) {
    if (typeof val === "object" && val !== null && !Array.isArray(val)) {
      const nested = emptyToNull(val as Record<string, unknown>)
      if (nested === null) delete cleaned[key]
      else cleaned[key] = nested
    }
  }
  return Object.keys(cleaned).length ? (cleaned as T) : null
}

function buildPartners(values: SaleOrderFormValues): SalePartnerInput[] | undefined {
  const rows = values.partners?.filter(
    (p) => p.customer_id || p.user_id || p.supplier_id || p.name_override,
  )
  return rows?.length ? rows : undefined
}

function buildAttachments(values: SaleOrderFormValues) {
  const rows = values.attachments?.filter((a) => a.filename?.trim())
  return rows?.length ? rows : undefined
}

export function formValuesToPayload(values: SaleOrderFormValues, confirm = false): SaleOrderPayload {
  const snap = values.customer_snapshot
  const billing = snap?.billing_address
  const shipping = snap?.shipping_address
  const refs = {
    ...(values.references ?? {}),
    customer_po_number: values.customer_po_number || undefined,
    customer_po_date: values.customer_po_date || undefined,
  }
  return {
    order_number_override: values.order_number_override?.trim() || undefined,
    customer_id: values.customer_id ?? null,
    order_date: values.order_date || undefined,
    order_type: values.order_type,
    sales_channel: (values.sales_channel as SaleOrderPayload["sales_channel"]) || null,
    order_source: (values.order_source as SaleOrderPayload["order_source"]) || null,
    priority: values.priority,
    salesperson_id: values.salesperson_id ?? null,
    currency_code: values.currency_code,
    price_list_code: values.price_list_code || null,
    pricing_procedure: values.pricing_procedure || null,
    payment_terms: values.payment_terms || snap?.payment_terms || null,
    payment_due_date: values.payment_due_date || null,
    payment_method_id: values.payment_method_id ?? null,
    header_discount_amount: numOrUndefined(values.header_discount_amount),
    freight_amount: numOrUndefined(values.freight_amount),
    insurance_amount: numOrUndefined(values.insurance_amount),
    handling_amount: numOrUndefined(values.handling_amount),
    warehouse_id: values.warehouse_id ?? null,
    shipping_point_id: values.shipping_point_id ?? null,
    partial_delivery_allowed: values.partial_delivery_allowed,
    complete_delivery_required: values.complete_delivery_required,
    planned_ship_date: values.planned_ship_date || null,
    requested_delivery_date: values.requested_delivery_date || null,
    shipping_method: values.shipping_method || null,
    shipping_conditions: values.shipping_conditions || null,
    transportation_group: values.transportation_group || null,
    loading_group: values.loading_group || null,
    incoterms: values.incoterms || snap?.incoterms || null,
    incoterms_location: values.incoterms_location || null,
    delivery_block: values.delivery_block || null,
    sales_organization: values.sales_organization || null,
    distribution_channel: values.distribution_channel || null,
    division: values.division || null,
    sales_office: values.sales_office || null,
    sales_group: values.sales_group || null,
    customer_po_number: values.customer_po_number || null,
    customer_po_date: values.customer_po_date || null,
    opportunity_id: values.opportunity_id ?? null,
    campaign_id: values.campaign_id || null,
    price_group: values.price_group || null,
    header_text: values.header_text || null,
    approval_status: values.approval_status || null,
    customer_snapshot: snap
      ? {
          customer_id: values.customer_id ?? undefined,
          customer_code: snap.customer_code,
          name: snap.name,
          contact_name: snap.contact_name,
          contact_phone: snap.contact_phone,
          contact_email: snap.contact_email,
          customer_group: snap.customer_group,
          credit_limit: snap.credit_limit,
          credit_status: snap.credit_status,
          payment_terms: snap.payment_terms,
          tax_id: snap.tax_id,
          gst_number: snap.gst_number,
          vat_number: snap.vat_number,
          shipping_preference: snap.shipping_preference,
          incoterms: snap.incoterms,
          billing_address: emptyToNull(billing ?? undefined) ?? undefined,
          shipping_address: emptyToNull(shipping ?? undefined) ?? undefined,
        }
      : null,
    pricing_conditions: emptyToNull(values.pricing_conditions ?? undefined),
    delivery_logistics: emptyToNull(values.delivery_logistics ?? undefined),
    billing_financial: emptyToNull(values.billing_financial ?? undefined),
    terms_compliance: emptyToNull(values.terms_compliance ?? undefined),
    references: emptyToNull(refs),
    workflow_approval: emptyToNull(values.workflow_approval ?? undefined),
    attachments: buildAttachments(values) ?? null,
    partners: buildPartners(values),
    items: values.items
      .filter((line) => line.product_id > 0)
      .map((line) => ({
        product_id: line.product_id,
        quantity: line.quantity,
        unit_price: line.unit_price || undefined,
        description: line.description,
        uom: line.uom,
        alternate_uom: line.alternate_uom,
        uom_conversion_factor: line.uom_conversion_factor,
        discount_percent: line.discount_percent,
        discount_amount: line.discount_amount,
        tax_code: line.tax_code,
        tax_rate_id: line.tax_rate_id ?? undefined,
        requested_delivery_date: line.requested_delivery_date,
        confirmed_delivery_date: line.confirmed_delivery_date,
        product_category: line.product_category,
        item_category: line.item_category,
        gross_price: line.gross_price,
        warehouse_id: line.warehouse_id ?? undefined,
        storage_location_id: line.storage_location_id ?? undefined,
        batch_number: line.batch_number,
        serial_number: line.serial_number,
        delivery_block: line.delivery_block,
        billing_block: line.billing_block,
        rejection_reason: line.rejection_reason,
        net_weight: line.net_weight,
        gross_weight: line.gross_weight,
        volume: line.volume,
        substitute_product_id: line.substitute_product_id ?? undefined,
        line_text: line.line_text,
        line_status: (line.line_status as SaleOrderPayload["items"][0]["line_status"]) || undefined,
      })),
    confirm,
  }
}

function strRecord(obj: Record<string, unknown> | undefined | null): Record<string, string> {
  if (!obj) return {}
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [k, v == null ? "" : String(v)]),
  )
}

function boolRecord(obj: Record<string, unknown> | undefined | null, key: string): boolean {
  if (!obj) return false
  return Boolean(obj[key])
}

export function saleToFormValues(sale: SaleOrder): SaleOrderFormValues {
  const snap = (sale.customer_snapshot ?? {}) as SaleOrderFormValues["customer_snapshot"]
  const refs = strRecord(sale.references as Record<string, unknown>)
  const pricing = strRecord(sale.pricing_conditions as Record<string, unknown>)
  const delivery = strRecord(sale.delivery_logistics as Record<string, unknown>)
  const billing = strRecord(sale.billing_financial as Record<string, unknown>)
  const terms = strRecord(sale.terms_compliance as Record<string, unknown>)
  const shipOverride = (sale.delivery_logistics as { ship_to_override?: Record<string, string> })
    ?.ship_to_override

  return {
    order_number_override: "",
    customer_id: sale.customer_id,
    order_date: sale.order_date,
    order_type: sale.order_type,
    sales_channel: sale.sales_channel ?? "",
    order_source: sale.order_source ?? "",
    priority: sale.priority,
    salesperson_id: sale.salesperson_id,
    currency_code: sale.currency_code,
    price_list_code: sale.price_list_code ?? "",
    pricing_procedure: sale.pricing_procedure ?? "",
    payment_terms: sale.payment_terms ?? "",
    payment_due_date: sale.payment_due_date ?? "",
    payment_method_id: sale.payment_method_id,
    header_discount_amount: sale.header_discount_amount,
    freight_amount: sale.freight_amount,
    insurance_amount: sale.insurance_amount,
    handling_amount: sale.handling_amount,
    warehouse_id: sale.warehouse_id,
    shipping_point_id: sale.shipping_point_id,
    partial_delivery_allowed: sale.partial_delivery_allowed,
    complete_delivery_required: sale.complete_delivery_required ?? false,
    planned_ship_date: sale.planned_ship_date ?? "",
    requested_delivery_date: sale.requested_delivery_date ?? "",
    shipping_method: sale.shipping_method ?? "",
    shipping_conditions: sale.shipping_conditions ?? "",
    transportation_group: sale.transportation_group ?? "",
    loading_group: sale.loading_group ?? "",
    incoterms: sale.incoterms ?? "",
    incoterms_location: sale.incoterms_location ?? "",
    delivery_block: sale.delivery_block ?? "",
    sales_organization: sale.sales_organization ?? "",
    distribution_channel: sale.distribution_channel ?? "",
    division: sale.division ?? "",
    sales_office: sale.sales_office ?? "",
    sales_group: sale.sales_group ?? "",
    customer_po_number: sale.customer_po_number ?? refs.customer_po_number ?? "",
    customer_po_date: sale.customer_po_date ?? refs.customer_po_date ?? "",
    opportunity_id: sale.opportunity_id,
    campaign_id: sale.campaign_id ?? "",
    price_group: sale.price_group ?? "",
    header_text: sale.header_text ?? "",
    approval_status: sale.approval_status ?? "",
    order_status: sale.order_status,
    credit_check_status: sale.credit_check_status,
    atp_check_status: sale.atp_check_status,
    delivery_status: sale.delivery_status ?? "",
    invoice_status: sale.invoice_status ?? "",
    payment_status: sale.payment_status,
    partners:
      sale.partners?.map((p) => ({
        role: p.role,
        customer_id: p.customer_id,
        supplier_id: p.supplier_id,
        user_id: p.user_id,
        name_override: p.name_override ?? "",
      })) ?? [],
    workflow_approval: {},
    attachments:
      sale.attachments?.map((a) => ({
        filename: String((a as { filename?: string }).filename ?? ""),
        url: String((a as { url?: string }).url ?? ""),
        content_type: String((a as { content_type?: string }).content_type ?? ""),
      })) ?? [],
    customer_snapshot: {
      customer_code: snap?.customer_code ?? "",
      name: snap?.name ?? sale.customer_name ?? "",
      contact_name: snap?.contact_name ?? "",
      contact_phone: snap?.contact_phone ?? "",
      contact_email: snap?.contact_email ?? "",
      customer_group: snap?.customer_group ?? "",
      credit_limit: String(snap?.credit_limit ?? ""),
      credit_status: snap?.credit_status ?? "",
      payment_terms: snap?.payment_terms ?? "",
      tax_id: snap?.tax_id ?? "",
      gst_number: (snap as { gst_number?: string })?.gst_number ?? "",
      vat_number: (snap as { vat_number?: string })?.vat_number ?? "",
      shipping_preference: snap?.shipping_preference ?? "",
      incoterms: snap?.incoterms ?? "",
      billing_address: (snap?.billing_address as Record<string, string>) ?? {},
      shipping_address: (snap?.shipping_address as Record<string, string>) ?? {},
    },
    pricing_conditions: {
      contract_ref: pricing.contract_ref ?? "",
      special_pricing_agreement: pricing.special_pricing_agreement ?? "",
      line_discount_notes: pricing.line_discount_notes ?? "",
      total_before_tax: pricing.total_before_tax ?? "",
      total_after_tax: pricing.total_after_tax ?? "",
      pricing_date: pricing.pricing_date ?? "",
      manual_price_override_reason: pricing.manual_price_override_reason ?? "",
      list_price_notes: pricing.list_price_notes ?? "",
    },
    delivery_logistics: {
      delivery_number: delivery.delivery_number ?? "",
      carrier_name: delivery.carrier_name ?? "",
      tracking_number: delivery.tracking_number ?? "",
      transport_mode: delivery.transport_mode ?? "",
      route: delivery.route ?? "",
      bill_of_lading: delivery.bill_of_lading ?? "",
      promised_date: delivery.promised_date ?? "",
      actual_date: delivery.actual_date ?? "",
      expected_shipment_date: delivery.expected_shipment_date ?? "",
      warehouse_assignment: delivery.warehouse_assignment ?? "",
      shipping_instructions: delivery.shipping_instructions ?? "",
      packaging_details: delivery.packaging_details ?? "",
      ship_to_override: shipOverride ?? {
        line1: "",
        line2: "",
        city: "",
        state: "",
        postal_code: "",
        country: "",
      },
    },
    billing_financial: {
      invoice_number: billing.invoice_number ?? "",
      invoice_date: billing.invoice_date ?? "",
      billing_type: billing.billing_type ?? "",
      billing_block: billing.billing_block ?? "",
      split_billing: boolRecord(sale.billing_financial as Record<string, unknown>, "split_billing"),
      taxable_amount: billing.taxable_amount ?? "",
      tax_amount: billing.tax_amount ?? "",
      total_amount: billing.total_amount ?? "",
      accounting_document_number: billing.accounting_document_number ?? "",
      cost_center: billing.cost_center ?? "",
      profit_center: billing.profit_center ?? "",
      project_code: billing.project_code ?? "",
      wbs_element: billing.wbs_element ?? "",
      payment_method_label: billing.payment_method_label ?? "",
      payment_receipt_number: billing.payment_receipt_number ?? "",
      amount_received: billing.amount_received ?? "",
      outstanding_amount: billing.outstanding_amount ?? "",
      credit_debit_note_ref: billing.credit_debit_note_ref ?? "",
      bank_details: billing.bank_details ?? "",
      card_last_four: billing.card_last_four ?? "",
    },
    terms_compliance: {
      warranty_terms: terms.warranty_terms ?? "",
      return_policy_ref: terms.return_policy_ref ?? "",
      inspection_requirements: terms.inspection_requirements ?? "",
      regulatory_compliance: terms.regulatory_compliance ?? "",
      order_validity_date: terms.order_validity_date ?? "",
      order_expiry_date: terms.order_expiry_date ?? "",
      export_license: terms.export_license ?? "",
      hazardous_material_info: terms.hazardous_material_info ?? "",
      sustainability_data: terms.sustainability_data ?? "",
    },
    references: {
      quotation_number: refs.quotation_number ?? "",
      contract_number: refs.contract_number ?? "",
      tender_number: refs.tender_number ?? "",
      internal_order_number: refs.internal_order_number ?? "",
      remarks: refs.remarks ?? "",
      internal_notes: refs.internal_notes ?? "",
      reason_code: refs.reason_code ?? "",
      order_reason: refs.order_reason ?? "",
      attachments_note: refs.attachments_note ?? "",
      atp_check_notes: refs.atp_check_notes ?? "",
      crm_opportunity_link: refs.crm_opportunity_link ?? "",
      forecast_vs_actual: refs.forecast_vs_actual ?? "",
      forecast_category: refs.forecast_category ?? "",
      closing_probability: refs.closing_probability ?? "",
      expected_revenue: refs.expected_revenue ?? "",
      lead_source: refs.lead_source ?? "",
      order_confirmation_date: refs.order_confirmation_date ?? "",
      returns_cancellation_reason: refs.returns_cancellation_reason ?? "",
      fulfillment_lead_time_days: refs.fulfillment_lead_time_days ?? "",
      profitability_analysis: refs.profitability_analysis ?? "",
    },
    items: sale.items.map((item) => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price,
      description: item.description ?? "",
      uom: item.uom ?? "",
      alternate_uom: item.alternate_uom ?? "",
      uom_conversion_factor: item.uom_conversion_factor ?? "",
      discount_percent: item.discount_percent,
      discount_amount: item.discount_amount,
      tax_code: item.tax_code ?? "",
      tax_rate_id: item.tax_rate_id,
      requested_delivery_date: item.requested_delivery_date ?? "",
      confirmed_delivery_date: item.confirmed_delivery_date ?? "",
      product_category: item.product_category ?? "",
      item_category: item.item_category ?? "",
      gross_price: item.gross_price ?? "",
      warehouse_id: item.warehouse_id,
      storage_location_id: item.storage_location_id,
      batch_number: item.batch_number ?? "",
      serial_number: item.serial_number ?? "",
      delivery_block: item.delivery_block ?? "",
      billing_block: item.billing_block ?? "",
      rejection_reason: item.rejection_reason ?? "",
      net_weight: item.net_weight ?? "",
      gross_weight: item.gross_weight ?? "",
      volume: item.volume ?? "",
      line_text: item.line_text ?? "",
      line_status: item.line_status ?? "",
      substitute_product_id: item.substitute_product_id,
    })),
    confirm: false,
  }
}
