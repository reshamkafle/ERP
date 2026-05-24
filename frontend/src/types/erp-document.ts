export type ErpDocumentType =
  | "TECH_PACK"
  | "BOM"
  | "PURCHASE_ORDER"
  | "GRN"
  | "INSPECTION_REPORT"
  | "LAB_TEST_REPORT"
  | "PRODUCTION_ORDER"
  | "STOCK_TRANSFER"
  | "INVENTORY_ADJUSTMENT"
  | "PICK_LIST"
  | "PACKING_LIST"
  | "SHIPPING_MARKS"
  | "ASN"
  | "COMMERCIAL_INVOICE"
  | "OUTGOING_INVOICE"
  | "BILL_OF_LADING"
  | "CERTIFICATE_OF_ORIGIN"
  | "EXPORT_DECLARATION"
  | "LETTER_OF_CREDIT"
  | "BILL_OF_EXCHANGE"
  | "PROOF_OF_DELIVERY"
  | "PAYMENT_RECORD"
  | "LANDED_COST"

export type ErpDocumentStatus = "DRAFT" | "ISSUED" | "CONFIRMED" | "CANCELLED"

export type JourneyStep = {
  document_type: ErpDocumentType
  journey_step: number
  phase: string
  label: string
  slug: string
  number_prefix: string
}

export type JourneyResponse = {
  steps: JourneyStep[]
  phases: string[]
}

export type ErpDocument = {
  id: number
  document_number: string
  document_type: ErpDocumentType
  type_label: string
  journey_step: number
  phase: string
  status: ErpDocumentStatus
  title: string
  reference_number: string | null
  notes: string | null
  content: Record<string, unknown>
  supplier_id: number | null
  customer_id: number | null
  purchase_id: number | null
  related_document_id: number | null
  created_by_id: number | null
  created_at: string
  updated_at: string
}

export type ErpDocumentListResponse = {
  items: ErpDocument[]
  total: number
}

export type ErpDocumentJourneyGroup = {
  phase: string
  journey_step_start: number
  steps: JourneyStep[]
  documents: ErpDocument[]
}

export type ErpDocumentJourneyViewResponse = {
  phases: ErpDocumentJourneyGroup[]
  total_documents: number
}
