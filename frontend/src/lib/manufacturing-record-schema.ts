import { z } from "zod"

import type { ModuleRecord } from "@/types/module"

const optionalStr = z.string()

export const MANUFACTURING_MODULE_CODE = "manufacturing"

export const MANUFACTURING_STATUS_OPTIONS = [
  "DRAFT",
  "ACTIVE",
  "IN_PROGRESS",
  "COMPLETED",
  "APPROVED",
  "REJECTED",
  "CANCELLED",
] as const

// --- Repeatable row schemas ---

export const bomLineRowSchema = z.object({
  component_code: optionalStr,
  qty_per_assembly: optionalStr,
  scrap_pct: optionalStr,
  yield_pct: optionalStr,
  alternate_group: optionalStr,
  ecn: optionalStr,
})

export const routingOperationRowSchema = z.object({
  sequence: optionalStr,
  operation_name: optionalStr,
  work_center: optionalStr,
  setup_time_minutes: optionalStr,
  run_time_minutes: optionalStr,
  cycle_time_minutes: optionalStr,
  requires_labor: optionalStr,
  requires_machine: optionalStr,
})

export const qualityTemplateRowSchema = z.object({
  characteristic: optionalStr,
  min_value: optionalStr,
  max_value: optionalStr,
  tolerance: optionalStr,
  defect_code: optionalStr,
})

export const laborSkillRowSchema = z.object({
  employee_ref: optionalStr,
  skill: optionalStr,
  availability: optionalStr,
  notes: optionalStr,
})

export const maintenanceRowSchema = z.object({
  machine_ref: optionalStr,
  scheduled_date: optionalStr,
  maintenance_type: optionalStr,
  notes: optionalStr,
})

export const approvedVendorRowSchema = z.object({
  supplier_code: optionalStr,
  supplier_name: optionalStr,
  lead_time_days: optionalStr,
  contract_ref: optionalStr,
  price_terms: optionalStr,
})

export const toolingRowSchema = z.object({
  code: optionalStr,
  name: optionalStr,
  linked_operation: optionalStr,
  lifecycle_status: optionalStr,
})

export const downtimeReasonRowSchema = z.object({
  reason_code: optionalStr,
  description: optionalStr,
  category: optionalStr,
})

export const scrapReworkRowSchema = z.object({
  date: optionalStr,
  quantity: optionalStr,
  reason: optionalStr,
  disposition: optionalStr,
})

// --- Profile section schemas ---

const itemMasterSchema = z.object({
  item_code: optionalStr,
  description: optionalStr,
  specifications: optionalStr,
  uom: optionalStr,
  item_category: optionalStr,
  product_category: optionalStr,
  product_group: optionalStr,
  hierarchy: optionalStr,
  gross_weight: optionalStr,
  net_weight: optionalStr,
  length: optionalStr,
  width: optionalStr,
  height: optionalStr,
  volume: optionalStr,
  shelf_life_days: optionalStr,
  expiry_details: optionalStr,
  default_warehouse: optionalStr,
  default_location: optionalStr,
})

const bomHeaderSchema = z.object({
  bom_number: optionalStr,
  version: optionalStr,
  scrap_pct: optionalStr,
  yield_rate: optionalStr,
  alternate_bom_ref: optionalStr,
  ecn: optionalStr,
  effective_from: optionalStr,
  effective_to: optionalStr,
  lines: z.array(bomLineRowSchema),
})

const routingHeaderSchema = z.object({
  routing_code: optionalStr,
  routing_name: optionalStr,
  parent_sku: optionalStr,
  default_work_center: optionalStr,
  production_version: optionalStr,
  notes: optionalStr,
  operations: z.array(routingOperationRowSchema),
})

const masterDataSchema = z.object({
  item_master: itemMasterSchema,
  bom: bomHeaderSchema,
  routing: routingHeaderSchema,
})

const inventorySchema = z.object({
  on_hand: optionalStr,
  available: optionalStr,
  reserved: optionalStr,
  in_transit: optionalStr,
  lot_tracking: optionalStr,
  serial_tracking: optionalStr,
  bin_location: optionalStr,
  min_level: optionalStr,
  max_level: optionalStr,
  reorder_level: optionalStr,
  abc_class: optionalStr,
  valuation_method: optionalStr,
})

