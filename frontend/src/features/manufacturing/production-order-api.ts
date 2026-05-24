import { api } from "@/lib/api"

export type ProductionOrderStatus =
  | "PLANNED"
  | "RELEASED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "CLOSED"
  | "CANCELLED"

export type ProductionOrder = {
  id: number
  order_number: string
  status: ProductionOrderStatus
  priority: string
  product_id: number
  product_name?: string | null
  product_sku?: string | null
  quantity_planned: string
  quantity_completed: string
  quantity_scrapped: string
  quantity_rework: string
  start_date: string | null
  end_date: string | null
  bom_parent_item_id: number | null
  routing_id: number | null
  production_version_id: number | null
  sales_order_id: number | null
  warehouse_id: number | null
  wip_warehouse_id: number | null
  creation_source: string
  notes: string | null
  created_at: string
  updated_at: string
  operations: {
    id: number
    sequence: number
    operation_name: string
    work_center_id: number | null
    status: string
    setup_time_minutes: string
    run_time_minutes: string
  }[]
}

export type ProductionOrderListResponse = {
  items: ProductionOrder[]
  total: number
}

export type ProductionOrderCreate = {
  product_id: number
  quantity_planned: number | string
  priority?: string
  start_date?: string | null
  end_date?: string | null
  bom_parent_item_id?: number | null
  routing_id?: number | null
  production_version_id?: number | null
  sales_order_id?: number | null
  warehouse_id?: number | null
  wip_warehouse_id?: number | null
  notes?: string | null
  order_number?: string | null
}

export type WorkCenter = {
  id: number
  code: string
  name: string
}

export type Routing = {
  id: number
  code: string
  name: string
}

export async function fetchProductionOrders(params?: {
  status?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<ProductionOrderListResponse>(
    "/v1/manufacturing/production-orders",
    { params },
  )
  return data
}

export async function fetchProductionOrder(id: number) {
  const { data } = await api.get<ProductionOrder>(`/v1/manufacturing/production-orders/${id}`)
  return data
}

export async function createProductionOrder(body: ProductionOrderCreate) {
  const { data } = await api.post<ProductionOrder>("/v1/manufacturing/production-orders", body)
  return data
}

export async function updateProductionOrder(id: number, body: Partial<ProductionOrderCreate>) {
  const { data } = await api.patch<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}`,
    body,
  )
  return data
}

export async function releaseProductionOrder(id: number) {
  const { data } = await api.post<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}/release`,
  )
  return data
}

export async function startProductionOrder(id: number) {
  const { data } = await api.post<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}/start`,
  )
  return data
}

export async function confirmProductionOrder(
  id: number,
  body: {
    quantity_completed: number | string
    quantity_rejected?: number | string
    quantity_rework?: number | string
    backflush?: boolean
    operation_id?: number | null
    notes?: string | null
  },
) {
  const { data } = await api.post<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}/confirm`,
    body,
  )
  return data
}

export async function completeProductionOrder(id: number) {
  const { data } = await api.post<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}/complete`,
  )
  return data
}

export async function closeProductionOrder(id: number) {
  const { data } = await api.post<ProductionOrder>(
    `/v1/manufacturing/production-orders/${id}/close`,
  )
  return data
}

export async function fetchWorkCenters() {
  const { data } = await api.get<WorkCenter[]>("/v1/manufacturing/work-centers")
  return data
}

export async function fetchRoutings() {
  const { data } = await api.get<Routing[]>("/v1/manufacturing/routings")
  return data
}

export async function runMrp(body: {
  horizon_days?: number
  include_sales?: boolean
  include_forecasts?: boolean
}) {
  const { data } = await api.post("/v1/manufacturing/mrp/runs", body)
  return data
}

export async function fetchProductionMetrics() {
  const { data } = await api.get<{
    oee_pct: string
    yield_pct: string
    avg_cycle_time_minutes: string
    total_downtime_minutes: string
    orders_completed: number
  }>("/v1/manufacturing/reports/metrics")
  return data
}
