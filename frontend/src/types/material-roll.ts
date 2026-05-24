export type MaterialRollStatus =
  | "IN_STOCK"
  | "ALLOCATED"
  | "IN_PRODUCTION"
  | "ON_HOLD"
  | "QUARANTINED"
  | "REJECTED"
  | "SHIPPED"

export type MaterialFinishType = "GREIGE" | "DYED" | "PRINTED" | "FINISHED" | "OTHER"

export interface MaterialRoll {
  id: number
  roll_number: string
  barcode: string | null
  rfid_tag: string | null
  serial_number: string | null
  product_id: number
  product_sku: string | null
  product_name: string | null
  material_type: string | null
  composition: string | null
  color: string | null
  dye_lot: string | null
  pattern: string | null
  gsm: string | null
  width: string | null
  finish_type: MaterialFinishType | null
  initial_quantity: string
  remaining_quantity: string
  primary_uom: string
  status: MaterialRollStatus
  warehouse_id: number | null
  location_id: number | null
  supplier_id: number | null
  supplier_lot_number: string | null
  grn_reference: string | null
  receipt_date: string | null
  quality_status: string
  inspection_passed: boolean | null
  last_scanned_at: string | null
  created_at: string
  updated_at: string
}

export interface MaterialRollMovement {
  id: number
  movement_type: string
  quantity_delta: string
  uom: string
  reference_document: string | null
  transaction_at: string
  remarks: string | null
}

export interface MaterialRollDetail extends MaterialRoll {
  movements: MaterialRollMovement[]
  inspections: { id: number; passed: boolean; inspected_at: string; notes: string | null }[]
  allocations: {
    id: number
    reference_type: string
    reference_id: number
    allocated_quantity: string
    status: string
  }[]
}

export interface MaterialRollListResponse {
  items: MaterialRoll[]
  total: number
}

export interface MaterialRollReceiveInput {
  product_id: number
  initial_quantity: number
  primary_uom?: string
  color?: string
  dye_lot?: string
  warehouse_id?: number
  barcode?: string
  rfid_tag?: string
  supplier_lot_number?: string
  grn_reference?: string
}

export interface MaterialRollScanResult {
  roll: MaterialRoll
  product_sku: string
  product_name: string
}
