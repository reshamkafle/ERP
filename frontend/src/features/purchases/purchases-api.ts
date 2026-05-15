import { api } from "@/lib/api"
import type {
  PurchaseListResponse,
  PurchaseProductListResponse,
  PurchaseRead,
} from "@/types/purchase"

export type PurchaseCreatePayload = {
  supplier_id: number
  items: { product_id: number; quantity: number; unit_cost: number }[]
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
