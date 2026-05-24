import type { ItemLifecycleStatus, ItemType } from "@/types/inventory"

export const INVENTORY_PAGE_SIZE = 20

export type InventoryListFilters = {
  search?: string
  category_id?: number
  item_type?: string
  lifecycle_status?: string
  template_id?: number
  style_code?: string
  color?: string
  size?: string
  variants_only?: boolean
}

export function buildInventoryListFilters(
  search: string,
  categoryId: string,
  itemType: ItemType | "",
  lifecycleStatus: ItemLifecycleStatus | "",
  styleCode = "",
  color = "",
  size = "",
  variantsOnly = false,
): InventoryListFilters {
  return {
    search: search || undefined,
    category_id: categoryId ? Number(categoryId) : undefined,
    item_type: itemType || undefined,
    lifecycle_status: lifecycleStatus || undefined,
    style_code: styleCode || undefined,
    color: color || undefined,
    size: size || undefined,
    variants_only: variantsOnly || undefined,
  }
}
