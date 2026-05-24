import { api } from "@/lib/api"
import type {
  MaterialRoll,
  MaterialRollDetail,
  MaterialRollListResponse,
  MaterialRollReceiveInput,
  MaterialRollScanResult,
  MaterialRollStatus,
} from "@/types/material-roll"

export async function fetchMaterialRolls(params: {
  search?: string
  product_id?: number
  status?: MaterialRollStatus
  dye_lot?: string
  skip?: number
  limit?: number
}): Promise<MaterialRollListResponse> {
  const res = await api.get<MaterialRollListResponse>("/v1/material-rolls", { params })
  return res.data
}

export async function fetchMaterialRoll(id: number): Promise<MaterialRollDetail> {
  const res = await api.get<MaterialRollDetail>(`/v1/material-rolls/${id}`)
  return res.data
}

export async function receiveMaterialRoll(body: MaterialRollReceiveInput): Promise<MaterialRoll> {
  const res = await api.post<MaterialRoll>("/v1/material-rolls/receive", body)
  return res.data
}

export async function scanMaterialRoll(identifier: {
  barcode?: string
  rfid_tag?: string
  roll_number?: string
}): Promise<MaterialRollScanResult> {
  const res = await api.post<MaterialRollScanResult>("/v1/material-rolls/scan", identifier)
  return res.data
}

export async function fetchRollLabelHtml(rollId: number): Promise<string> {
  const res = await api.get(`/v1/material-rolls/${rollId}/label/print`, {
    responseType: "text",
  })
  return res.data as string
}

export async function issueMaterialRoll(
  rollId: number,
  body: { quantity: number; reference_document?: string; remarks?: string },
): Promise<MaterialRoll> {
  const res = await api.post<MaterialRoll>(`/v1/material-rolls/${rollId}/issue`, body)
  return res.data
}
