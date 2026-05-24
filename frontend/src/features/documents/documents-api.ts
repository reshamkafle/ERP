import { api } from "@/lib/api"
import type { ErpDocumentFormValues } from "@/lib/erp-document-schema"
import type {
  ErpDocument,
  ErpDocumentJourneyViewResponse,
  ErpDocumentListResponse,
  ErpDocumentType,
  JourneyResponse,
} from "@/types/erp-document"

function parseOptionalId(value: string | undefined): number | null {
  if (!value?.trim()) return null
  const n = Number(value)
  return Number.isFinite(n) && n > 0 ? n : null
}

function buildPayload(values: ErpDocumentFormValues) {
  return {
    document_type: values.document_type,
    title: values.title,
    status: values.status,
    reference_number: values.reference_number?.trim() || null,
    notes: values.notes?.trim() || null,
    content: {},
    supplier_id: parseOptionalId(values.supplier_id),
    customer_id: parseOptionalId(values.customer_id),
    purchase_id: parseOptionalId(values.purchase_id),
    related_document_id: parseOptionalId(values.related_document_id),
  }
}

export async function fetchDocumentJourney() {
  const { data } = await api.get<JourneyResponse>("/v1/erp-documents/journey")
  return data
}

export async function fetchDocumentJourneyView() {
  const { data } = await api.get<ErpDocumentJourneyViewResponse>("/v1/erp-documents/journey-view")
  return data
}

export async function fetchErpDocuments(params: {
  search?: string
  document_type?: ErpDocumentType
  phase?: string
  skip?: number
  limit?: number
}) {
  const { data } = await api.get<ErpDocumentListResponse>("/v1/erp-documents", { params })
  return data
}

export async function fetchErpDocument(id: number) {
  const { data } = await api.get<ErpDocument>(`/v1/erp-documents/${id}`)
  return data
}

export async function createErpDocument(values: ErpDocumentFormValues) {
  const { data } = await api.post<ErpDocument>("/v1/erp-documents", buildPayload(values))
  return data
}

export async function updateErpDocument(id: number, values: ErpDocumentFormValues) {
  const payload = buildPayload(values)
  const { data } = await api.patch<ErpDocument>(`/v1/erp-documents/${id}`, {
    title: payload.title,
    status: payload.status,
    reference_number: payload.reference_number,
    notes: payload.notes,
    content: payload.content,
    supplier_id: payload.supplier_id,
    customer_id: payload.customer_id,
    purchase_id: payload.purchase_id,
    related_document_id: payload.related_document_id,
  })
  return data
}

export async function deleteErpDocument(id: number) {
  await api.delete(`/v1/erp-documents/${id}`)
}
