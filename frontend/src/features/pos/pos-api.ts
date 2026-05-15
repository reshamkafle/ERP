import { api } from "@/lib/api"
import type { PosProductListResponse, Sale, SaleCheckoutPayload } from "@/types/sale"

export async function fetchPosProducts(params: { search?: string; limit?: number }) {
  const { data } = await api.get<PosProductListResponse>("/v1/sales/products", { params })
  return data
}

export async function checkoutSale(payload: SaleCheckoutPayload) {
  const { data } = await api.post<Sale>("/v1/sales", payload)
  return data
}
