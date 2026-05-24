import { api } from "@/lib/api"
import type {
  ProcurementRunResponse,
  PurchaseListResponse,
  PurchaseProductListResponse,
  PurchaseRead,
} from "@/types/purchase"

export type PurchaseCreatePayload = {
  supplier_id: number
  items: { product_id: number; quantity: number }[]
}

export async function fetchPurchaseProducts(params: {
  search?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<PurchaseProductListResponse>("/v1/purchases/products", {
    params,
  })
  return data
}

export async function fetchPurchases(params: {
  supplier_id?: number
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<PurchaseListResponse>("/v1/purchases", { params })
  return data
}

export async function createPurchase(payload: PurchaseCreatePayload) {
  const { data } = await api.post<PurchaseRead>("/v1/purchases", payload)
  return data
}

export type ProcurementRunBody = {
  sales_lookback_days?: number
  max_lines_per_supplier?: number
  velocity_limit?: number
}

export async function createProcurementRun(body: ProcurementRunBody = {}) {
  const { data } = await api.post<ProcurementRunResponse>("/v1/procurement-runs", body)
  return data
}

export async function confirmPurchase(purchaseId: number) {
  const { data } = await api.post<PurchaseRead>(`/v1/purchases/${purchaseId}/confirm`)
  return data
}

export async function discardDraftPurchase(purchaseId: number) {
  await api.delete(`/v1/purchases/${purchaseId}`)
}
