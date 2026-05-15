import { api } from "@/lib/api"
import type { Sale, SaleListResponse } from "@/types/sale"

export async function fetchSales(params: {
  customer_id?: number
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<SaleListResponse>("/v1/sales", { params })
  return data
}

export async function fetchSale(saleId: number) {
  const { data } = await api.get<Sale>(`/v1/sales/${saleId}`)
  return data
}
