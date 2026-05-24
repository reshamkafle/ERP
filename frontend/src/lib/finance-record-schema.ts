import { z } from "zod"

import type { ModuleRecord } from "@/types/module"

/** Empty string when unset — defaults applied in defaultFinanceFormValues. */
const optionalStr = z.string()

export const financeLineItemSchema = z.object({
  line_item_number: optionalStr,
  gl_account: optionalStr,
  offset_account: optionalStr,
  amount_document_currency: optionalStr,
  amount_local_currency: optionalStr,
  debit_credit_indicator: optionalStr,
  assignment: optionalStr,
  line_text: optionalStr,
  business_partner: optionalStr,
  cost_center: optionalStr,
  profit_center: optionalStr,
  internal_order: optionalStr,
  segment: optionalStr,
  tax_code: optionalStr,
  withholding_tax: optionalStr,
  payment_terms: optionalStr,
})

export const financeOrganizationalSchema = z.object({
  company_code: optionalStr,
  chart_of_accounts: optionalStr,
  controlling_area: optionalStr,
  fiscal_year_variant: optionalStr,
  posting_keys: optionalStr,
  document_types: optionalStr,
  business_area: optionalStr,
  profit_center: optionalStr,
  segment: optionalStr,
})

export const financeGlMasterSchema = z.object({
  gl_account_number: optionalStr,
  account_group: optionalStr,
  short_text: optionalStr,
  long_text: optionalStr,
  account_type: optionalStr,
  reconciliation_account: optionalStr,
  field_status_group: optionalStr,
  open_item_management: optionalStr,
  line_item_display: optionalStr,
  tax_category: optionalStr,
  currency: optionalStr,
  alternative_account_number: optionalStr,
})

export const financeCustomerMasterSchema = z.object({
  customer_number: optionalStr,
  name: optionalStr,
  address: optionalStr,
  contact_details: optionalStr,
  reconciliation_gl: optionalStr,
  payment_terms: optionalStr,
  credit_limit: optionalStr,
  sales_org: optionalStr,
  distribution_channel: optionalStr,
  bank_details: optionalStr,
  tax_information: optionalStr,
  dunning_procedure: optionalStr,
})

export const financeVendorMasterSchema = z.object({
  vendor_number: optionalStr,
  name: optionalStr,
  address: optionalStr,
  contact: optionalStr,
  reconciliation_gl: optionalStr,
  payment_terms: optionalStr,
  withholding_tax: optionalStr,
  purchasing_org: optionalStr,
  bank_details: optionalStr,
  payment_methods: optionalStr,
})

export const financeAssetMasterSchema = z.object({
  asset_number: optionalStr,
  sub_number: optionalStr,
  description: optionalStr,
  asset_class: optionalStr,
  acquisition_date: optionalStr,
  acquisition_value: optionalStr,
  depreciation_key: optionalStr,
  depreciation_area: optionalStr,
  useful_life: optionalStr,
  cost_center: optionalStr,
  profit_center: optionalStr,
  inventory_number: optionalStr,
  location: optionalStr,
})

export const financeBankMasterSchema = z.object({
  house_bank: optionalStr,
  bank_account_number: optionalStr,
  bank_key: optionalStr,
  swift_bic: optionalStr,
  iban: optionalStr,
  gl_account_link: optionalStr,
  bank_statement_config: optionalStr,
})

export const financeMasterFiSchema = z.object({
  gl_account: financeGlMasterSchema,
  customer: financeCustomerMasterSchema,
  vendor: financeVendorMasterSchema,
  asset: financeAssetMasterSchema,
  bank: financeBankMasterSchema,
})

export const financeCostCenterSchema = z.object({
  cost_center: optionalStr,
  description: optionalStr,
  responsible_person: optionalStr,
  hierarchy: optionalStr,
  cost_center_category: optionalStr,
  functional_area: optionalStr,
})

export const financeProfitCenterSchema = z.object({
  profit_center: optionalStr,
  description: optionalStr,
  hierarchy: optionalStr,
  segment_assignment: optionalStr,
})

export const financeInternalOrderSchema = z.object({
  order_type: optionalStr,
  responsible_person: optionalStr,
  settlement_rules: optionalStr,
  budget: optionalStr,
})

export const financeCostElementSchema = z.object({
  cost_element: optionalStr,
  primary_secondary: optionalStr,
  category: optionalStr,
})

export const financeActivityTypeSchema = z.object({
  activity_type: optionalStr,
  price: optionalStr,
  unit_of_measure: optionalStr,
})

export const financeStatisticalKeyFigureSchema = z.object({
  key_figure: optionalStr,
  description: optionalStr,
})

