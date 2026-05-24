import { api } from "@/lib/api"
import type {
  CrmActivity,
  CrmLead,
  CrmLeadListResponse,
  CrmOpportunity,
  CrmOpportunityListResponse,
  CustomerContact,
  PipelineSummary,
} from "@/types/crm"

export async function fetchPipelineSummary() {
  const { data } = await api.get<PipelineSummary>("/v1/crm/pipeline/summary")
  return data
}

export async function fetchLeads(params?: { search?: string; status?: string }) {
  const { data } = await api.get<CrmLeadListResponse>("/v1/crm/leads", { params })
  return data
}

export async function createLead(body: Record<string, unknown>) {
  const { data } = await api.post<CrmLead>("/v1/crm/leads", body)
  return data
}

export async function updateLead(id: number, body: Record<string, unknown>) {
  const { data } = await api.patch<CrmLead>(`/v1/crm/leads/${id}`, body)
  return data
}

export async function deleteLead(id: number) {
  await api.delete(`/v1/crm/leads/${id}`)
}

export async function fetchOpportunities(params?: {
  customer_id?: number
  stage?: string
  search?: string
}) {
  const { data } = await api.get<CrmOpportunityListResponse>("/v1/crm/opportunities", { params })
  return data
}

export async function createOpportunity(body: Record<string, unknown>) {
  const { data } = await api.post<CrmOpportunity>("/v1/crm/opportunities", body)
  return data
}

export async function updateOpportunity(id: number, body: Record<string, unknown>) {
  const { data } = await api.patch<CrmOpportunity>(`/v1/crm/opportunities/${id}`, body)
  return data
}

export async function deleteOpportunity(id: number) {
  await api.delete(`/v1/crm/opportunities/${id}`)
}

export async function fetchCrmContacts(params?: { search?: string }) {
  const { data } = await api.get<CustomerContact[]>("/v1/crm/contacts", { params })
  return data
}

export async function createCustomerContact(customerId: number, body: Record<string, unknown>) {
  const { data } = await api.post<CustomerContact>(`/v1/customers/${customerId}/contacts`, body)
  return data
}

export async function updateCustomerContact(
  customerId: number,
  contactId: number,
  body: Record<string, unknown>,
) {
  const { data } = await api.patch<CustomerContact>(
    `/v1/customers/${customerId}/contacts/${contactId}`,
    body,
  )
  return data
}

export async function deleteCustomerContact(customerId: number, contactId: number) {
  await api.delete(`/v1/customers/${customerId}/contacts/${contactId}`)
}

export async function fetchCustomerContacts(customerId: number) {
  const { data } = await api.get<CustomerContact[]>(`/v1/customers/${customerId}/contacts`)
  return data
}

export async function createCustomerActivity(customerId: number, body: Record<string, unknown>) {
  const { data } = await api.post<CrmActivity>(`/v1/customers/${customerId}/activities`, body)
  return data
}

export async function updateCustomerActivity(
  customerId: number,
  activityId: number,
  body: Record<string, unknown>,
) {
  const { data } = await api.patch<CrmActivity>(
    `/v1/customers/${customerId}/activities/${activityId}`,
    body,
  )
  return data
}

export async function deleteCustomerActivity(customerId: number, activityId: number) {
  await api.delete(`/v1/customers/${customerId}/activities/${activityId}`)
}
