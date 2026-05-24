import { api } from "@/lib/api"
import type {
  StorageLocation,
  StorageLocationListResponse,
  Warehouse,
  WarehouseListResponse,
} from "@/types/inventory"

export type WarehouseFormValues = {
  code: string
  name: string
  warehouse_type: string
  address: string
  capacity_weight: string
  capacity_volume: string
  capacity_pallets: number | ""
  status: string
  is_default: boolean
  wave_picking_enabled: boolean
  cross_docking_enabled: boolean
  cycle_count_frequency: string
  cycle_count_class: string
  packing_rules_json: string
}

export type LocationFormValues = {
  code: string
  warehouse_id: number
  aisle: string
  row: string
  column: string
  level: string
  location_type: string
  capacity: string
  putaway_strategy: string
  picking_strategy: string
  status: string
  zone: string
}

export async function fetchWarehouses(params?: { search?: string; skip?: number; limit?: number }) {
  const { data } = await api.get<WarehouseListResponse>("/v1/warehouses", { params })
  return data
}

export async function createWarehouse(values: WarehouseFormValues) {
  const { data } = await api.post<Warehouse>("/v1/warehouses", warehousePayload(values))
  return data
}

export async function updateWarehouse(id: number, values: WarehouseFormValues) {
  const { data } = await api.patch<Warehouse>(`/v1/warehouses/${id}`, warehousePayload(values))
  return data
}

export async function deleteWarehouse(id: number) {
  await api.delete(`/v1/warehouses/${id}`)
}

function warehousePayload(values: WarehouseFormValues) {
  let packing_rules = null
  if (values.packing_rules_json.trim()) {
    try {
      packing_rules = JSON.parse(values.packing_rules_json)
    } catch {
      packing_rules = null
    }
  }
  return {
    code: values.code,
    name: values.name,
    warehouse_type: values.warehouse_type,
    address: values.address || null,
    capacity_weight: values.capacity_weight || null,
    capacity_volume: values.capacity_volume || null,
    capacity_pallets: values.capacity_pallets === "" ? null : values.capacity_pallets,
    status: values.status,
    is_default: values.is_default,
    wave_picking_enabled: values.wave_picking_enabled,
    cross_docking_enabled: values.cross_docking_enabled,
    cycle_count_frequency: values.cycle_count_frequency || null,
    cycle_count_class: values.cycle_count_class || null,
    packing_rules,
  }
}

export async function fetchStorageLocations(params?: {
  warehouse_id?: number
  search?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<StorageLocationListResponse>("/v1/storage-locations", { params })
  return data
}

export async function createStorageLocation(values: LocationFormValues) {
  const { data } = await api.post<StorageLocation>("/v1/storage-locations", {
    code: values.code,
    warehouse_id: values.warehouse_id,
    aisle: values.aisle || null,
    row: values.row || null,
    column: values.column || null,
    level: values.level || null,
    location_type: values.location_type,
    capacity: values.capacity || null,
    putaway_strategy: values.putaway_strategy || null,
    picking_strategy: values.picking_strategy || null,
    status: values.status,
    zone: values.zone || null,
  })
  return data
}

export async function updateStorageLocation(id: number, values: LocationFormValues) {
  const { data } = await api.patch<StorageLocation>(`/v1/storage-locations/${id}`, {
    code: values.code,
    warehouse_id: values.warehouse_id,
    aisle: values.aisle || null,
    row: values.row || null,
    column: values.column || null,
    level: values.level || null,
    location_type: values.location_type,
    capacity: values.capacity || null,
    putaway_strategy: values.putaway_strategy || null,
    picking_strategy: values.picking_strategy || null,
    status: values.status,
    zone: values.zone || null,
  })
  return data
}

export async function deleteStorageLocation(id: number) {
  await api.delete(`/v1/storage-locations/${id}`)
}
