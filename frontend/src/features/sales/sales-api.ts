import { api } from "@/lib/api"
import type {
  SaleListResponse,
  SaleLookups,
  SaleOrder,
  SaleOrderPayload,
} from "@/types/sale"

export type SalesListParams = {
  customer_id?: number
  order_status?: string
  order_number?: string
  date_from?: string
  date_to?: string
  skip?: number
  limit?: number
}

export async function fetchSaleLookups() {
  const { data } = await api.get<SaleLookups>("/v1/sales/lookups")
  return data
}

export async function fetchSales(params?: SalesListParams) {
  const { data } = await api.get<SaleListResponse>("/v1/sales", { params })
  return data
}

export async function fetchSale(saleId: number) {
  const { data } = await api.get<SaleOrder>(`/v1/sales/${saleId}`)
  return data
}

export async function createSaleOrder(payload: SaleOrderPayload) {
  const { data } = await api.post<SaleOrder>("/v1/sales", payload)
  return data
}

export async function updateSaleOrder(saleId: number, payload: Partial<SaleOrderPayload>) {
  const { data } = await api.patch<SaleOrder>(`/v1/sales/${saleId}`, payload)
  return data
}

export async function confirmSaleOrder(
  saleId: number,
  body?: { run_credit_check?: boolean; run_atp_check?: boolean; override_credit_failure?: boolean },
) {
  const { data } = await api.post<SaleOrder>(`/v1/sales/${saleId}/confirm`, body ?? {})
  return data
}

export async function cancelSaleOrder(saleId: number, reason?: string) {
  const { data } = await api.post<SaleOrder>(`/v1/sales/${saleId}/cancel`, null, {
    params: reason ? { reason } : undefined,
  })
  return data
}

export async function runCreditCheck(saleId: number) {
  const { data } = await api.post<SaleOrder>(`/v1/sales/${saleId}/credit-check`)
  return data
}

export async function runAtpCheck(saleId: number) {
  const { data } = await api.post<SaleOrder>(`/v1/sales/${saleId}/atp-check`)
  return data
}
