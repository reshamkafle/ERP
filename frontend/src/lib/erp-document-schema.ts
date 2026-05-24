import { z } from "zod"

import type { ErpDocumentStatus, ErpDocumentType } from "@/types/erp-document"

const documentTypes = [
  "TECH_PACK",
  "BOM",
  "PURCHASE_ORDER",
  "GRN",
  "INSPECTION_REPORT",
  "LAB_TEST_REPORT",
  "PRODUCTION_ORDER",
  "STOCK_TRANSFER",
  "INVENTORY_ADJUSTMENT",
  "PICK_LIST",
  "PACKING_LIST",
  "SHIPPING_MARKS",
  "ASN",
  "COMMERCIAL_INVOICE",
  "OUTGOING_INVOICE",
  "BILL_OF_LADING",
  "CERTIFICATE_OF_ORIGIN",
  "EXPORT_DECLARATION",
  "LETTER_OF_CREDIT",
  "BILL_OF_EXCHANGE",
  "PROOF_OF_DELIVERY",
  "PAYMENT_RECORD",
  "LANDED_COST",
] as const satisfies readonly ErpDocumentType[]

const documentStatuses = [
  "DRAFT",
  "ISSUED",
  "CONFIRMED",
  "CANCELLED",
] as const satisfies readonly ErpDocumentStatus[]

export const erpDocumentFormSchema = z.object({
  document_type: z.enum(documentTypes),
  title: z.string().min(1, "Title is required").max(255),
  status: z.enum(documentStatuses),
  reference_number: z.string().max(128).optional(),
  notes: z.string().optional(),
  supplier_id: z.string().optional(),
  customer_id: z.string().optional(),
  purchase_id: z.string().optional(),
  related_document_id: z.string().optional(),
})

export type ErpDocumentFormValues = z.infer<typeof erpDocumentFormSchema>
