import type { ErpDocumentType } from "@/types/erp-document"

export const DOCUMENTS_PAGE_SIZE = 20

export type DocumentsListFilters = {
  search?: string
  document_type: ErpDocumentType
}

export function buildDocumentsListFilters(
  search: string,
  documentType: ErpDocumentType,
): DocumentsListFilters {
  return {
    search: search.trim() || undefined,
    document_type: documentType,
  }
}
