export type InventoryFieldType = "text" | "number" | "textarea" | "select" | "checkbox"

export type InventoryFieldDef = {
  path: keyof import("@/lib/inventory-schema").InventoryFormValues | string
  label: string
  type?: InventoryFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
  /** Show only when this field is truthy */
  showWhen?: string
}

export type InventoryTabDef = {
  id: string
  title: string
  description?: string
  fields: InventoryFieldDef[]
  readOnly?: boolean
}

const itemTypeOptions = [
  { value: "RAW", label: "Raw material" },
  { value: "FINISHED", label: "Finished goods" },
  { value: "SEMI_FINISHED", label: "Semi-finished" },
  { value: "CONSUMABLE", label: "Consumable" },
  { value: "TRADING", label: "Trading" },
  { value: "SERVICE", label: "Service" },
  { value: "ASSET", label: "Asset" },
]

const abcOptions = [
  { value: "", label: "—" },
  { value: "A", label: "A" },
  { value: "B", label: "B" },
  { value: "C", label: "C" },
]

const xyzOptions = [
  { value: "", label: "—" },
  { value: "FAST", label: "Fast moving" },
  { value: "SLOW", label: "Slow moving" },
  { value: "NON_MOVING", label: "Non-moving" },
]

const valuationOptions = [
  { value: "", label: "—" },
  { value: "STANDARD", label: "Standard" },
  { value: "AVERAGE", label: "Average" },
  { value: "LAST_PURCHASE", label: "Last purchase" },
  { value: "FIFO", label: "FIFO" },
  { value: "LIFO", label: "LIFO" },
]

const lifecycleOptions = [
  { value: "ACTIVE", label: "Active" },
  { value: "INACTIVE", label: "Inactive" },
  { value: "DISCONTINUED", label: "Discontinued" },
  { value: "OBSOLETE", label: "Obsolete" },
]

const approvalOptions = [
  { value: "DRAFT", label: "Draft" },
  { value: "PENDING", label: "Pending" },
  { value: "APPROVED", label: "Approved" },
  { value: "REJECTED", label: "Rejected" },
]