const planningSchema = z.object({
  po_reference: optionalStr,
  order_quantity: optionalStr,
  due_date: optionalStr,
  priority: optionalStr,
  bom_version: optionalStr,
  routing_version: optionalStr,
  planned_consumption: optionalStr,
  actual_consumption: optionalStr,
  production_status: optionalStr,
  demand_forecast_ref: optionalStr,
  sales_order_ref: optionalStr,
  mrp_horizon_days: optionalStr,
  mps_code: optionalStr,
  calendar_code: optionalStr,
  order_creation_mode: optionalStr,
  last_mrp_run: optionalStr,
})

const qualitySchema = z.object({
  inspection_parameters: optionalStr,
  checkpoints: optionalStr,
  acceptance_criteria: optionalStr,
  coa_required: optionalStr,
  ncr_reference: optionalStr,
  capa_reference: optionalStr,
  plan_code: optionalStr,
  stage: optionalStr,
  templates: z.array(qualityTemplateRowSchema),
})

const costingSchema = z.object({
  standard_cost: optionalStr,
  variable_cost: optionalStr,
  fixed_cost: optionalStr,
  material_cost: optionalStr,
  labor_cost: optionalStr,
  overhead_cost: optionalStr,
  cost_center: optionalStr,
  allocation_rules: optionalStr,
  wip_tracking_notes: optionalStr,
})

const resourcesSchema = z.object({
  work_center_code: optionalStr,
  capacity: optionalStr,
  efficiency_pct: optionalStr,
  downtime_notes: optionalStr,
  shift_calendar: optionalStr,
  labor_skills: z.array(laborSkillRowSchema),
  maintenance: z.array(maintenanceRowSchema),
})

const supplierSchema = z.object({
  purchase_lead_time: optionalStr,
  contract_pricing: optionalStr,
  terms: optionalStr,
  pr_po_links: optionalStr,
  approved_vendors: z.array(approvedVendorRowSchema),
})

const customerSalesSchema = z.object({
  customer_specific_bom: optionalStr,
  packing_labeling: optionalStr,
  order_history_notes: optionalStr,
  delivery_performance: optionalStr,
  customer_name: optionalStr,
  config_code: optionalStr,
})

const complianceSchema = z.object({
  forward_traceability: optionalStr,
  backward_traceability: optionalStr,
  regulatory_codes: optionalStr,
  country_of_origin: optionalStr,
  hs_code: optionalStr,
  sustainability_notes: optionalStr,
  carbon_footprint: optionalStr,
})

const otherSchema = z.object({
  ecn_eco_number: optionalStr,
  ecn_title: optionalStr,
  ecn_effective_date: optionalStr,
  labor_booking_actual: optionalStr,
  labor_booking_standard: optionalStr,
  tooling: z.array(toolingRowSchema),
  downtime_reasons: z.array(downtimeReasonRowSchema),
  scrap_rework: z.array(scrapReworkRowSchema),
})

export const manufacturingProfileSchema = z.object({
  master_data: masterDataSchema,
  inventory: inventorySchema,
  planning: planningSchema,
  quality: qualitySchema,
  costing: costingSchema,
  resources: resourcesSchema,
  supplier: supplierSchema,
  customer_sales: customerSalesSchema,
  compliance: complianceSchema,
  other: otherSchema,
})

export const manufacturingFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  manufacturing_profile: manufacturingProfileSchema,
})

export type ManufacturingFormValues = z.infer<typeof manufacturingFormSchema>
export type ManufacturingProfile = z.infer<typeof manufacturingProfileSchema>
export type BomLineRow = z.infer<typeof bomLineRowSchema>
export type RoutingOperationRow = z.infer<typeof routingOperationRowSchema>
export type QualityTemplateRow = z.infer<typeof qualityTemplateRowSchema>
export type LaborSkillRow = z.infer<typeof laborSkillRowSchema>
export type MaintenanceRow = z.infer<typeof maintenanceRowSchema>
export type ApprovedVendorRow = z.infer<typeof approvedVendorRowSchema>
export type ToolingRow = z.infer<typeof toolingRowSchema>
export type DowntimeReasonRow = z.infer<typeof downtimeReasonRowSchema>
export type ScrapReworkRow = z.infer<typeof scrapReworkRowSchema>

export const emptyBomLineRow = (): BomLineRow => ({
  component_code: "",
  qty_per_assembly: "",
  scrap_pct: "",
  yield_pct: "",
  alternate_group: "",
  ecn: "",
})

export const emptyRoutingOperationRow = (): RoutingOperationRow => ({
  sequence: "",
  operation_name: "",
  work_center: "",
  setup_time_minutes: "",
  run_time_minutes: "",
  cycle_time_minutes: "",
  requires_labor: "",
  requires_machine: "",
})