export const financeMasterCoSchema = z.object({
  cost_center: financeCostCenterSchema,
  profit_center: financeProfitCenterSchema,
  internal_order: financeInternalOrderSchema,
  cost_element: financeCostElementSchema,
  activity_type: financeActivityTypeSchema,
  statistical_key_figure: financeStatisticalKeyFigureSchema,
})

export const financeTransactionalHeaderSchema = z.object({
  document_number: optionalStr,
  company_code: optionalStr,
  fiscal_year: optionalStr,
  posting_date: optionalStr,
  document_date: optionalStr,
  document_type: optionalStr,
  posting_key: optionalStr,
  reference: optionalStr,
  header_text: optionalStr,
  clearing_document: optionalStr,
  clearing_date: optionalStr,
  special_gl_indicator: optionalStr,
  asset_transaction_type: optionalStr,
  controlling_area: optionalStr,
  cost_element: optionalStr,
  value_type: optionalStr,
  object_type: optionalStr,
  invoice_number: optionalStr,
  due_date: optionalStr,
  dunning_level: optionalStr,
  invoice_reference: optionalStr,
  payment_block: optionalStr,
  automatic_payment_run: optionalStr,
  depreciation_posting: optionalStr,
  retirement_details: optionalStr,
  bank_statement_line: optionalStr,
  reconciliation_status: optionalStr,
  allocated_amounts: optionalStr,
  variance_categories: optionalStr,
  settlement_receivers: optionalStr,
})

export const financeTransactionalSchema = z.object({
  header: financeTransactionalHeaderSchema,
  line_items: z.array(financeLineItemSchema),
})

export const financeReportingSchema = z.object({
  balance_sheet_scope: optionalStr,
  pl_accounts: optionalStr,
  trial_balance: optionalStr,
  cash_flow: optionalStr,
  copa_characteristics: optionalStr,
  copa_value_fields: optionalStr,
  budget_vs_actual: optionalStr,
  forecasts: optionalStr,
  kpi_liquidity_ratio: optionalStr,
  kpi_roi: optionalStr,
  kpi_cost_variances: optionalStr,
  compliance_kpis: optionalStr,
})

export const financeFormSchema = z.object({
  feature_code: z.string().min(1),
  reference: z.string().min(1).max(64),
  title: z.string().min(1).max(255),
  status: z.string().min(1).max(32),
  description: optionalStr,
  party_name: optionalStr,
  amount: optionalStr,
  quantity: optionalStr,
  start_date: optionalStr,
  end_date: optionalStr,
  organizational: financeOrganizationalSchema,
  master_fi: financeMasterFiSchema,
  master_co: financeMasterCoSchema,
  transactional: financeTransactionalSchema,
  reporting: financeReportingSchema,
})

export type FinanceFormValues = z.infer<typeof financeFormSchema>
export type FinanceLineItem = z.infer<typeof financeLineItemSchema>

export const FINANCE_MODULE_CODE = "finance"

export const FINANCE_STATUS_OPTIONS = [
  "DRAFT",
  "ACTIVE",
  "IN_PROGRESS",
  "COMPLETED",
  "APPROVED",
  "REJECTED",
  "CANCELLED",
] as const

export const emptyLineItem = (): FinanceLineItem => ({
  line_item_number: "",
  gl_account: "",
  offset_account: "",
  amount_document_currency: "",
  amount_local_currency: "",
  debit_credit_indicator: "",
  assignment: "",
  line_text: "",
  business_partner: "",
  cost_center: "",
  profit_center: "",
  internal_order: "",
  segment: "",
  tax_code: "",
  withholding_tax: "",
  payment_terms: "",
})

