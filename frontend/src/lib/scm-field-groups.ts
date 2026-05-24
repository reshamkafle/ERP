export type ScmFieldType = "text" | "number" | "date" | "textarea" | "select" | "checkbox"

export type ScmFieldDef = {
  path: string
  label: string
  type?: ScmFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type ScmSectionDef = {
  id: string
  title: string
  description?: string
  fields: ScmFieldDef[]
  isLineItems?: boolean
}

const statusOptions = [
  { value: "DRAFT", label: "Draft" },
  { value: "PENDING", label: "Pending" },
  { value: "APPROVED", label: "Approved" },
  { value: "IN_PROGRESS", label: "In progress" },
  { value: "COMPLETED", label: "Completed" },
  { value: "REJECTED", label: "Rejected" },
  { value: "CANCELLED", label: "Cancelled" },
]

const valuationOptions = [
  { value: "", label: "—" },
  { value: "FIFO", label: "FIFO" },
  { value: "LIFO", label: "LIFO" },
  { value: "AVERAGE", label: "Moving average" },
  { value: "STANDARD", label: "Standard cost" },
]

const abcOptions = [
  { value: "", label: "—" },
  { value: "A", label: "A" },
  { value: "B", label: "B" },
  { value: "C", label: "C" },
]

const transportModeOptions = [
  { value: "", label: "—" },
  { value: "ROAD", label: "Road" },
  { value: "SEA", label: "Sea" },
  { value: "AIR", label: "Air" },
  { value: "RAIL", label: "Rail" },
]

const exceptionOptions = [
  { value: "", label: "—" },
  { value: "STOCKOUT", label: "Stockout" },
  { value: "DELAY", label: "Delay" },
  { value: "OVERSTOCK", label: "Overstock" },
]

export const coreRecordFields: ScmFieldDef[] = [
  { path: "reference", label: "Record reference" },
  { path: "title", label: "Title / summary" },
  { path: "status", label: "Status", type: "select", options: statusOptions },
  { path: "description", label: "Description / notes", type: "textarea", colSpan: 2 },
  { path: "party_name", label: "Party / counterparty" },
  { path: "amount", label: "Amount", type: "number" },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "start_date", label: "Start / effective date", type: "date" },
  { path: "end_date", label: "End / due date", type: "date" },
]

export const masterDataFields: ScmFieldDef[] = [
  { path: "master_data.item_sku", label: "Item / product code (SKU)" },
  { path: "master_data.item_name", label: "Item description" },
  { path: "master_data.item_type", label: "Item classification (raw, finished, etc.)" },
  { path: "master_data.primary_uom", label: "Primary UOM" },
  { path: "master_data.gross_weight", label: "Gross weight", type: "number" },
  { path: "master_data.net_weight", label: "Net weight", type: "number" },
  { path: "master_data.dimensions", label: "Dimensions (L×W×H)", colSpan: 2 },
  { path: "master_data.shelf_life_days", label: "Shelf life (days)", type: "number" },
  { path: "master_data.bom_version", label: "BOM version" },
  { path: "master_data.bom_parent_sku", label: "BOM parent SKU" },
  { path: "master_data.supplier_code", label: "Supplier / vendor code" },
  { path: "master_data.supplier_lead_time_days", label: "Supplier lead time (days)", type: "number" },
  {
    path: "master_data.approved_vendor",
    label: "Approved vendor list",
    type: "select",
    options: [
      { value: "", label: "—" },
      { value: "YES", label: "Yes" },
      { value: "NO", label: "No" },
    ],
  },
  { path: "master_data.customer_code", label: "Customer code" },
  { path: "master_data.ship_to_address", label: "Ship-to address", type: "textarea", colSpan: 2 },
  { path: "master_data.credit_terms", label: "Credit terms" },
  { path: "master_data.service_level_agreement", label: "Service level agreement (SLA)" },
  { path: "master_data.warehouse_code", label: "Warehouse / plant code" },
  { path: "master_data.bin_location", label: "Storage bin / location" },
  { path: "master_data.geo_region", label: "Geographic region" },
]

export const inventoryFields: ScmFieldDef[] = [
  { path: "inventory.on_hand", label: "On-hand qty", type: "number" },
  { path: "inventory.available", label: "Available qty", type: "number" },
  { path: "inventory.reserved", label: "Reserved qty", type: "number" },
  { path: "inventory.in_transit", label: "In-transit qty", type: "number" },
  {
    path: "inventory.valuation_method",
    label: "Valuation method",
    type: "select",
    options: valuationOptions,
  },
  { path: "inventory.lot_number", label: "Lot number" },
  { path: "inventory.serial_number", label: "Serial number" },
  { path: "inventory.safety_stock", label: "Safety stock level", type: "number" },
  { path: "inventory.reorder_point", label: "Reorder point", type: "number" },
  { path: "inventory.min_stock", label: "Minimum stock", type: "number" },
  { path: "inventory.max_stock", label: "Maximum stock", type: "number" },
  { path: "inventory.abc_class", label: "ABC classification", type: "select", options: abcOptions },
  { path: "inventory.aging_bucket", label: "Inventory aging bucket" },
  { path: "inventory.last_movement_date", label: "Last movement date", type: "date" },
]