export const emptyQualityTemplateRow = (): QualityTemplateRow => ({
  characteristic: "",
  min_value: "",
  max_value: "",
  tolerance: "",
  defect_code: "",
})

export const emptyLaborSkillRow = (): LaborSkillRow => ({
  employee_ref: "",
  skill: "",
  availability: "",
  notes: "",
})

export const emptyMaintenanceRow = (): MaintenanceRow => ({
  machine_ref: "",
  scheduled_date: "",
  maintenance_type: "",
  notes: "",
})

export const emptyApprovedVendorRow = (): ApprovedVendorRow => ({
  supplier_code: "",
  supplier_name: "",
  lead_time_days: "",
  contract_ref: "",
  price_terms: "",
})

export const emptyToolingRow = (): ToolingRow => ({
  code: "",
  name: "",
  linked_operation: "",
  lifecycle_status: "",
})

export const emptyDowntimeReasonRow = (): DowntimeReasonRow => ({
  reason_code: "",
  description: "",
  category: "",
})

export const emptyScrapReworkRow = (): ScrapReworkRow => ({
  date: "",
  quantity: "",
  reason: "",
  disposition: "",
})

export const defaultManufacturingProfile: ManufacturingProfile = {
  master_data: {
    item_master: {
      item_code: "",
      description: "",
      specifications: "",
      uom: "",
      item_category: "",
      product_category: "",
      product_group: "",
      hierarchy: "",
      gross_weight: "",
      net_weight: "",
      length: "",
      width: "",
      height: "",
      volume: "",
      shelf_life_days: "",
      expiry_details: "",
      default_warehouse: "",
      default_location: "",
    },
    bom: {
      bom_number: "",
      version: "",
      scrap_pct: "",
      yield_rate: "",
      alternate_bom_ref: "",
      ecn: "",
      effective_from: "",
      effective_to: "",
      lines: [],
    },
    routing: {
      routing_code: "",
      routing_name: "",
      parent_sku: "",
      default_work_center: "",
      production_version: "",
      notes: "",
      operations: [],
    },
  },
  inventory: {
    on_hand: "",
    available: "",
    reserved: "",
    in_transit: "",
    lot_tracking: "",
    serial_tracking: "",
    bin_location: "",
    min_level: "",
    max_level: "",
    reorder_level: "",
    abc_class: "",
    valuation_method: "",
  },
  planning: {
    po_reference: "",
    order_quantity: "",
    due_date: "",
    priority: "",
    bom_version: "",
    routing_version: "",
    planned_consumption: "",
    actual_consumption: "",
    production_status: "",
    demand_forecast_ref: "",
    sales_order_ref: "",
    mrp_horizon_days: "",
    mps_code: "",
    calendar_code: "",
    order_creation_mode: "",
    last_mrp_run: "",
  },
  quality: {
    inspection_parameters: "",
    checkpoints: "",
    acceptance_criteria: "",
    coa_required: "",
    ncr_reference: "",
    capa_reference: "",
    plan_code: "",
    stage: "",
    templates: [],
  },
  costing: {
    standard_cost: "",
    variable_cost: "",
    fixed_cost: "",
    material_cost: "",
    labor_cost: "",
    overhead_cost: "",
    cost_center: "",
    allocation_rules: "",
    wip_tracking_notes: "",
  },
  resources: {
    work_center_code: "",
    capacity: "",
    efficiency_pct: "",
    downtime_notes: "",
    shift_calendar: "",
    labor_skills: [],
    maintenance: [],
  },
  supplier: {
    purchase_lead_time: "",
    contract_pricing: "",
    terms: "",
    pr_po_links: "",
    approved_vendors: [],
  },
  customer_sales: {
    customer_specific_bom: "",
    packing_labeling: "",
    order_history_notes: "",
    delivery_performance: "",
    customer_name: "",
    config_code: "",
  },
  compliance: {
    forward_traceability: "",
    backward_traceability: "",
    regulatory_codes: "",
    country_of_origin: "",
    hs_code: "",
    sustainability_notes: "",
    carbon_footprint: "",
  },
  other: {
    ecn_eco_number: "",
    ecn_title: "",
    ecn_effective_date: "",
    labor_booking_actual: "",
    labor_booking_standard: "",
    tooling: [],
    downtime_reasons: [],
    scrap_rework: [],
  },
}

