export type DocumentFlowChartPoint = {
  label: string
  count: number
}

export type DocumentFlowCardMetrics = {
  id: string
  total: number
  new_count: number
  chart: DocumentFlowChartPoint[]
}

export type DocumentFlowMetricsResponse = {
  period: string
  new_days: number
  cards: DocumentFlowCardMetrics[]
}

export type DocumentFlowPeriod = "today" | "week"
