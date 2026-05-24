import { api } from "@/lib/api"
import type {
  ModuleCatalogResponse,
  ModuleOverview,
  ModuleRecord,
  ModuleRecordCreate,
  ModuleRecordListResponse,
  ModuleRecordUpdate,
} from "@/types/module"

export async function fetchModuleCatalog() {
  const { data } = await api.get<ModuleCatalogResponse>("/v1/erp-modules/catalog")
  return data
}

export async function fetchModuleOverview(moduleCode: string) {
  const { data } = await api.get<ModuleOverview>(`/v1/erp-modules/${moduleCode}/overview`)
  return data
}

export async function fetchModuleRecords(
  moduleCode: string,
  params?: { feature_code?: string; search?: string; status?: string; limit?: number },
) {
  const { data } = await api.get<ModuleRecordListResponse>(
    `/v1/erp-modules/${moduleCode}/records`,
    { params },
  )
  return data
}

export async function fetchModuleRecord(moduleCode: string, recordId: number) {
  const { data } = await api.get<ModuleRecord>(
    `/v1/erp-modules/${moduleCode}/records/${recordId}`,
  )
  return data
}

export async function createModuleRecord(moduleCode: string, body: ModuleRecordCreate) {
  const { data } = await api.post<ModuleRecord>(`/v1/erp-modules/${moduleCode}/records`, body)
  return data
}

export async function updateModuleRecord(
  moduleCode: string,
  recordId: number,
  body: ModuleRecordUpdate,
) {
  const { data } = await api.patch<ModuleRecord>(
    `/v1/erp-modules/${moduleCode}/records/${recordId}`,
    body,
  )
  return data
}

export async function deleteModuleRecord(moduleCode: string, recordId: number) {
  await api.delete(`/v1/erp-modules/${moduleCode}/records/${recordId}`)
}
