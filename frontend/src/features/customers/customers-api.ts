import { api } from "@/lib/api"
import {
  customerFormToPayload,
  defaultCustomerFormValues,
  defaultExtendedData,
  type CustomerFormValues,
} from "@/lib/customer-schema"
import type {
  ChartOfAccountOption,
  Customer,
  CustomerAuditLogEntry,
  CustomerDetail,
  CustomerListResponse,
  CustomerOverview,
} from "@/types/customer"
import type { CrmActivity, CustomerContact, CrmOpportunityListResponse } from "@/types/crm"

export function customerToForm(customer: Customer): CustomerFormValues {
  const ext = customer.extended_data
  return {
    name: customer.name,
    customer_code: customer.customer_code ?? "",
    legal_name: customer.legal_name ?? "",
    trade_name: customer.trade_name ?? "",
    search_terms: customer.search_terms ?? "",
    status: customer.status ?? "",
    customer_type: customer.customer_type ?? "",
    parent_customer_id: customer.parent_customer_id ? String(customer.parent_customer_id) : "",
    phone: customer.phone ?? "",
    mobile_phone: customer.mobile_phone ?? "",
    fax: customer.fax ?? "",
    email: customer.email ?? "",
    timezone: customer.timezone ?? "",
    language: customer.language ?? "",
    latitude: customer.latitude != null ? String(customer.latitude) : "",
    longitude: customer.longitude != null ? String(customer.longitude) : "",
    segment: customer.segment ?? "",
    customer_group: customer.customer_group ?? "",
    industry: customer.industry ?? "",
    company_size: customer.company_size ?? "",
    annual_revenue: customer.annual_revenue ?? "",
    website: customer.website ?? "",
    contact_name: customer.contact_name ?? "",
    contact_phone: customer.contact_phone ?? "",
    contact_email: customer.contact_email ?? "",
    billing_address_line1: customer.billing_address_line1 ?? "",
    billing_address_line2: customer.billing_address_line2 ?? "",
    billing_city: customer.billing_city ?? "",
    billing_state: customer.billing_state ?? "",
    billing_postal_code: customer.billing_postal_code ?? "",
    billing_country: customer.billing_country ?? "",
    shipping_address_line1: customer.shipping_address_line1 ?? "",
    shipping_address_line2: customer.shipping_address_line2 ?? "",
    shipping_city: customer.shipping_city ?? "",
    shipping_state: customer.shipping_state ?? "",
    shipping_postal_code: customer.shipping_postal_code ?? "",
    shipping_country: customer.shipping_country ?? "",
    credit_limit: customer.credit_limit ?? "",
    credit_status: customer.credit_status ?? "",
    payment_terms: customer.payment_terms ?? "",
    reconciliation_account_id: customer.reconciliation_account_id
      ? String(customer.reconciliation_account_id)
      : "",
    tax_id: customer.tax_id ?? "",
    tax_registration_type: customer.tax_registration_type ?? "",
    tax_classification: customer.tax_classification ?? "",
    tax_exempt: customer.tax_exempt ?? false,
    gst_number: customer.gst_number ?? "",
    vat_number: customer.vat_number ?? "",
    billing_preference: customer.billing_preference ?? "",
    bank_details: {
      bank_name: customer.bank_details?.bank_name ?? "",
      account_number: customer.bank_details?.account_number ?? "",
      iban: customer.bank_details?.iban ?? "",
      swift: customer.bank_details?.swift ?? "",
    },
    dunning_procedure: customer.dunning_procedure ?? "",
    withholding_tax: customer.withholding_tax ?? "",
    incoterms: customer.incoterms ?? "",
    currency_code: customer.currency_code,
    sales_rep: customer.sales_rep ?? "",
    price_group: customer.price_group ?? "",
    shipping_conditions: customer.shipping_conditions ?? "",
    delivering_plant: customer.delivering_plant ?? "",
    order_probability: customer.order_probability ?? "",
    lead_source: customer.lead_source ?? "",
    year_founded: customer.year_founded != null ? String(customer.year_founded) : "",
    ownership_type: customer.ownership_type ?? "",
    territory: customer.territory ?? "",
    employee_count: customer.employee_count != null ? String(customer.employee_count) : "",
    account_owner_id: customer.account_owner_id ? String(customer.account_owner_id) : "",
    shipping_preference: customer.shipping_preference ?? "",
    preferred_carrier: customer.preferred_carrier ?? "",
    receiving_hours: customer.receiving_hours ?? "",
    freight_terms: customer.freight_terms ?? "",
    transport_zone: customer.transport_zone ?? "",
    extended_data: ext
      ? {
          integration_ids: {
            crm_id: ext.integration_ids?.crm_id ?? "",
            ecommerce_id: ext.integration_ids?.ecommerce_id ?? "",
            legacy_id: ext.integration_ids?.legacy_id ?? "",
          },
          consent_flags: {
            marketing: ext.consent_flags?.marketing ?? false,
            gdpr: ext.consent_flags?.gdpr ?? false,
            ccpa: ext.consent_flags?.ccpa ?? false,
          },
          custom_fields: ext.custom_fields?.map((f) => ({
            key: f.key,
            value: f.value ?? "",
          })) ?? [],
          risk_rating: ext.risk_rating ?? "",
          loyalty: {
            tier: ext.loyalty?.tier ?? "",
            points: ext.loyalty?.points != null ? String(ext.loyalty.points) : "",
          },
          marketing: {
            journey_stage: ext.marketing?.journey_stage ?? "",
            last_marketing_touch: ext.marketing?.last_marketing_touch ?? "",
            campaign_membership: ext.marketing?.campaign_membership ?? "",
            email_opt_in: ext.marketing?.email_opt_in ?? false,
            marketing_source: ext.marketing?.marketing_source ?? "",
          },
          analytics: {
            churn_risk_score:
              ext.analytics?.churn_risk_score != null ? String(ext.analytics.churn_risk_score) : "",
            behavior_tags: ext.analytics?.behavior_tags?.join(", ") ?? "",
            labels: ext.analytics?.labels?.join(", ") ?? "",
          },
          service: {
            contract_number: ext.service?.contract_number ?? "",
            sla_tier: ext.service?.sla_tier ?? "",
            last_csat: ext.service?.last_csat != null ? String(ext.service.last_csat) : "",
            last_nps: ext.service?.last_nps != null ? String(ext.service.last_nps) : "",
            last_service_date: ext.service?.last_service_date ?? "",
            warranty_info: ext.service?.warranty_info ?? "",
            installed_base: ext.service?.installed_base ?? "",
          },
        }
      : defaultExtendedData,
    notes: customer.notes ?? "",
    contacts:
      customer.contacts?.map((c) => ({
        contact_code: c.contact_code ?? "",
        salutation: c.salutation ?? "",
        first_name: c.first_name ?? "",
        middle_name: c.middle_name ?? "",
        last_name: c.last_name ?? "",
        name: c.name,
        email: c.email ?? "",
        email_secondary: c.email_secondary ?? "",
        phone: c.phone ?? "",
        phone_secondary: c.phone_secondary ?? "",
        title: c.title ?? "",
        department: c.department ?? "",
        role: c.role ?? "",
        is_primary: c.is_primary ?? false,
        preferred_language: c.preferred_language ?? "",
        linkedin_url: c.linkedin_url ?? "",
        birthday: c.birthday ?? "",
        anniversary: c.anniversary ?? "",
        notes: c.notes ?? "",
      })) ?? [],
    addresses:
      customer.addresses?.map((a) => ({
        address_type: a.address_type,
        label: a.label ?? "",
        line1: a.line1 ?? "",
        line2: a.line2 ?? "",
        house_no: a.house_no ?? "",
        city: a.city ?? "",
        state: a.state ?? "",
        postal_code: a.postal_code ?? "",
        country: a.country ?? "",
        latitude: a.latitude != null ? String(a.latitude) : "",
        longitude: a.longitude != null ? String(a.longitude) : "",
        is_default: a.is_default ?? false,
      })) ?? [],
    sales_areas:
      customer.sales_areas?.map((s) => ({
        sales_org: s.sales_org,
        distribution_channel: s.distribution_channel ?? "",
        division: s.division ?? "",
        credit_limit: s.credit_limit ?? "",
        payment_terms: s.payment_terms ?? "",
        pricing_procedure: s.pricing_procedure ?? "",
      })) ?? [],
  }
}

