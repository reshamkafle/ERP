import { api } from "@/lib/api"
import type {
  DocumentFlowMetricsResponse,
  DocumentFlowPeriod,
} from "@/types/dashboard-flow"

export async function fetchDocumentFlowMetrics(params?: {
  period?: DocumentFlowPeriod
  newDays?: number
}): Promise<DocumentFlowMetricsResponse> {
  const { data } = await api.get<DocumentFlowMetricsResponse>(
    "/v1/dashboard/document-flow-metrics",
    {
      params: {
        period: params?.period ?? "week",
        new_days: params?.newDays ?? 30,
      },
    },
  )
  return data
}