export const procurementFields: ScmFieldDef[] = [
  { path: "procurement.pr_reference", label: "Purchase requisition ref" },
  { path: "procurement.po_reference", label: "Purchase order ref" },
  { path: "procurement.contract_reference", label: "Supplier contract ref" },
  {
    path: "procurement.blanket_order",
    label: "Blanket order",
    type: "select",
    options: [
      { value: "", label: "—" },
      { value: "YES", label: "Yes" },
      { value: "NO", label: "No" },
    ],
  },
  { path: "procurement.rfq_reference", label: "RFQ reference" },
  { path: "procurement.quotation_history", label: "Quotation / RFQ history", type: "textarea", colSpan: 2 },
  { path: "procurement.procurement_schedule", label: "Procurement schedule" },
  { path: "procurement.lead_time_days", label: "Lead time (days)", type: "number" },
  { path: "procurement.pricing_conditions", label: "Pricing conditions summary", type: "textarea", colSpan: 2 },
]

export const demandSalesFields: ScmFieldDef[] = [
  { path: "demand_sales.sales_order_ref", label: "Sales order reference" },
  { path: "demand_sales.short_term_forecast_qty", label: "Short-term forecast qty", type: "number" },
  { path: "demand_sales.long_term_forecast_qty", label: "Long-term forecast qty", type: "number" },
  { path: "demand_sales.historical_demand_notes", label: "Historical demand / patterns", type: "textarea", colSpan: 2 },
  { path: "demand_sales.backlog_qty", label: "Order backlog qty", type: "number" },
  { path: "demand_sales.delivery_schedule", label: "Delivery schedule" },
  { path: "demand_sales.promotion_adjustment_pct", label: "Promotion / seasonal adjustment %", type: "number" },
]

export const productionFields: ScmFieldDef[] = [
  { path: "production.mrp_run_ref", label: "MRP run reference" },
  { path: "production.planned_order_qty", label: "Planned order qty", type: "number" },
  { path: "production.production_order_ref", label: "Production order ref" },
  { path: "production.schedule_start_date", label: "Schedule start date", type: "date" },
  { path: "production.schedule_end_date", label: "Schedule end date", type: "date" },
  { path: "production.wip_status", label: "WIP status" },
  { path: "production.wip_qty", label: "WIP quantity", type: "number" },
  { path: "production.routing_id", label: "Routing ID" },
  { path: "production.work_center", label: "Work center" },
]

export const logisticsFields: ScmFieldDef[] = [
  { path: "logistics.ship_schedule", label: "Shipping / delivery schedule" },
  { path: "logistics.carrier", label: "Carrier" },
  { path: "logistics.freight_forwarder", label: "Freight forwarder" },
  { path: "logistics.route", label: "Transportation route" },
  { path: "logistics.transport_mode", label: "Mode", type: "select", options: transportModeOptions },
  { path: "logistics.freight_cost", label: "Freight cost", type: "number" },
  { path: "logistics.tracking_number", label: "Tracking number" },
  { path: "logistics.shipment_status", label: "Shipment status" },
  { path: "logistics.incoterms", label: "Incoterms" },
  { path: "logistics.customs_doc_ref", label: "Customs documentation ref" },
]

export const warehouseFields: ScmFieldDef[] = [
  { path: "warehouse.putaway_strategy", label: "Put-away strategy" },
  { path: "warehouse.picking_strategy", label: "Picking strategy" },
  { path: "warehouse.packing_strategy", label: "Packing strategy" },
  { path: "warehouse.layout_zone", label: "Warehouse layout / zone" },
  { path: "warehouse.handling_unit", label: "Handling unit" },
  { path: "warehouse.packaging_type", label: "Packaging type" },
  { path: "warehouse.cycle_count_date", label: "Cycle count date", type: "date" },
  { path: "warehouse.physical_variance_qty", label: "Physical inventory variance qty", type: "number" },
]

export const financialFields: ScmFieldDef[] = [
  { path: "financial.purchase_price", label: "Purchase price", type: "number" },
  { path: "financial.landed_cost", label: "Landed cost", type: "number" },
  { path: "financial.transfer_price", label: "Transfer pricing", type: "number" },
  { path: "financial.freight_logistics_cost", label: "Freight / logistics cost", type: "number" },
  { path: "financial.ap_reference", label: "Accounts payable ref" },
  { path: "financial.ar_reference", label: "Accounts receivable ref" },
  { path: "financial.budget_reference", label: "Budget reference" },
  { path: "financial.cost_center", label: "Cost center" },
]

