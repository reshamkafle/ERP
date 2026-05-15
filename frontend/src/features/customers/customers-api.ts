import { api } from "@/lib/api"
import type { Customer, CustomerDetail, CustomerListResponse } from "@/types/customer"
import type { CustomerFormValues } from "@/lib/customer-schema"

function buildPayload(values: CustomerFormValues) {
  return {
    name: values.name,
    phone: values.phone?.trim() || null,
    email: values.email?.trim() || null,
    notes: values.notes?.trim() || null,
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
  const { data } = await api.post<Customer>("/v1/customers", buildPayload(values))
  return data
}

export async function updateCustomer(id: number, values: CustomerFormValues) {
  const { data } = await api.patch<Customer>(`/v1/customers/${id}`, buildPayload(values))
  return data
}

export async function deleteCustomer(id: number) {
  await api.delete(`/v1/customers/${id}`)
}