export const defaultManufacturingFormValues: ManufacturingFormValues = {
  feature_code: "bom_routing",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  manufacturing_profile: defaultManufacturingProfile,
}

function asString(v: unknown): string {
  if (v == null) return ""
  return String(v)
}

function mergeSection<T extends Record<string, string>>(
  defaults: T,
  source: Record<string, unknown> | undefined,
): T {
  const out = { ...defaults }
  if (!source) return out
  for (const key of Object.keys(defaults) as (keyof T)[]) {
    if (key in source) out[key] = asString(source[key as string]) as T[keyof T]
  }
  return out
}

function mergeArray<T extends Record<string, string>>(
  empty: () => T,
  source: unknown,
): T[] {
  if (!Array.isArray(source)) return []
  return source.map((row) => mergeSection(empty(), row as Record<string, unknown>))
}

function parseProfileSection(
  defaults: ManufacturingProfile,
  source: Record<string, unknown> | undefined,
): ManufacturingProfile {
  if (!source) return defaults

  const md = (source.master_data as Record<string, unknown>) ?? {}
  const im = (md.item_master as Record<string, unknown>) ?? {}
  const bom = (md.bom as Record<string, unknown>) ?? {}
  const routing = (md.routing as Record<string, unknown>) ?? {}
  const inv = (source.inventory as Record<string, unknown>) ?? {}
  const plan = (source.planning as Record<string, unknown>) ?? {}
  const qual = (source.quality as Record<string, unknown>) ?? {}
  const cost = (source.costing as Record<string, unknown>) ?? {}
  const res = (source.resources as Record<string, unknown>) ?? {}
  const sup = (source.supplier as Record<string, unknown>) ?? {}
  const cs = (source.customer_sales as Record<string, unknown>) ?? {}
  const comp = (source.compliance as Record<string, unknown>) ?? {}
  const oth = (source.other as Record<string, unknown>) ?? {}

  return {
    master_data: {
      item_master: mergeSection(defaults.master_data.item_master, im),
      bom: {
        ...mergeSection(
          {
            bom_number: "",
            version: "",
            scrap_pct: "",
            yield_rate: "",
            alternate_bom_ref: "",
            ecn: "",
            effective_from: "",
            effective_to: "",
          },
          bom,
        ),
        lines: mergeArray(emptyBomLineRow, bom.lines),
      },
      routing: {
        ...mergeSection(
          {
            routing_code: "",
            routing_name: "",
            parent_sku: "",
            default_work_center: "",
            production_version: "",
            notes: "",
          },
          routing,
        ),
        operations: mergeArray(emptyRoutingOperationRow, routing.operations),
      },
    },
    inventory: mergeSection(defaults.inventory, inv),
    planning: mergeSection(defaults.planning, plan),
    quality: {
      ...mergeSection(
        {
          inspection_parameters: "",
          checkpoints: "",
          acceptance_criteria: "",
          coa_required: "",
          ncr_reference: "",
          capa_reference: "",
          plan_code: "",
          stage: "",
        },
        qual,
      ),
      templates: mergeArray(emptyQualityTemplateRow, qual.templates),
    },
    costing: mergeSection(defaults.costing, cost),
    resources: {
      ...mergeSection(
        {
          work_center_code: "",
          capacity: "",
          efficiency_pct: "",
          downtime_notes: "",
          shift_calendar: "",
        },
        res,
      ),
      labor_skills: mergeArray(emptyLaborSkillRow, res.labor_skills),
      maintenance: mergeArray(emptyMaintenanceRow, res.maintenance),
    },
    supplier: {
      ...mergeSection(
        {
          purchase_lead_time: "",
          contract_pricing: "",
          terms: "",
          pr_po_links: "",
        },
        sup,
      ),
      approved_vendors: mergeArray(emptyApprovedVendorRow, sup.approved_vendors),
    },
    customer_sales: mergeSection(defaults.customer_sales, cs),
    compliance: mergeSection(defaults.compliance, comp),
    other: {
      ...mergeSection(
        {
          ecn_eco_number: "",
          ecn_title: "",
          ecn_effective_date: "",
          labor_booking_actual: "",
          labor_booking_standard: "",
        },
        oth,
      ),
      tooling: mergeArray(emptyToolingRow, oth.tooling),
      downtime_reasons: mergeArray(emptyDowntimeReasonRow, oth.downtime_reasons),
      scrap_rework: mergeArray(emptyScrapReworkRow, oth.scrap_rework),
    },
  }
}

