import type { BOMRead, ManufacturingItem } from "@/types/bom"

/** Draft BOM for a parent that has a manufacturing item but no BOM header yet. */
export function createEmptyBom(parent: ManufacturingItem): BOMRead {
  return {
    parent_item_id: parent.id,
    parent_sku: parent.sku,
    parent_name: parent.name,
    parent_description: null,
    bom_number: `${parent.sku}-V1`,
    version: 1,
    status: "DRAFT",
    bom_type: "MANUFACTURING",
    effective_start_date: null,
    effective_end_date: null,
    eco_number: null,
    approved_at: null,
    approved_by_id: null,
    created_by_id: null,
    created_at: null,
    updated_by_id: null,
    updated_at: null,
    parent_product_snapshot: null,
    lines: [],
    alternates: [],
  }
}