export const complianceFields: ScmFieldDef[] = [
  { path: "compliance.country_of_origin", label: "Country of origin" },
  { path: "compliance.certifications", label: "Certifications", type: "textarea", colSpan: 2 },
  { path: "compliance.inspection_result", label: "Quality inspection result" },
  { path: "compliance.coa_reference", label: "Certificate of analysis (COA) ref" },
  { path: "compliance.esg_notes", label: "Sustainability / ESG notes", type: "textarea", colSpan: 2 },
  { path: "compliance.supplier_risk_score", label: "Supplier risk score", type: "number" },
  { path: "compliance.disruption_alert", label: "Risk / disruption alert", type: "textarea", colSpan: 2 },
]

export const analyticsFields: ScmFieldDef[] = [
  { path: "analytics.on_time_delivery_pct", label: "On-time delivery %", type: "number" },
  { path: "analytics.fill_rate_pct", label: "Fill rate %", type: "number" },
  { path: "analytics.inventory_turnover", label: "Inventory turnover", type: "number" },
  { path: "analytics.order_cycle_time_days", label: "Order cycle time (days)", type: "number" },
  { path: "analytics.supplier_performance_score", label: "Supplier performance score", type: "number" },
  {
    path: "analytics.dashboard_alert",
    label: "Dashboard alert",
    type: "select",
    options: [
      { value: "", label: "—" },
      { value: "YES", label: "Yes" },
      { value: "NO", label: "No" },
    ],
  },
  {
    path: "analytics.exception_type",
    label: "Exception type",
    type: "select",
    options: exceptionOptions,
  },
  { path: "analytics.exception_notes", label: "Exception notes", type: "textarea", colSpan: 2 },
]

export const scmLineItemFields: ScmFieldDef[] = [
  { path: "item_code", label: "Item code" },
  { path: "description", label: "Description" },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "uom", label: "UOM" },
  { path: "notes", label: "Notes", type: "textarea", colSpan: 2 },
]

export const SCM_FEATURE_OPTIONS = [
  { value: "demand_planning", label: "Demand Planning" },
  { value: "forecasting", label: "Forecasting" },
  { value: "logistics", label: "Logistics Management" },
  { value: "transportation", label: "Transportation" },
  { value: "supplier_relationship", label: "Supplier Relationship" },
] as const

export const SCM_PHASE1_FEATURES: Set<string> = new Set(SCM_FEATURE_OPTIONS.map((o) => o.value))

/** All category tabs shown on every SCM record. */
export const SCM_CATEGORY_SECTIONS: ScmSectionDef[] = [
  { id: "master_data", title: "Master Data", description: "References to item, BOM, supplier, customer, and location masters.", fields: masterDataFields },
  { id: "inventory", title: "Inventory & Stock", description: "Stock levels, valuation, lot/serial, and replenishment parameters.", fields: inventoryFields },
  { id: "procurement", title: "Procurement & Sourcing", description: "PR/PO, contracts, RFQ, and procurement schedules.", fields: procurementFields },
  { id: "demand_sales", title: "Demand & Sales", description: "Forecasts, backlog, and promotional adjustments.", fields: demandSalesFields },
  { id: "production", title: "Production & Planning", description: "MRP, production orders, WIP, and routings.", fields: productionFields },
  { id: "logistics", title: "Logistics & Transportation", description: "Carriers, routes, tracking, and international terms.", fields: logisticsFields },
  { id: "warehouse", title: "Warehouse Management", description: "Put-away, picking, packing, and cycle counting.", fields: warehouseFields },
  { id: "financial", title: "Financial & Cost", description: "Pricing, landed cost, and cost center allocation.", fields: financialFields },
  { id: "compliance", title: "Compliance & Quality", description: "Regulatory, quality, ESG, and supplier risk data.", fields: complianceFields },
  { id: "analytics", title: "Analytics & Performance", description: "KPIs, alerts, and exception reporting.", fields: analyticsFields },
]

export function getScmSectionsForFeature(_featureCode: string): ScmSectionDef[] {
  return [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    ...SCM_CATEGORY_SECTIONS,
    {
      id: "lines",
      title: "Line items",
      description: "Optional detail lines (demand, shipment, or planning lines).",
      fields: scmLineItemFields,
      isLineItems: true,
    },
  ]
}

export const SCM_LINKED_ROUTES: { label: string; to: string }[] = [
  { label: "Inventory", to: "/inventory" },
  { label: "Suppliers", to: "/suppliers" },
  { label: "Warehouses", to: "/warehouses" },
  { label: "Locations", to: "/locations" },
  { label: "BOM", to: "/bom" },
  { label: "Purchases", to: "/purchases" },
  { label: "Customers", to: "/customers" },
  { label: "Sales", to: "/sales" },
  { label: "Reports", to: "/reports" },
]
