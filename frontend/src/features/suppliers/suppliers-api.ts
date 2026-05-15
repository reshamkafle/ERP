import { api } from "@/lib/api"
import type { SupplierFormValues } from "@/lib/supplier-schema"
import type {
  Supplier,
  SupplierDetail,
  SupplierListResponse,
} from "@/types/supplier"

function buildPayload(values: SupplierFormValues) {
  return {
    name: values.name,
    phone: values.phone?.trim() || null,
    email: values.email?.trim() || null,
    notes: values.notes?.trim() || null,
  }
}

export async function fetchSuppliers(params: {
  search?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<SupplierListResponse>("/v1/suppliers", { params })
  return data
}

export async function fetchSupplier(id: number) {
  const { data } = await api.get<SupplierDetail>(`/v1/suppliers/${id}`)
  return data
}

export async function createSupplier(values: SupplierFormValues) {
  const { data } = await api.post<Supplier>("/v1/suppliers", buildPayload(values))
  return data
}

export async function updateSupplier(id: number, values: SupplierFormValues) {
  const { data } = await api.patch<Supplier>(`/v1/suppliers/${id}`, buildPayload(values))
  return data
}

export async function deleteSupplier(id: number) {
  await api.delete(`/v1/suppliers/${id}`)
}
