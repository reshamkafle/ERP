import { api } from "@/lib/api"
import {
  formToSupplierPayload,
  type SupplierFormValues,
} from "@/lib/supplier-schema"
import type {
  Supplier,
  SupplierDetail,
  SupplierListResponse,
} from "@/types/supplier"

export type SupplierPayload = ReturnType<typeof formToSupplierPayload>

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

export async function createSupplier(payload: SupplierPayload) {
  const { data } = await api.post<Supplier>("/v1/suppliers", payload)
  return data
}

export async function updateSupplier(id: number, payload: SupplierPayload) {
  const { data } = await api.patch<Supplier>(`/v1/suppliers/${id}`, payload)
  return data
}

export async function deleteSupplier(id: number) {
  await api.delete(`/v1/suppliers/${id}`)
}

export function supplierFormToPayload(values: SupplierFormValues): SupplierPayload {
  return formToSupplierPayload(values)
}