export async function fetchCustomers(params: {
  search?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<CustomerListResponse>("/v1/customers", { params })
  return data
}

export async function fetchCustomer(id: number) {
  const { data } = await api.get<CustomerDetail>(`/v1/customers/${id}`)
  return data
}

export async function createCustomer(values: CustomerFormValues) {
  const { data } = await api.post<Customer>("/v1/customers", customerFormToPayload(values))
  return data
}

export async function updateCustomer(id: number, values: CustomerFormValues) {
  const { data } = await api.patch<Customer>(`/v1/customers/${id}`, customerFormToPayload(values))
  return data
}

export async function deleteCustomer(id: number) {
  await api.delete(`/v1/customers/${id}`)
}

export async function fetchCustomerOverview(id: number) {
  const { data } = await api.get<CustomerOverview>(`/v1/customers/${id}/overview`)
  return data
}

export async function fetchCustomerContacts(customerId: number) {
  const { data } = await api.get<CustomerContact[]>(`/v1/customers/${customerId}/contacts`)
  return data
}

export async function fetchCustomerActivities(customerId: number) {
  const { data } = await api.get<CrmActivity[]>(`/v1/customers/${customerId}/activities`)
  return data
}

export async function fetchCustomerOpportunities(customerId: number) {
  const { data } = await api.get<CrmOpportunityListResponse>(
    `/v1/customers/${customerId}/opportunities`,
  )
  return data
}

export async function fetchCustomerAuditLog(customerId: number) {
  const { data } = await api.get<CustomerAuditLogEntry[]>(
    `/v1/customers/${customerId}/audit-log`,
  )
  return data
}

export async function fetchCustomerDocuments(customerId: number) {
  const { data } = await api.get<{ items: { id: number; document_number: string; title: string; document_type: string; status: string }[]; total: number }>(
    `/v1/customers/${customerId}/documents`,
  )
  return data
}

export async function fetchChartOfAccounts(): Promise<ChartOfAccountOption[]> {
  const { data } = await api.get<{ items?: ChartOfAccountOption[] } | ChartOfAccountOption[]>(
    "/v1/chart-of-accounts",
  )
  if (Array.isArray(data)) return data
  return data.items ?? []
}

export function customerToSnapshotFields(customer: Customer) {
  return {
    customer_code: customer.customer_code ?? "",
    name: customer.name,
    contact_name: customer.contact_name ?? "",
    contact_phone: customer.contact_phone ?? customer.phone ?? "",
    contact_email: customer.contact_email ?? customer.email ?? "",
    customer_group: customer.customer_group ?? "",
    credit_limit: customer.credit_limit ?? "",
    credit_status: customer.credit_status ?? "",
    payment_terms: customer.payment_terms ?? "",
    tax_id: customer.tax_id ?? "",
    shipping_preference: customer.shipping_preference ?? "",
    incoterms: customer.incoterms ?? "",
    trade_name: customer.trade_name ?? "",
    status: customer.status ?? "",
    gst_number: customer.gst_number ?? "",
    vat_number: customer.vat_number ?? "",
    currency_code: customer.currency_code,
    billing_address: {
      line1: customer.billing_address_line1 ?? "",
      line2: customer.billing_address_line2 ?? "",
      city: customer.billing_city ?? "",
      state: customer.billing_state ?? "",
      postal_code: customer.billing_postal_code ?? "",
      country: customer.billing_country ?? "",
    },
    shipping_address: {
      line1: customer.shipping_address_line1 ?? "",
      line2: customer.shipping_address_line2 ?? "",
      city: customer.shipping_city ?? "",
      state: customer.shipping_state ?? "",
      postal_code: customer.shipping_postal_code ?? "",
      country: customer.shipping_country ?? "",
    },
  }
}

export { defaultCustomerFormValues, customerFormToPayload }
