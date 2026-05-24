import { api } from "@/lib/api"

export type ProductionContractType = "CMT" | "FOB"
export type ProductionPlanStatus = "DRAFT" | "SCHEDULED" | "IN_PROGRESS" | "CLOSED" | "CANCELLED"
export type CutOrderStatus = "DRAFT" | "RELEASED" | "CUTTING" | "COMPLETED" | "CANCELLED"

export type ProductionPlanLine = {
  id: number
  production_plan_id: number
  product_id: number
  color_value_id: number | null
  size_value_id: number | null
  quantity_planned: string
  quantity_cut: string
  quantity_sewn: string
  quantity_packed: string
  due_date: string | null
  priority: number
  product_sku?: string | null
  product_name?: string | null
  color_label?: string | null
  size_label?: string | null
}

export type ProductionPlan = {
  id: number
  plan_number: string
  status: ProductionPlanStatus
  sales_order_id: number | null
  style_template_id: number | null
  contract_id: number | null
  bom_parent_item_id: number | null
  routing_id: number | null
  target_ship_date: string | null
  planning_horizon_days: number
  notes: string | null
  created_at: string
  updated_at: string
  lines: ProductionPlanLine[]
  schedules: {
    id: number
    schedule_date: string
    planned_output: string
    sewing_line_code?: string | null
  }[]
  contract_type?: ProductionContractType | null
  contract_number?: string | null
}

export type ProductionPlanListResponse = {
  items: ProductionPlan[]
  total: number
}

export type CutOrder = {
  id: number
  cut_order_number: string
  production_plan_id: number
  status: CutOrderStatus
  fabric_item_id: number | null
  cutting_date: string | null
  priority: number
  marker_ref: string | null
  marker_length: string | null
  marker_width: string | null
  efficiency_pct: string | null
  plies: number | null
  notes: string | null
  fabric_item_sku?: string | null
  size_breakdowns: {
    id: number
    color_label: string | null
    size_label: string | null
    pieces_to_cut: string
    pieces_cut: string
  }[]
}

export type LineBalanceResult = {
  calculated_takt_minutes: string
  line_efficiency_pct: string
  bottleneck_station: number
  assignments: {
    operation_name: string
    station_no: number
    assigned_smv: string
  }[]
  station_loads: { station_no: number; total_smv: string; utilization_pct: string }[]
}

export type ProductionContract = {
  id: number
  contract_number: string
  contract_type: ProductionContractType
  buyer_name: string | null
  sales_order_id: number | null
  material_supplies: {
    id: number
    manufacturing_item_id: number
    quantity_received: string
    quantity_consumed: string
  }[]
}

export async function fetchProductionPlans(skip = 0, limit = 100) {
  const { data } = await api.get<ProductionPlanListResponse>("/manufacturing/planning/plans", {
    params: { skip, limit },
  })
  return data
}

export async function fetchProductionPlan(id: number) {
  const { data } = await api.get<ProductionPlan>(`/manufacturing/planning/plans/${id}`)
  return data
}

export async function createPlanFromSales(salesOrderId: number, contractId?: number) {
  const { data } = await api.post<ProductionPlan>("/manufacturing/planning/plans/from-sales", {
    sales_order_id: salesOrderId,
    contract_id: contractId ?? null,
  })
  return data
}

export async function schedulePlan(id: number) {
  const { data } = await api.post<ProductionPlan>(`/manufacturing/planning/plans/${id}/schedule`)
  return data
}

export async function releasePlan(id: number) {
  const { data } = await api.post<ProductionPlan>(`/manufacturing/planning/plans/${id}/release`)
  return data
}

export async function fetchCutOrders(planId?: number) {
  const { data } = await api.get<CutOrder[]>("/manufacturing/cut-orders", {
    params: planId ? { plan_id: planId } : {},
  })
  return data
}

export async function completeCutOrder(id: number) {
  const { data } = await api.post<CutOrder>(`/manufacturing/cut-orders/${id}/complete`)
  return data
}

export async function fetchContracts() {
  const { data } = await api.get<ProductionContract[]>("/manufacturing/contracts")
  return data
}

export async function calculateLineBalance(body: {
  operations: { operation_name: string; smv_minutes: number }[]
  operators_count: number
  target_quantity: number
  available_minutes: number
}) {
  const { data } = await api.post<LineBalanceResult>("/manufacturing/line-balancing/calculate", body)
  return data
}