function migrateLegacyExtra(extra: Record<string, unknown>): ManufacturingProfile {
  const profile = structuredClone(defaultManufacturingProfile)

  const master = extra.master as Record<string, unknown> | undefined
  if (master) {
    profile.master_data.routing = {
      ...profile.master_data.routing,
      ...mergeSection(
        {
          routing_code: "",
          routing_name: "",
          parent_sku: "",
          default_work_center: "",
          production_version: "",
          notes: "",
        },
        master,
      ),
      operations: profile.master_data.routing.operations,
    }
  }

  const shopFloor = extra.shop_floor as Record<string, unknown> | undefined
  if (shopFloor) {
    profile.resources.work_center_code = asString(shopFloor.work_center_code)
    profile.planning.actual_consumption = [
      asString(shopFloor.output_quantity),
      asString(shopFloor.scrap_quantity),
    ]
      .filter(Boolean)
      .join(" / ")
    profile.other.downtime_reasons = shopFloor.downtime_reason
      ? [
          {
            reason_code: "",
            description: asString(shopFloor.downtime_reason),
            category: "shop_floor",
          },
        ]
      : []
    profile.resources.downtime_notes = asString(shopFloor.downtime_reason)
  }

  const planning = extra.planning as Record<string, unknown> | undefined
  if (planning) {
    profile.planning = mergeSection(profile.planning, {
      mrp_horizon_days: asString(planning.mrp_horizon_days),
      mps_code: asString(planning.mps_code),
      calendar_code: asString(planning.calendar_code),
      order_creation_mode: asString(planning.order_creation_mode),
      last_mrp_run: asString(planning.last_mrp_run),
    })
  }

  const quality = extra.quality as Record<string, unknown> | undefined
  if (quality) {
    profile.quality = {
      ...profile.quality,
      ...mergeSection(
        {
          plan_code: "",
          stage: "",
          ncr_reference: "",
          inspection_parameters: "",
          checkpoints: "",
          acceptance_criteria: "",
          coa_required: "",
          capa_reference: "",
        },
        quality,
      ),
      templates: quality.characteristic
        ? [
            {
              characteristic: asString(quality.characteristic),
              min_value: asString(quality.min_value),
              max_value: asString(quality.max_value),
              tolerance: "",
              defect_code: "",
            },
          ]
        : profile.quality.templates,
    }
  }

  const mto = extra.mto as Record<string, unknown> | undefined
  if (mto) {
    profile.customer_sales = mergeSection(profile.customer_sales, {
      customer_name: asString(mto.customer_name),
      config_code: asString(mto.config_code),
    })
    profile.planning.sales_order_ref = asString(mto.sales_order_ref)
  }

  const prod = extra.production as Record<string, unknown> | undefined
  if (prod) {
    const facility = (prod.facility as Record<string, unknown>) ?? {}
    const process = (prod.process as Record<string, unknown>) ?? {}
    const supply = (prod.supply_chain as Record<string, unknown>) ?? {}
    const capacity = (prod.capacity as Record<string, unknown>) ?? {}
    const workforce = (prod.workforce as Record<string, unknown>) ?? {}
    const qual = (prod.quality as Record<string, unknown>) ?? {}
    const costs = (prod.costs as Record<string, unknown>) ?? {}
    const regs = (prod.regulations as Record<string, unknown>) ?? {}
    const sust = (prod.sustainability as Record<string, unknown>) ?? {}
    const timeline = (prod.timeline as Record<string, unknown>) ?? {}
    const kpis = (prod.kpis as Record<string, unknown>) ?? {}

    profile.master_data.item_master.description = asString(process.step_by_step_flow)
    profile.master_data.routing.notes = asString(process.flowchart_notes)
    profile.resources.capacity = asString(capacity.installed_capacity)
    profile.resources.efficiency_pct = asString(capacity.utilized_pct)
    profile.resources.shift_calendar = asString(workforce.shift_patterns)
    profile.planning.due_date = asString(timeline.production_start_date)
    profile.costing = mergeSection(profile.costing, {
      material_cost: asString(costs.raw_material_cost),
      labor_cost: asString(costs.labor_cost),
      overhead_cost: asString(costs.overhead),
      variable_cost: asString(costs.fixed_vs_variable),
    })
    profile.quality = {
      ...profile.quality,
      inspection_parameters: asString(qual.standards) || profile.quality.inspection_parameters,
      checkpoints: asString(qual.inspection_stages) || profile.quality.checkpoints,
      acceptance_criteria:
        asString(qual.testing_procedures) || profile.quality.acceptance_criteria,
    }
    profile.compliance = mergeSection(profile.compliance, {
      regulatory_codes: asString(regs.product_regulatory),
      sustainability_notes: asString(sust.waste_recycling),
      carbon_footprint: asString(sust.carbon_footprint),
    })
    profile.inventory.reorder_level = asString(supply.reorder_levels)
    profile.supplier.purchase_lead_time = asString(supply.lead_time)

    const materials = mergeArray(
      () => ({ material_name: "", supplier: "", unit: "", notes: "" }),
      supply.materials,
    )
    profile.supplier.approved_vendors = materials.map((m) => ({
      supplier_code: "",
      supplier_name: m.supplier,
      lead_time_days: "",
      contract_ref: m.material_name,
      price_terms: m.notes,
    }))

    const altSuppliers = mergeArray(
      () => ({ supplier_name: "", material_or_component: "", lead_time: "", notes: "" }),
      supply.alternate_suppliers,
    )
    for (const a of altSuppliers) {
      profile.supplier.approved_vendors.push({
        supplier_code: "",
        supplier_name: a.supplier_name,
        lead_time_days: a.lead_time,
        contract_ref: a.material_or_component,
        price_terms: a.notes,
      })
    }

    if (facility.plant_location) {
      profile.compliance.forward_traceability = `Plant: ${asString(facility.plant_location)}`
    }
    if (kpis.oee_pct) {
      profile.resources.efficiency_pct = profile.resources.efficiency_pct || asString(kpis.oee_pct)
    }
  }

  return profile
}

