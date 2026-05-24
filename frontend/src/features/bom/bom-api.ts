import axios from "axios"

import { api } from "@/lib/api"
import type {
  BOMAlternateCreate,
  BOMAlternateRead,
  BOMRead,
  BOMStatus,
  BOMSubstituteCreate,
  BOMSubstituteRead,
  BOMSummary,
  BOMTree,
  ExplosionResult,
  FabricSummary,
  ManufacturingItem,
  SaveBOMRequest,
  SaveBOMResponse,
  TrimSummary,
} from "@/types/bom"

export async function fetchBomList() {
  const { data } = await api.get<{ boms: BOMSummary[] }>("/v1/bom")
  return data.boms
}

export async function fetchBomItems(category?: string) {
  const { data } = await api.get<{ items: ManufacturingItem[] }>("/v1/bom/items", {
    params: category ? { category } : undefined,
  })
  return data.items
}

export async function fetchBom(sku: string) {
  const { data } = await api.get<BOMRead>(`/v1/bom/${encodeURIComponent(sku)}`)
  return data
}

/** Returns null when the parent exists but has no BOM yet (HTTP 404). */
export async function fetchBomOptional(sku: string): Promise<BOMRead | null> {
  try {
    return await fetchBom(sku)
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      return null
    }
    throw err
  }
}

export async function saveBom(sku: string, payload: SaveBOMRequest) {
  const { data } = await api.post<SaveBOMResponse>(
    `/v1/bom/${encodeURIComponent(sku)}`,
    payload,
  )
  return data
}

export async function updateBomStatus(sku: string, status: BOMStatus) {
  const { data } = await api.patch<BOMRead>(
    `/v1/bom/${encodeURIComponent(sku)}/status`,
    { status },
  )
  return data
}

export async function fetchBomTree(sku: string, depth?: number) {
  const { data } = await api.get<BOMTree>(`/v1/bom/${encodeURIComponent(sku)}/tree`, {
    params: depth !== undefined ? { depth } : undefined,
  })
  return data
}

export async function fetchBomExplosion(sku: string, orderQuantity: number) {
  const { data } = await api.get<ExplosionResult>(
    `/v1/bom/${encodeURIComponent(sku)}/explode`,
    { params: { order_quantity: orderQuantity } },
  )
  return data
}

export async function fetchFabricSummary(sku: string, orderQty: number) {
  const { data } = await api.get<FabricSummary>(
    `/v1/bom/${encodeURIComponent(sku)}/fabric-summary`,
    { params: { order_qty: orderQty } },
  )
  return data
}

export async function fetchTrimSummary(sku: string, orderQty: number) {
  const { data } = await api.get<TrimSummary>(
    `/v1/bom/${encodeURIComponent(sku)}/trim-summary`,
    { params: { order_qty: orderQty } },
  )
  return data
}

export async function addBomAlternate(sku: string, payload: BOMAlternateCreate) {
  const { data } = await api.post<BOMAlternateRead>(
    `/v1/bom/${encodeURIComponent(sku)}/alternates`,
    payload,
  )
  return data
}

export async function addBomSubstitute(
  sku: string,
  lineId: number,
  payload: BOMSubstituteCreate,
) {
  const { data } = await api.post<BOMSubstituteRead>(
    `/v1/bom/${encodeURIComponent(sku)}/lines/${lineId}/substitutes`,
    payload,
  )
  return data
}
