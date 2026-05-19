import { z } from "zod"

export const inventoryFormSchema = z
  .object({
    sku: z.string().min(1, "SKU is required").max(64),
    name: z.string().min(1, "Name is required").max(255),
    description: z.string().optional(),
    barcode: z.string().max(64).optional(),
    alternate_codes: z.string().optional(),
    category_id: z.number().nullable(),
    sub_category: z.string().max(120).optional(),
    product_line: z.string().max(120).optional(),
    item_type: z.enum(["RAW", "FINISHED", "TRADING", "SERVICE", "ASSET"]),
    size: z.string().max(64).optional(),
    color: z.string().max(64).optional(),
    model: z.string().max(120).optional(),
    variant: z.string().max(120).optional(),
    serial_number_flag: z.boolean(),
    batch_lot_flag: z.boolean(),
    expiry_date_flag: z.boolean(),
    primary_uom: z.string().min(1).max(32),
    secondary_uom: z.string().max(32).optional(),
    conversion_factor: z.string().optional(),
    length: z.string().optional(),
    width: z.string().optional(),
    height: z.string().optional(),
    volume: z.string().optional(),
    gross_weight: z.string().optional(),
    net_weight: z.string().optional(),
    lifecycle_status: z.enum(["ACTIVE", "INACTIVE", "DISCONTINUED", "OBSOLETE"]),
    approval_status: z.enum(["DRAFT", "PENDING", "APPROVED", "REJECTED"]),
    tax_code: z.string().max(64).optional(),
    hs_code: z.string().max(32).optional(),
    country_of_origin: z.string().max(64).optional(),
    hazardous_flag: z.boolean(),
    perishable_flag: z.boolean(),
    price: z.number().min(0),
    cost_price: z.number().min(0),
    low_stock_threshold: z.number().min(0),
    default_supplier_id: z.number().int().positive().nullable(),
    promotion_reorder_boost: z.boolean(),
    initial_stock: z.number().min(0).optional(),
  })
  .superRefine((data, ctx) => {
    const hasSecondary = Boolean(data.secondary_uom?.trim())
    const hasConversion = Boolean(data.conversion_factor)
    if (hasSecondary && !hasConversion) {
      ctx.addIssue({
        code: "custom",
        message: "Conversion factor required when secondary UOM is set",
        path: ["conversion_factor"],
      })
    }
    if (hasConversion && !hasSecondary) {
      ctx.addIssue({
        code: "custom",
        message: "Secondary UOM required when conversion factor is set",
        path: ["secondary_uom"],
      })
    }
  })

export type InventoryFormValues = z.infer<typeof inventoryFormSchema>
