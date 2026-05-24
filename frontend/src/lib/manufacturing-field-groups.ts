export type ManufacturingFieldType = "text" | "number" | "date" | "textarea" | "select"

export type ManufacturingFieldDef = {
  path: string
  label: string
  type?: ManufacturingFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type ManufacturingRepeatableKey =
  | "bom_lines"
  | "routing_operations"
  | "quality_templates"
  | "labor_skills"
  | "maintenance"
  | "approved_vendors"
  | "tooling"
  | "downtime_reasons"
  | "scrap_rework"

export type ManufacturingSectionDef = {
  id: string
  title: string
  description?: string
  fields: ManufacturingFieldDef[]
  isRepeatable?: boolean
  repeatableKey?: ManufacturingRepeatableKey
}

const P = "manufacturing_profile"

const statusOptions = [
  { value: "DRAFT", label: "Draft" },
  { value: "ACTIVE", label: "Active" },
  { value: "IN_PROGRESS", label: "In Progress" },
  { value: "COMPLETED", label: "Completed" },
  { value: "APPROVED", label: "Approved" },
  { value: "REJECTED", label: "Rejected" },
  { value: "CANCELLED", label: "Cancelled" },
]

const itemCategoryOptions = [
  { value: "", label: "— Select —" },
  { value: "finished_goods", label: "Finished Goods" },
  { value: "raw_materials", label: "Raw Materials" },
  { value: "semi_finished", label: "Semi-Finished Goods" },
  { value: "consumables", label: "Consumables" },
]

const uomOptions = [
  { value: "", label: "— Select —" },
  { value: "EA", label: "EA (Each)" },
  { value: "KG", label: "KG" },
  { value: "G", label: "G" },
  { value: "M", label: "M" },
  { value: "L", label: "L" },
  { value: "BOX", label: "BOX" },
  { value: "ROLL", label: "ROLL" },
]

const valuationOptions = [
  { value: "", label: "— Select —" },
  { value: "FIFO", label: "FIFO" },
  { value: "LIFO", label: "LIFO" },
  { value: "STANDARD", label: "Standard Cost" },
  { value: "MOVING_AVERAGE", label: "Moving Average" },
]

const productionStatusOptions = [
  { value: "", label: "— Select —" },
  { value: "RELEASED", label: "Released" },
  { value: "IN_PROGRESS", label: "In Progress" },
  { value: "COMPLETED", label: "Completed" },
  { value: "CLOSED", label: "Closed" },
]

const qualityStageOptions = [
  { value: "", label: "— Select —" },
  { value: "INBOUND", label: "Inbound" },
  { value: "IN_PROCESS", label: "In-Process" },
  { value: "FINAL", label: "Final" },
]

const yesNoOptions = [
  { value: "", label: "— Select —" },
  { value: "yes", label: "Yes" },
  { value: "no", label: "No" },
]

const abcOptions = [
  { value: "", label: "— Select —" },
  { value: "A", label: "A" },
  { value: "B", label: "B" },
  { value: "C", label: "C" },
]

export const coreRecordFields: ManufacturingFieldDef[] = [
  { path: "reference", label: "Reference / ID" },
  { path: "title", label: "Title / Display name" },
  { path: "status", label: "Status", type: "select", options: statusOptions },
  { path: "description", label: "Description", type: "textarea", colSpan: 2 },
]

// --- Repeatable row field defs ---

export const bomLineRowFields: ManufacturingFieldDef[] = [
  { path: "component_code", label: "Component code" },
  { path: "qty_per_assembly", label: "Qty per assembly" },
  { path: "scrap_pct", label: "Scrap %" },
  { path: "yield_pct", label: "Yield %" },
  { path: "alternate_group", label: "Alternate group" },
  { path: "ecn", label: "ECN" },
]

export const routingOperationRowFields: ManufacturingFieldDef[] = [
  { path: "sequence", label: "Sequence" },
  { path: "operation_name", label: "Operation name" },
  { path: "work_center", label: "Work center" },
  { path: "setup_time_minutes", label: "Setup time (min)" },
  { path: "run_time_minutes", label: "Run time (min)" },
  { path: "cycle_time_minutes", label: "Cycle time (min)" },
  { path: "requires_labor", label: "Requires labor", type: "select", options: yesNoOptions },
  { path: "requires_machine", label: "Requires machine", type: "select", options: yesNoOptions },
]

export const qualityTemplateRowFields: ManufacturingFieldDef[] = [
  { path: "characteristic", label: "Characteristic" },
  { path: "min_value", label: "Min value" },
  { path: "max_value", label: "Max value" },
  { path: "tolerance", label: "Tolerance" },
  { path: "defect_code", label: "Defect code" },
]

export const laborSkillRowFields: ManufacturingFieldDef[] = [
  { path: "employee_ref", label: "Employee ref" },
  { path: "skill", label: "Skill" },
  { path: "availability", label: "Availability" },
  { path: "notes", label: "Notes" },
]

export const maintenanceRowFields: ManufacturingFieldDef[] = [
  { path: "machine_ref", label: "Machine ref" },
  { path: "scheduled_date", label: "Scheduled date", type: "date" },
  { path: "maintenance_type", label: "Maintenance type" },
  { path: "notes", label: "Notes" },
]

export const approvedVendorRowFields: ManufacturingFieldDef[] = [
  { path: "supplier_code", label: "Supplier code" },
  { path: "supplier_name", label: "Supplier name" },
  { path: "lead_time_days", label: "Lead time (days)" },
  { path: "contract_ref", label: "Contract ref" },
  { path: "price_terms", label: "Price / terms" },
]

export const toolingRowFields: ManufacturingFieldDef[] = [
  { path: "code", label: "Tooling code" },
  { path: "name", label: "Name" },
  { path: "linked_operation", label: "Linked operation" },
  { path: "lifecycle_status", label: "Lifecycle status" },
]

export const downtimeReasonRowFields: ManufacturingFieldDef[] = [
  { path: "reason_code", label: "Reason code" },
  { path: "description", label: "Description" },
  { path: "category", label: "Category" },
]

export const scrapReworkRowFields: ManufacturingFieldDef[] = [
  { path: "date", label: "Date", type: "date" },
  { path: "quantity", label: "Quantity" },
  { path: "reason", label: "Reason" },
  { path: "disposition", label: "Disposition" },
]

export const REPEATABLE_FIELD_MAP: Record<ManufacturingRepeatableKey, ManufacturingFieldDef[]> = {
  bom_lines: bomLineRowFields,
  routing_operations: routingOperationRowFields,
  quality_templates: qualityTemplateRowFields,
  labor_skills: laborSkillRowFields,
  maintenance: maintenanceRowFields,
  approved_vendors: approvedVendorRowFields,
  tooling: toolingRowFields,
  downtime_reasons: downtimeReasonRowFields,
  scrap_rework: scrapReworkRowFields,
}

export const REPEATABLE_ARRAY_PATH: Record<ManufacturingRepeatableKey, string> = {
  bom_lines: `${P}.master_data.bom.lines`,
  routing_operations: `${P}.master_data.routing.operations`,
  quality_templates: `${P}.quality.templates`,
  labor_skills: `${P}.resources.labor_skills`,
  maintenance: `${P}.resources.maintenance`,
  approved_vendors: `${P}.supplier.approved_vendors`,
  tooling: `${P}.other.tooling`,
  downtime_reasons: `${P}.other.downtime_reasons`,
  scrap_rework: `${P}.other.scrap_rework`,
}

export const REPEATABLE_LABELS: Record<ManufacturingRepeatableKey, string> = {
  bom_lines: "BOM line",
  routing_operations: "Routing operation",
  quality_templates: "Test / inspection template",
  labor_skills: "Labor skill",
  maintenance: "Maintenance schedule",
  approved_vendors: "Approved vendor",
  tooling: "Tooling / fixture",
  downtime_reasons: "Downtime reason",
  scrap_rework: "Scrap / rework entry",
}

// --- Tab sections ---

const itemMasterFields: ManufacturingFieldDef[] = [
  {
    path: `${P}.master_data.item_master.item_code`,
    label: "Item code",
    placeholder: "SKU from Inventory module",
  },
  { path: `${P}.master_data.item_master.description`, label: "Description", colSpan: 2 },
  { path: `${P}.master_data.item_master.specifications`, label: "Specifications", type: "textarea", colSpan: 2 },
  { path: `${P}.master_data.item_master.uom`, label: "UOM", type: "select", options: uomOptions },
  {
    path: `${P}.master_data.item_master.item_category`,
    label: "Item category",
    type: "select",
    options: itemCategoryOptions,
  },
  { path: `${P}.master_data.item_master.product_category`, label: "Product category" },
  { path: `${P}.master_data.item_master.product_group`, label: "Product group" },
  { path: `${P}.master_data.item_master.hierarchy`, label: "Product hierarchy" },
  { path: `${P}.master_data.item_master.gross_weight`, label: "Gross weight" },
  { path: `${P}.master_data.item_master.net_weight`, label: "Net weight" },
  { path: `${P}.master_data.item_master.length`, label: "Length" },
  { path: `${P}.master_data.item_master.width`, label: "Width" },
  { path: `${P}.master_data.item_master.height`, label: "Height" },
  { path: `${P}.master_data.item_master.volume`, label: "Volume" },
  { path: `${P}.master_data.item_master.shelf_life_days`, label: "Shelf life (days)" },
  { path: `${P}.master_data.item_master.expiry_details`, label: "Expiry details", type: "textarea", colSpan: 2 },
  { path: `${P}.master_data.item_master.default_warehouse`, label: "Default warehouse" },
  { path: `${P}.master_data.item_master.default_location`, label: "Default location" },
]

const bomHeaderFields: ManufacturingFieldDef[] = [
  { path: `${P}.master_data.bom.bom_number`, label: "BOM number" },
  { path: `${P}.master_data.bom.version`, label: "Version" },
  { path: `${P}.master_data.bom.scrap_pct`, label: "Scrap %" },
  { path: `${P}.master_data.bom.yield_rate`, label: "Yield rate" },
  { path: `${P}.master_data.bom.alternate_bom_ref`, label: "Alternate BOM ref" },
  { path: `${P}.master_data.bom.ecn`, label: "Engineering change (ECN)" },
  { path: `${P}.master_data.bom.effective_from`, label: "Effective from", type: "date" },
  { path: `${P}.master_data.bom.effective_to`, label: "Effective to", type: "date" },
]

const routingHeaderFields: ManufacturingFieldDef[] = [
  { path: `${P}.master_data.routing.routing_code`, label: "Routing code" },
  { path: `${P}.master_data.routing.routing_name`, label: "Routing name" },
  { path: `${P}.master_data.routing.parent_sku`, label: "Parent SKU" },
  { path: `${P}.master_data.routing.default_work_center`, label: "Default work center" },
  { path: `${P}.master_data.routing.production_version`, label: "Production version" },
  { path: `${P}.master_data.routing.notes`, label: "Routing notes", type: "textarea", colSpan: 2 },
]

const inventoryFields: ManufacturingFieldDef[] = [
  { path: `${P}.inventory.on_hand`, label: "On-hand qty" },
  { path: `${P}.inventory.available`, label: "Available qty" },
  { path: `${P}.inventory.reserved`, label: "Reserved qty" },
  { path: `${P}.inventory.in_transit`, label: "In-transit qty" },
  { path: `${P}.inventory.lot_tracking`, label: "Lot tracking", type: "select", options: yesNoOptions },
  { path: `${P}.inventory.serial_tracking`, label: "Serial tracking", type: "select", options: yesNoOptions },
  { path: `${P}.inventory.bin_location`, label: "Bin / location" },
  { path: `${P}.inventory.min_level`, label: "Minimum level" },
  { path: `${P}.inventory.max_level`, label: "Maximum level" },
  { path: `${P}.inventory.reorder_level`, label: "Reorder level" },
  { path: `${P}.inventory.abc_class`, label: "ABC classification", type: "select", options: abcOptions },
  {
    path: `${P}.inventory.valuation_method`,
    label: "Valuation method",
    type: "select",
    options: valuationOptions,
  },
]

const planningFields: ManufacturingFieldDef[] = [
  { path: `${P}.planning.po_reference`, label: "Production order ref (informational)" },
  { path: `${P}.planning.order_quantity`, label: "Order quantity" },
  { path: `${P}.planning.due_date`, label: "Due date", type: "date" },
  { path: `${P}.planning.priority`, label: "Priority" },
  { path: `${P}.planning.bom_version`, label: "BOM version used" },
  { path: `${P}.planning.routing_version`, label: "Routing version used" },
  { path: `${P}.planning.planned_consumption`, label: "Planned consumption", type: "textarea", colSpan: 2 },
  { path: `${P}.planning.actual_consumption`, label: "Actual consumption", type: "textarea", colSpan: 2 },
  {
    path: `${P}.planning.production_status`,
    label: "Production status",
    type: "select",
    options: productionStatusOptions,
  },
  { path: `${P}.planning.demand_forecast_ref`, label: "Demand forecast ref" },
  { path: `${P}.planning.sales_order_ref`, label: "Sales order ref (MRP)" },
  { path: `${P}.planning.mrp_horizon_days`, label: "MRP horizon (days)" },
  { path: `${P}.planning.mps_code`, label: "MPS schedule code" },
  { path: `${P}.planning.calendar_code`, label: "Production calendar" },
  { path: `${P}.planning.order_creation_mode`, label: "Order creation mode" },
  { path: `${P}.planning.last_mrp_run`, label: "Last MRP run ref" },
]

const qualityScalarFields: ManufacturingFieldDef[] = [
  { path: `${P}.quality.plan_code`, label: "Inspection plan code" },
  { path: `${P}.quality.stage`, label: "Stage", type: "select", options: qualityStageOptions },
  {
    path: `${P}.quality.inspection_parameters`,
    label: "Inspection parameters",
    type: "textarea",
    colSpan: 2,
  },
  { path: `${P}.quality.checkpoints`, label: "Checkpoints", type: "textarea", colSpan: 2 },
  { path: `${P}.quality.acceptance_criteria`, label: "Acceptance criteria / tolerances", type: "textarea", colSpan: 2 },
  { path: `${P}.quality.coa_required`, label: "COA required", type: "select", options: yesNoOptions },
  { path: `${P}.quality.ncr_reference`, label: "NCR reference" },
  { path: `${P}.quality.capa_reference`, label: "CAPA reference" },
]

const costingFields: ManufacturingFieldDef[] = [
  { path: `${P}.costing.standard_cost`, label: "Standard cost" },
  { path: `${P}.costing.variable_cost`, label: "Variable cost" },
  { path: `${P}.costing.fixed_cost`, label: "Fixed cost" },
  { path: `${P}.costing.material_cost`, label: "Material cost" },
  { path: `${P}.costing.labor_cost`, label: "Labor cost" },
  { path: `${P}.costing.overhead_cost`, label: "Overhead cost" },
  { path: `${P}.costing.cost_center`, label: "Cost center" },
  { path: `${P}.costing.allocation_rules`, label: "Cost allocation rules", type: "textarea", colSpan: 2 },
  { path: `${P}.costing.wip_tracking_notes`, label: "WIP tracking notes", type: "textarea", colSpan: 2 },
]

const resourcesScalarFields: ManufacturingFieldDef[] = [
  { path: `${P}.resources.work_center_code`, label: "Work center code" },
  { path: `${P}.resources.capacity`, label: "Capacity" },
  { path: `${P}.resources.efficiency_pct`, label: "Efficiency %" },
  { path: `${P}.resources.downtime_notes`, label: "Downtime notes", type: "textarea", colSpan: 2 },
  { path: `${P}.resources.shift_calendar`, label: "Shift / calendar", type: "textarea", colSpan: 2 },
]

const supplierScalarFields: ManufacturingFieldDef[] = [
  { path: `${P}.supplier.purchase_lead_time`, label: "Purchase lead time" },
  { path: `${P}.supplier.contract_pricing`, label: "Contract / pricing" },
  { path: `${P}.supplier.terms`, label: "Terms", type: "textarea", colSpan: 2 },
  { path: `${P}.supplier.pr_po_links`, label: "PR / PO links to production", type: "textarea", colSpan: 2 },
]

const customerSalesFields: ManufacturingFieldDef[] = [
  { path: `${P}.customer_sales.customer_specific_bom`, label: "Customer-specific BOM / formulation", type: "textarea", colSpan: 2 },
  { path: `${P}.customer_sales.packing_labeling`, label: "Special packing / labeling", type: "textarea", colSpan: 2 },
  { path: `${P}.customer_sales.order_history_notes`, label: "Order history notes", type: "textarea", colSpan: 2 },
  { path: `${P}.customer_sales.delivery_performance`, label: "Delivery performance", type: "textarea", colSpan: 2 },
  { path: `${P}.customer_sales.customer_name`, label: "Customer" },
  { path: `${P}.customer_sales.config_code`, label: "BOM configuration code" },
]

const complianceFields: ManufacturingFieldDef[] = [
  { path: `${P}.compliance.forward_traceability`, label: "Forward traceability", type: "textarea", colSpan: 2 },
  { path: `${P}.compliance.backward_traceability`, label: "Backward traceability", type: "textarea", colSpan: 2 },
  { path: `${P}.compliance.regulatory_codes`, label: "Regulatory compliance (ISO, FDA, REACH, etc.)", type: "textarea", colSpan: 2 },
  { path: `${P}.compliance.country_of_origin`, label: "Country of origin" },
  { path: `${P}.compliance.hs_code`, label: "HS code" },
  { path: `${P}.compliance.sustainability_notes`, label: "Sustainability notes", type: "textarea", colSpan: 2 },
  { path: `${P}.compliance.carbon_footprint`, label: "Carbon footprint data", type: "textarea", colSpan: 2 },
]

const otherScalarFields: ManufacturingFieldDef[] = [
  { path: `${P}.other.ecn_eco_number`, label: "ECN / ECO number" },
  { path: `${P}.other.ecn_title`, label: "ECN / ECO title" },
  { path: `${P}.other.ecn_effective_date`, label: "ECN effective date", type: "date" },
  { path: `${P}.other.labor_booking_standard`, label: "Labor time — standard" },
  { path: `${P}.other.labor_booking_actual`, label: "Labor time — actual" },
]

export type ManufacturingMasterTab = {
  id: string
  label: string
  sections: ManufacturingSectionDef[]
}

export const MANUFACTURING_MASTER_TABS: ManufacturingMasterTab[] = [
  {
    id: "master_data",
    label: "1. Master Data",
    sections: [
      { id: "item_master", title: "Item master", fields: itemMasterFields },
      { id: "bom_header", title: "Bill of materials (header)", fields: bomHeaderFields },
      {
        id: "bom_lines",
        title: "BOM components (multi-level lines)",
        description: "Quantity per assembly, scrap, yield, alternates, and ECN per line.",
        fields: [],
        isRepeatable: true,
        repeatableKey: "bom_lines",
      },
      { id: "routing_header", title: "Routing / process sheet (header)", fields: routingHeaderFields },
      {
        id: "routing_ops",
        title: "Routing operations",
        description: "Sequence, work centers, standard times, labor and machine requirements.",
        fields: [],
        isRepeatable: true,
        repeatableKey: "routing_operations",
      },
    ],
  },
  {
    id: "inventory",
    label: "2. Inventory",
    sections: [{ id: "inventory", title: "Inventory & warehouse", fields: inventoryFields }],
  },
  {
    id: "planning",
    label: "3. Planning",
    sections: [{ id: "planning", title: "Production planning & control", fields: planningFields }],
  },
  {
    id: "quality",
    label: "4. Quality",
    sections: [
      { id: "quality_scalar", title: "Quality management", fields: qualityScalarFields },
      {
        id: "quality_templates",
        title: "Test / inspection templates",
        fields: [],
        isRepeatable: true,
        repeatableKey: "quality_templates",
      },
    ],
  },
  {
    id: "costing",
    label: "5. Costing",
    sections: [{ id: "costing", title: "Costing & finance", fields: costingFields }],
  },
  {
    id: "resources",
    label: "6. Resources",
    sections: [
      { id: "resources_scalar", title: "Work center & capacity", fields: resourcesScalarFields },
      {
        id: "labor_skills",
        title: "Labor / employee skills",
        fields: [],
        isRepeatable: true,
        repeatableKey: "labor_skills",
      },
      {
        id: "maintenance",
        title: "Machine maintenance schedules",
        fields: [],
        isRepeatable: true,
        repeatableKey: "maintenance",
      },
    ],
  },
  {
    id: "supplier",
    label: "7. Supplier",
    sections: [
      { id: "supplier_scalar", title: "Purchase information", fields: supplierScalarFields },
      {
        id: "approved_vendors",
        title: "Approved vendor list",
        fields: [],
        isRepeatable: true,
        repeatableKey: "approved_vendors",
      },
    ],
  },
  {
    id: "customer_sales",
    label: "8. Customer",
    sections: [{ id: "customer_sales", title: "Customer & sales", fields: customerSalesFields }],
  },
  {
    id: "compliance",
    label: "9. Compliance",
    sections: [{ id: "compliance", title: "Compliance & traceability", fields: complianceFields }],
  },
  {
    id: "other",
    label: "10. Other",
    sections: [
      { id: "other_scalar", title: "Engineering & labor", fields: otherScalarFields },
      {
        id: "tooling",
        title: "Tooling & fixtures",
        fields: [],
        isRepeatable: true,
        repeatableKey: "tooling",
      },
      {
        id: "downtime",
        title: "Production downtime reasons",
        fields: [],
        isRepeatable: true,
        repeatableKey: "downtime_reasons",
      },
      {
        id: "scrap_rework",
        title: "Scrap & rework tracking",
        fields: [],
        isRepeatable: true,
        repeatableKey: "scrap_rework",
      },
    ],
  },
]

export const MANUFACTURING_FEATURE_OPTIONS = [
  { value: "production_orders", label: "Production Orders" },
  { value: "bom_routing", label: "BOM & Routing" },
  { value: "shop_floor", label: "Shop Floor Control" },
  { value: "capacity_planning", label: "Capacity Planning" },
  { value: "quality_management", label: "Quality Management" },
  { value: "make_to_order", label: "Make-to-Order" },
  { value: "make_to_stock", label: "Make-to-Stock" },
  { value: "engineer_to_order", label: "Engineer-to-Order" },
] as const