export const defaultFinanceFormValues: FinanceFormValues = {
  feature_code: "general_ledger",
  reference: "",
  title: "",
  status: "DRAFT",
  description: "",
  party_name: "",
  amount: "",
  quantity: "",
  start_date: "",
  end_date: "",
  organizational: {
    company_code: "",
    chart_of_accounts: "",
    controlling_area: "",
    fiscal_year_variant: "",
    posting_keys: "",
    document_types: "",
    business_area: "",
    profit_center: "",
    segment: "",
  },
  master_fi: {
    gl_account: {
      gl_account_number: "",
      account_group: "",
      short_text: "",
      long_text: "",
      account_type: "",
      reconciliation_account: "",
      field_status_group: "",
      open_item_management: "",
      line_item_display: "",
      tax_category: "",
      currency: "",
      alternative_account_number: "",
    },
    customer: {
      customer_number: "",
      name: "",
      address: "",
      contact_details: "",
      reconciliation_gl: "",
      payment_terms: "",
      credit_limit: "",
      sales_org: "",
      distribution_channel: "",
      bank_details: "",
      tax_information: "",
      dunning_procedure: "",
    },
    vendor: {
      vendor_number: "",
      name: "",
      address: "",
      contact: "",
      reconciliation_gl: "",
      payment_terms: "",
      withholding_tax: "",
      purchasing_org: "",
      bank_details: "",
      payment_methods: "",
    },
    asset: {
      asset_number: "",
      sub_number: "",
      description: "",
      asset_class: "",
      acquisition_date: "",
      acquisition_value: "",
      depreciation_key: "",
      depreciation_area: "",
      useful_life: "",
      cost_center: "",
      profit_center: "",
      inventory_number: "",
      location: "",
    },
    bank: {
      house_bank: "",
      bank_account_number: "",
      bank_key: "",
      swift_bic: "",
      iban: "",
      gl_account_link: "",
      bank_statement_config: "",
    },
  },
  master_co: {
    cost_center: {
      cost_center: "",
      description: "",
      responsible_person: "",
      hierarchy: "",
      cost_center_category: "",
      functional_area: "",
    },
    profit_center: {
      profit_center: "",
      description: "",
      hierarchy: "",
      segment_assignment: "",
    },
    internal_order: {
      order_type: "",
      responsible_person: "",
      settlement_rules: "",
      budget: "",
    },
    cost_element: {
      cost_element: "",
      primary_secondary: "",
      category: "",
    },
    activity_type: {
      activity_type: "",
      price: "",
      unit_of_measure: "",
    },
    statistical_key_figure: {
      key_figure: "",
      description: "",
    },
  },
  transactional: {
    header: {
      document_number: "",
      company_code: "",
      fiscal_year: "",
      posting_date: "",
      document_date: "",
      document_type: "",
      posting_key: "",
      reference: "",
      header_text: "",
      clearing_document: "",
      clearing_date: "",
      special_gl_indicator: "",
      asset_transaction_type: "",
      controlling_area: "",
      cost_element: "",
      value_type: "",
      object_type: "",
      invoice_number: "",
      due_date: "",
      dunning_level: "",
      invoice_reference: "",
      payment_block: "",
      automatic_payment_run: "",
      depreciation_posting: "",
      retirement_details: "",
      bank_statement_line: "",
      reconciliation_status: "",
      allocated_amounts: "",
      variance_categories: "",
      settlement_receivers: "",
    },
    line_items: [],
  },
  reporting: {
    balance_sheet_scope: "",
    pl_accounts: "",
    trial_balance: "",
    cash_flow: "",
    copa_characteristics: "",
    copa_value_fields: "",
    budget_vs_actual: "",
    forecasts: "",
    kpi_liquidity_ratio: "",
    kpi_roi: "",
    kpi_cost_variances: "",
    compliance_kpis: "",
  },
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

function parseExtra(extra: Record<string, unknown> | null | undefined) {
  const org = (extra?.organizational as Record<string, unknown>) ?? {}
  const mfi = (extra?.master_fi as Record<string, unknown>) ?? {}
  const mco = (extra?.master_co as Record<string, unknown>) ?? {}
  const txn = (extra?.transactional as Record<string, unknown>) ?? {}
  const header = (txn.header as Record<string, unknown>) ?? {}
  const lines = Array.isArray(txn.line_items) ? txn.line_items : []
  const rep = (extra?.reporting as Record<string, unknown>) ?? {}

  return {
    organizational: mergeSection(defaultFinanceFormValues.organizational, org),
    master_fi: {
      gl_account: mergeSection(
        defaultFinanceFormValues.master_fi.gl_account,
        mfi.gl_account as Record<string, unknown>,
      ),
      customer: mergeSection(
        defaultFinanceFormValues.master_fi.customer,
        mfi.customer as Record<string, unknown>,
      ),
      vendor: mergeSection(
        defaultFinanceFormValues.master_fi.vendor,
        mfi.vendor as Record<string, unknown>,
      ),
      asset: mergeSection(
        defaultFinanceFormValues.master_fi.asset,
        mfi.asset as Record<string, unknown>,
      ),
      bank: mergeSection(
        defaultFinanceFormValues.master_fi.bank,
        mfi.bank as Record<string, unknown>,
      ),
    },
    master_co: {
      cost_center: mergeSection(
        defaultFinanceFormValues.master_co.cost_center,
        mco.cost_center as Record<string, unknown>,
      ),
      profit_center: mergeSection(
        defaultFinanceFormValues.master_co.profit_center,
        mco.profit_center as Record<string, unknown>,
      ),
      internal_order: mergeSection(
        defaultFinanceFormValues.master_co.internal_order,
        mco.internal_order as Record<string, unknown>,
      ),
      cost_element: mergeSection(
        defaultFinanceFormValues.master_co.cost_element,
        mco.cost_element as Record<string, unknown>,
      ),
      activity_type: mergeSection(
        defaultFinanceFormValues.master_co.activity_type,
        mco.activity_type as Record<string, unknown>,
      ),
      statistical_key_figure: mergeSection(
        defaultFinanceFormValues.master_co.statistical_key_figure,
        mco.statistical_key_figure as Record<string, unknown>,
      ),
    },
    transactional: {
      header: mergeSection(defaultFinanceFormValues.transactional.header, header),
      line_items: lines.length
        ? lines.map((row) =>
            mergeSection(emptyLineItem(), row as Record<string, unknown>),
          )
        : [],
    },
    reporting: mergeSection(defaultFinanceFormValues.reporting, rep),
  }
}

export function recordToForm(record: ModuleRecord): FinanceFormValues {
  const extra = parseExtra(record.extra_data)
  return {
    feature_code: record.feature_code,
    reference: record.reference,
    title: record.title,
    status: record.status,
    description: record.description ?? "",
    party_name: record.party_name ?? "",
    amount: record.amount != null ? String(record.amount) : "",
    quantity: record.quantity != null ? String(record.quantity) : "",
    start_date: record.start_date ?? "",
    end_date: record.end_date ?? "",
    ...extra,
  }
}

function parseOptionalNumber(value: string): number | null {
  const t = value.trim()
  if (!t) return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

function deriveTopLevelFromForm(values: FinanceFormValues) {
  const h = values.transactional.header
  let party = values.party_name.trim()
  let amount = parseOptionalNumber(values.amount)
  let startDate = values.start_date.trim() || null
  let endDate = values.end_date.trim() || null

  switch (values.feature_code) {
    case "accounts_receivable":
      party = party || values.master_fi.customer.name.trim()
      amount =
        amount ??
        parseOptionalNumber(
          values.transactional.line_items[0]?.amount_document_currency ?? "",
        )
      startDate = startDate || h.posting_date.trim() || null
      endDate = endDate || h.due_date.trim() || null
      break
    case "accounts_payable":
      party = party || values.master_fi.vendor.name.trim()
      amount =
        amount ??
        parseOptionalNumber(
          values.transactional.line_items[0]?.amount_document_currency ?? "",
        )
      startDate = startDate || h.posting_date.trim() || null
      break
    case "general_ledger":
    case "compliance_tax":
      amount =
        amount ??
        parseOptionalNumber(
          values.transactional.line_items[0]?.amount_document_currency ?? "",
        )
      startDate = startDate || h.posting_date.trim() || null
      endDate = endDate || h.document_date.trim() || null
      break
    case "asset_management":
      party = party || values.master_fi.asset.description.trim()
      amount = amount ?? parseOptionalNumber(values.master_fi.asset.acquisition_value)
      startDate = startDate || values.master_fi.asset.acquisition_date.trim() || null
      break
    default:
      break
  }

  return {
    party_name: party || null,
    amount,
    quantity: parseOptionalNumber(values.quantity),
    start_date: startDate,
    end_date: endDate,
  }
}

export function formToCreatePayload(values: FinanceFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    feature_code: values.feature_code,
    reference: values.reference.trim(),
    title: values.title.trim(),
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: {
      organizational: values.organizational,
      master_fi: values.master_fi,
      master_co: values.master_co,
      transactional: values.transactional,
      reporting: values.reporting,
    },
  }
}

export function formToUpdatePayload(values: FinanceFormValues) {
  const top = deriveTopLevelFromForm(values)
  return {
    title: values.title.trim(),
    status: values.status,
    description: values.description.trim() || null,
    party_name: top.party_name,
    amount: top.amount,
    quantity: top.quantity,
    start_date: top.start_date,
    end_date: top.end_date,
    extra_data: {
      organizational: values.organizational,
      master_fi: values.master_fi,
      master_co: values.master_co,
      transactional: values.transactional,
      reporting: values.reporting,
    },
  }
}

export function newFinanceReference(): string {
  return `FI-${Date.now().toString(36).toUpperCase()}`
}

export function companyCodeFromRecord(record: ModuleRecord): string {
  const extra = record.extra_data
  if (!extra || typeof extra !== "object") return "—"
  const org = extra.organizational as Record<string, unknown> | undefined
  const code = org?.company_code
  return typeof code === "string" && code.trim() ? code : "—"
}