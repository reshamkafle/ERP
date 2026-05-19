import { api } from "@/lib/api"
import type {
  PromotionConfirmBody,
  PromotionRunCreateBody,
  PromotionRunDetail,
  PromotionRunResponse,
} from "@/types/promotion"

export async function createPromotionRun(body: PromotionRunCreateBody = {}) {
  const { data } = await api.post<PromotionRunResponse>("/v1/promotion-runs", body)
  return data
}

export async function fetchPromotionRun(runId: number) {
  const { data } = await api.get<PromotionRunDetail>(`/v1/promotion-runs/${runId}`)
  return data
}

export async function confirmPromotionRun(runId: number, body: PromotionConfirmBody) {
  const { data } = await api.post<PromotionRunDetail>(`/v1/promotion-runs/${runId}/confirm`, body)
  return data
}