export const INVENTORY_TABS: InventoryTabDef[] = [
  {
    id: "identification",
    title: "Identification",
    fields: [
      { path: "sku", label: "SKU / Item code" },
      { path: "name", label: "Item name" },
      { path: "barcode", label: "Barcode (EAN/UPC)" },
      { path: "qr_code", label: "QR code" },
      { path: "rfid_tag", label: "RFID tag" },
      { path: "alternate_codes", label: "Alternate codes", type: "textarea", colSpan: 2 },
      { path: "description", label: "Description", type: "textarea", colSpan: 2 },
      { path: "image_url", label: "Image URL", colSpan: 2 },
    ],
  },
  {
    id: "classification",
    title: "Classification",
    fields: [
      { path: "category_id", label: "Category", type: "select" },
      { path: "sub_category", label: "Sub-category" },
      { path: "product_line", label: "Product line / family" },
      { path: "item_type", label: "Item type", type: "select", options: itemTypeOptions },
      { path: "size", label: "Size" },
      { path: "color", label: "Color" },
      { path: "model", label: "Model" },
      { path: "variant", label: "Variant" },
      { path: "abc_class", label: "ABC class", type: "select", options: abcOptions },
      { path: "xyz_class", label: "XYZ class", type: "select", options: xyzOptions },
      { path: "lifecycle_status", label: "Lifecycle", type: "select", options: lifecycleOptions },
      { path: "approval_status", label: "Approval", type: "select", options: approvalOptions },
    ],
  },
  {
    id: "units",
    title: "Units & dimensions",
    fields: [
      { path: "primary_uom", label: "Primary UOM" },
      { path: "secondary_uom", label: "Secondary UOM" },
      { path: "purchase_uom", label: "Purchase UOM" },
      { path: "sales_uom", label: "Sales UOM" },
      { path: "conversion_factor", label: "Conversion factor" },
      { path: "length", label: "Length" },
      { path: "width", label: "Width" },
      { path: "height", label: "Height" },
      { path: "volume", label: "Volume" },
      { path: "gross_weight", label: "Gross weight" },
      { path: "net_weight", label: "Net weight" },
    ],
  },
  {
    id: "tracking",
    title: "Tracking",
    fields: [
      { path: "serial_number_flag", label: "Serial number tracking", type: "checkbox" },
      { path: "batch_lot_flag", label: "Lot / batch tracking", type: "checkbox" },
      { path: "roll_tracking_enabled", label: "Roll tracking (fabric)", type: "checkbox" },
      { path: "batch_management_enabled", label: "Batch management enabled", type: "checkbox" },
      { path: "expiry_date_flag", label: "Expiry date tracking", type: "checkbox" },
      { path: "shelf_life_days", label: "Shelf life (days)", type: "number", showWhen: "expiry_date_flag" },
      { path: "hazardous_flag", label: "Hazardous", type: "checkbox" },
      { path: "perishable_flag", label: "Perishable", type: "checkbox" },
    ],
  },
  {
    id: "pricing",
    title: "Pricing & costing",
    fields: [
      { path: "price", label: "Selling price", type: "number" },
      { path: "cost_price", label: "Cost price", type: "number" },
      { path: "standard_cost", label: "Standard cost", type: "number" },
      {
        path: "cost_valuation_method",
        label: "Valuation method",
        type: "select",
        options: valuationOptions,
      },
      { path: "tax_code", label: "Tax code (legacy)" },
      { path: "tax_rate_id", label: "Tax rate", type: "select" },
      { path: "hs_code", label: "HS code" },
      { path: "country_of_origin", label: "Country of origin" },
      { path: "low_stock_threshold", label: "Low stock threshold", type: "number" },
      { path: "reorder_level", label: "Reorder level", type: "number" },
      { path: "max_stock_level", label: "Max stock level", type: "number" },
      { path: "economic_order_qty", label: "Economic order qty (EOQ)", type: "number" },
      { path: "lead_time_days", label: "Lead time (days)", type: "number" },
      { path: "default_warehouse_id", label: "Default warehouse", type: "select" },
      { path: "default_location_id", label: "Default location", type: "select" },
    ],
  },
  {
    id: "replenishment",
    title: "Replenishment",
    fields: [
      { path: "reorder_point", label: "Reorder point", type: "number" },
      { path: "safety_stock_level", label: "Safety stock", type: "number" },
      { path: "min_order_qty", label: "Min order qty", type: "number" },
      { path: "max_order_qty", label: "Max order qty", type: "number" },
      { path: "default_supplier_id", label: "Default supplier", type: "select" },
      { path: "procurement_lead_time_days", label: "Procurement lead time (days)", type: "number" },
      { path: "promotion_reorder_boost", label: "Promotion reorder boost", type: "checkbox" },
      {
        path: "demand_forecast_notes",
        label: "Demand forecast notes",
        type: "textarea",
        colSpan: 2,
      },
    ],
  },
  {
    id: "quality",
    title: "Quality & compliance",
    fields: [
      { path: "quality_inspection_required", label: "Inspection required", type: "checkbox" },
      {
        path: "inspection_checklist_json",
        label: "Inspection checklist (JSON)",
        type: "textarea",
        colSpan: 2,
        showWhen: "quality_inspection_required",
      },
      {
        path: "expiry_alert_threshold_days",
        label: "Expiry alert (days before)",
        type: "number",
        showWhen: "expiry_date_flag",
      },
      { path: "hazardous_material_class", label: "Hazardous material class" },
      {
        path: "regulatory_compliance_codes",
        label: "Regulatory codes (MSDS, FDA, etc.)",
        type: "textarea",
        colSpan: 2,
      },
      { path: "attachments_json", label: "Attachments (JSON array)", type: "textarea", colSpan: 2 },
    ],
  },
  {
    id: "manufacturing",
    title: "Manufacturing / BOM",
    fields: [{ path: "manufacturing_item_sku", label: "Manufacturing item SKU", type: "select" }],
  },
]

export const INVENTORY_READ_ONLY_TABS = ["stock", "transactions", "audit"] as const