function parseManufacturingProfile(extra: Record<string, unknown> | undefined): ManufacturingProfile {
  const raw = extra?.manufacturing_profile
  if (raw && typeof raw === "object") {
    return parseProfileSection(defaultManufacturingProfile, raw as Record<string, unknown>)
  }
  if (extra && (extra.master || extra.shop_floor || extra.planning || extra.quality || extra.mto || extra.production)) {
    const migrated = migrateLegacyExtra(extra)
    return parseProfileSection(defaultManufacturingProfile, migrated as unknown as Record<string, unknown>)
  }
  return defaultManufacturingProfile
}

export function recordToForm(record: ModuleRecord): ManufacturingFormValues {
  const extra =
    record.extra_data && typeof record.extra_data === "object"
      ? (record.extra_data as Record<string, unknown>)
      : undefined

  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    manufacturing_profile: parseManufacturingProfile(extra),
  }
}

function extraDataFromForm(values: ManufacturingFormValues) {
  return { manufacturing_profile: values.manufacturing_profile }
}

function deriveTopLevelFromForm(values: ManufacturingFormValues) {
  const im = values.manufacturing_profile.master_data.item_master
  let title = values.title.trim()
  const reference = values.reference.trim()
  let startDate: string | null = null

  if (!title && im.item_code.trim()) {
    title = im.item_code.trim()
  }
  if (!title && im.description.trim()) {
    title = im.description.trim().slice(0, 80)
  }

  const due = values.manufacturing_profile.planning.due_date.trim()
  if (due) startDate = due

  return {
    reference: reference || values.reference,
    title: title || values.title,
    start_date: startDate,
  }
}

export function formToCreatePayload(values: ManufacturingFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    feature_code: values.feature_code,
    reference: top.reference,
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    party_name: null,
    amount: null,
    quantity: null,
    start_date: top.start_date,
    end_date: null,
    extra_data: extraDataFromForm(values),
  }
}

export function formToUpdatePayload(values: ManufacturingFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    title: top.title,
    status: values.status,
    description: values.description.trim() || null,
    start_date: top.start_date,
    extra_data: extraDataFromForm(values),
  }
}

export function newManufacturingReference(featureCode?: string): string {
  const prefix = featureCode === "production_orders" ? "PO" : "MFG"
  return `${prefix}-${Date.now().toString(36).toUpperCase()}`
}

function profileFromRecord(record: ModuleRecord): ManufacturingProfile {
  const extra =
    record.extra_data && typeof record.extra_data === "object"
      ? (record.extra_data as Record<string, unknown>)
      : undefined
  return parseManufacturingProfile(extra)
}

export function itemCodeFromRecord(record: ModuleRecord): string {
  const code = profileFromRecord(record).master_data.item_master.item_code
  return code.trim() ? code : "—"
}

export function productionStatusFromRecord(record: ModuleRecord): string {
  const status = profileFromRecord(record).planning.production_status
  return status.trim() ? status : "—"
}
