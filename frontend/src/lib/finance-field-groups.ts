export type FinanceFieldType = "text" | "number" | "date" | "textarea" | "select"

export type FinanceFieldDef = {
  path: string
  label: string
  type?: FinanceFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type FinanceSectionDef = {
  id: string
  title: string
  description?: string
  fields: FinanceFieldDef[]
  /** When true, dialog renders line_items via useFieldArray instead of fields list */
  isLineItems?: boolean
}

const organizationalFields: FinanceFieldDef[] = [
  { path: "organizational.company_code", label: "Company Code (BUKRS)" },
  { path: "organizational.chart_of_accounts", label: "Chart of Accounts (KTOPL)" },
  { path: "organizational.controlling_area", label: "Controlling Area (KOKRS)" },
  { path: "organizational.fiscal_year_variant", label: "Fiscal Year Variant" },
  { path: "organizational.posting_keys", label: "Posting Keys" },
  { path: "organizational.document_types", label: "Document Types (BLART)" },
  { path: "organizational.business_area", label: "Business Area" },
  { path: "organizational.profit_center", label: "Profit Center" },
  { path: "organizational.segment", label: "Segment" },
]

const organizationalSubset: FinanceFieldDef[] = [
  { path: "organizational.company_code", label: "Company Code (BUKRS)" },
  { path: "organizational.controlling_area", label: "Controlling Area (KOKRS)" },
  { path: "organizational.fiscal_year_variant", label: "Fiscal Year Variant" },
  { path: "organizational.document_types", label: "Document Types (BLART)" },
]

const glMasterFields: FinanceFieldDef[] = [
  { path: "master_fi.gl_account.gl_account_number", label: "G/L Account Number (SAKNR)" },
  { path: "master_fi.gl_account.account_group", label: "Account Group" },
  { path: "master_fi.gl_account.short_text", label: "Short Text" },
  { path: "master_fi.gl_account.long_text", label: "Long Text Description", type: "textarea" },
  { path: "master_fi.gl_account.account_type", label: "Account Type (Balance Sheet / P&L)" },
  { path: "master_fi.gl_account.reconciliation_account", label: "Reconciliation Account" },
  { path: "master_fi.gl_account.field_status_group", label: "Field Status Group" },
  { path: "master_fi.gl_account.open_item_management", label: "Open Item Management" },
  { path: "master_fi.gl_account.line_item_display", label: "Line Item Display" },
  { path: "master_fi.gl_account.tax_category", label: "Tax Category" },
  { path: "master_fi.gl_account.currency", label: "Currency" },
  { path: "master_fi.gl_account.alternative_account_number", label: "Alternative Account Number" },
]

const customerMasterFields: FinanceFieldDef[] = [
  { path: "master_fi.customer.customer_number", label: "Customer Number (KUNNR)" },
  { path: "master_fi.customer.name", label: "Name" },
  { path: "master_fi.customer.address", label: "Address", type: "textarea" },
  { path: "master_fi.customer.contact_details", label: "Contact Details" },
  { path: "master_fi.customer.reconciliation_gl", label: "Reconciliation G/L" },
  { path: "master_fi.customer.payment_terms", label: "Payment Terms" },
  { path: "master_fi.customer.credit_limit", label: "Credit Limit" },
  { path: "master_fi.customer.sales_org", label: "Sales Organization" },
  { path: "master_fi.customer.distribution_channel", label: "Distribution Channel" },
  { path: "master_fi.customer.bank_details", label: "Bank Details" },
  { path: "master_fi.customer.tax_information", label: "Tax Information" },
  { path: "master_fi.customer.dunning_procedure", label: "Dunning Procedure" },
]

const vendorMasterFields: FinanceFieldDef[] = [
  { path: "master_fi.vendor.vendor_number", label: "Vendor Number (LIFNR)" },
  { path: "master_fi.vendor.name", label: "Name" },
  { path: "master_fi.vendor.address", label: "Address", type: "textarea" },
  { path: "master_fi.vendor.contact", label: "Contact" },
  { path: "master_fi.vendor.reconciliation_gl", label: "Reconciliation G/L" },
  { path: "master_fi.vendor.payment_terms", label: "Payment Terms" },
  { path: "master_fi.vendor.withholding_tax", label: "Withholding Tax" },
  { path: "master_fi.vendor.purchasing_org", label: "Purchasing Organization" },
  { path: "master_fi.vendor.bank_details", label: "Bank Details" },
  { path: "master_fi.vendor.payment_methods", label: "Payment Methods" },
]

const assetMasterFields: FinanceFieldDef[] = [
  { path: "master_fi.asset.asset_number", label: "Asset Number" },
  { path: "master_fi.asset.sub_number", label: "Sub-Number" },
  { path: "master_fi.asset.description", label: "Description" },
  { path: "master_fi.asset.asset_class", label: "Asset Class" },
  { path: "master_fi.asset.acquisition_date", label: "Acquisition Date", type: "date" },
  { path: "master_fi.asset.acquisition_value", label: "Acquisition Value", type: "number" },
  { path: "master_fi.asset.depreciation_key", label: "Depreciation Key" },
  { path: "master_fi.asset.depreciation_area", label: "Depreciation Area" },
  { path: "master_fi.asset.useful_life", label: "Useful Life" },
  { path: "master_fi.asset.cost_center", label: "Cost Center" },
  { path: "master_fi.asset.profit_center", label: "Profit Center" },
  { path: "master_fi.asset.inventory_number", label: "Inventory Number" },
  { path: "master_fi.asset.location", label: "Location" },
]

const costCenterFields: FinanceFieldDef[] = [
  { path: "master_co.cost_center.cost_center", label: "Cost Center (KOSTL)" },
  { path: "master_co.cost_center.description", label: "Description" },
  { path: "master_co.cost_center.responsible_person", label: "Responsible Person" },
  { path: "master_co.cost_center.hierarchy", label: "Hierarchy" },
  { path: "master_co.cost_center.cost_center_category", label: "Cost Center Category" },
  { path: "master_co.cost_center.functional_area", label: "Functional Area" },
]

const profitCenterCoFields: FinanceFieldDef[] = [
  { path: "master_co.profit_center.profit_center", label: "Profit Center (PRCTR)" },
  { path: "master_co.profit_center.description", label: "Description" },
  { path: "master_co.profit_center.hierarchy", label: "Hierarchy" },
  { path: "master_co.profit_center.segment_assignment", label: "Segment Assignment" },
]

const internalOrderFields: FinanceFieldDef[] = [
  { path: "master_co.internal_order.order_type", label: "Order Type" },
  { path: "master_co.internal_order.responsible_person", label: "Responsible Person" },
  { path: "master_co.internal_order.settlement_rules", label: "Settlement Rules", type: "textarea" },
  { path: "master_co.internal_order.budget", label: "Budget", type: "number" },
]

const costElementFields: FinanceFieldDef[] = [
  { path: "master_co.cost_element.cost_element", label: "Cost Element (KSTAR)" },
  { path: "master_co.cost_element.primary_secondary", label: "Primary / Secondary" },
  { path: "master_co.cost_element.category", label: "Category" },
]

const activityTypeFields: FinanceFieldDef[] = [
  { path: "master_co.activity_type.activity_type", label: "Activity Type" },
  { path: "master_co.activity_type.price", label: "Price", type: "number" },
  { path: "master_co.activity_type.unit_of_measure", label: "Unit of Measure" },
]

const statisticalKeyFields: FinanceFieldDef[] = [
  { path: "master_co.statistical_key_figure.key_figure", label: "Statistical Key Figure" },
  { path: "master_co.statistical_key_figure.description", label: "Description" },
]

const txnHeaderGlFields: FinanceFieldDef[] = [
  { path: "transactional.header.document_number", label: "Document Number (BELNR)" },
  { path: "transactional.header.company_code", label: "Company Code (BUKRS)" },
  { path: "transactional.header.fiscal_year", label: "Fiscal Year (GJAHR)" },
  { path: "transactional.header.posting_date", label: "Posting Date (BUDAT)", type: "date" },
  { path: "transactional.header.document_date", label: "Document Date (BLDAT)", type: "date" },
  { path: "transactional.header.document_type", label: "Document Type (BLART)" },
  { path: "transactional.header.posting_key", label: "Posting Key" },
  { path: "transactional.header.reference", label: "Reference (XBLNR)" },
  { path: "transactional.header.header_text", label: "Header Text" },
  { path: "transactional.header.clearing_document", label: "Clearing Document" },
  { path: "transactional.header.clearing_date", label: "Clearing Date", type: "date" },
  { path: "transactional.header.special_gl_indicator", label: "Special G/L Indicator" },
]

const txnHeaderApFields: FinanceFieldDef[] = [
  ...txnHeaderGlFields.slice(0, 9),
  { path: "transactional.header.invoice_reference", label: "Invoice Reference" },
  { path: "transactional.header.payment_block", label: "Payment Block" },
  { path: "transactional.header.automatic_payment_run", label: "Automatic Payment Run Data" },
]

const txnHeaderArFields: FinanceFieldDef[] = [
  ...txnHeaderGlFields.slice(0, 9),
  { path: "transactional.header.invoice_number", label: "Invoice Number" },
  { path: "transactional.header.due_date", label: "Due Date", type: "date" },
  { path: "transactional.header.dunning_level", label: "Dunning Level" },
  { path: "transactional.header.special_gl_indicator", label: "Special G/L" },
]

const txnHeaderAssetFields: FinanceFieldDef[] = [
  { path: "transactional.header.document_number", label: "Document Number" },
  { path: "transactional.header.posting_date", label: "Posting Date", type: "date" },
  { path: "transactional.header.asset_transaction_type", label: "Asset Transaction Type" },
  { path: "transactional.header.depreciation_posting", label: "Depreciation Posting" },
  { path: "transactional.header.retirement_details", label: "Retirement Details", type: "textarea" },
]

const txnHeaderTaxFields: FinanceFieldDef[] = [
  { path: "transactional.header.document_number", label: "Document Number" },
  { path: "transactional.header.company_code", label: "Company Code" },
  { path: "transactional.header.posting_date", label: "Posting Date", type: "date" },
  { path: "transactional.header.document_type", label: "Document Type" },
  { path: "transactional.header.reference", label: "Reference" },
]

const txnHeaderCoFields: FinanceFieldDef[] = [
  { path: "transactional.header.controlling_area", label: "Controlling Area" },
  { path: "transactional.header.cost_element", label: "Cost Element" },
  { path: "transactional.header.value_type", label: "Value Type (WRTTP)" },
  { path: "transactional.header.object_type", label: "Object Type" },
  { path: "transactional.header.allocated_amounts", label: "Allocated Amounts", type: "number" },
  { path: "transactional.header.variance_categories", label: "Variance Categories" },
  { path: "transactional.header.settlement_receivers", label: "Settlement Receivers" },
]

const reportingFields: FinanceFieldDef[] = [
  { path: "reporting.balance_sheet_scope", label: "Balance Sheet Scope" },
  { path: "reporting.pl_accounts", label: "P&L Accounts" },
  { path: "reporting.trial_balance", label: "Trial Balance" },
  { path: "reporting.cash_flow", label: "Cash Flow" },
  { path: "reporting.copa_characteristics", label: "CO-PA Characteristics (Product, Customer, Region)" },
  { path: "reporting.copa_value_fields", label: "CO-PA Value Fields (Revenue, Cost)" },
  { path: "reporting.budget_vs_actual", label: "Budget vs. Actual" },
  { path: "reporting.forecasts", label: "Forecasts" },
  { path: "reporting.kpi_liquidity_ratio", label: "KPI: Liquidity Ratios" },
  { path: "reporting.kpi_roi", label: "KPI: ROI" },
  { path: "reporting.kpi_cost_variances", label: "KPI: Cost Variances" },
]

const reportingComplianceFields: FinanceFieldDef[] = [
  ...reportingFields.filter((f) =>
    ["reporting.compliance_kpis", "reporting.trial_balance", "reporting.budget_vs_actual"].includes(
      f.path,
    ),
  ),
  { path: "reporting.compliance_kpis", label: "Compliance KPIs" },
]

export const lineItemFields: FinanceFieldDef[] = [
  { path: "line_item_number", label: "Line Item (BUZEI)" },
  { path: "gl_account", label: "G/L Account (HKONT)" },
  { path: "offset_account", label: "Offset Account" },
  { path: "amount_document_currency", label: "Amount Doc. Currency (WRBTR)", type: "number" },
  { path: "amount_local_currency", label: "Amount Local (DMBTR)", type: "number" },
  { path: "debit_credit_indicator", label: "Debit/Credit (SHKZG)" },
  { path: "assignment", label: "Assignment (ZUONR)" },
  { path: "line_text", label: "Text" },
  { path: "business_partner", label: "Business Partner" },
  { path: "cost_center", label: "Cost Center" },
  { path: "profit_center", label: "Profit Center" },
  { path: "internal_order", label: "Internal Order" },
  { path: "segment", label: "Segment" },
  { path: "tax_code", label: "Tax Code" },
  { path: "withholding_tax", label: "Withholding Tax" },
  { path: "payment_terms", label: "Payment Terms" },
]

const coreRecordFields: FinanceFieldDef[] = [
  { path: "reference", label: "Reference" },
  { path: "title", label: "Title / Header Text" },
  {
    path: "status",
    label: "Status",
    type: "select",
    options: [
      { value: "DRAFT", label: "Draft" },
      { value: "ACTIVE", label: "Active" },
      { value: "IN_PROGRESS", label: "In Progress" },
      { value: "COMPLETED", label: "Completed" },
      { value: "APPROVED", label: "Approved" },
      { value: "REJECTED", label: "Rejected" },
      { value: "CANCELLED", label: "Cancelled" },
    ],
  },
  { path: "description", label: "Description", type: "textarea", colSpan: 2 },
  { path: "party_name", label: "Party / Business Partner" },
  { path: "amount", label: "Amount (summary)", type: "number" },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "start_date", label: "Start / Posting Date", type: "date" },
  { path: "end_date", label: "End / Due Date", type: "date" },
]

const FEATURE_SECTIONS: Record<string, FinanceSectionDef[]> = {
  general_ledger: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "org", title: "Organizational & configuration", fields: organizationalFields },
    { id: "gl", title: "G/L account master", fields: glMasterFields },
    { id: "txn", title: "Document header", fields: txnHeaderGlFields },
    {
      id: "lines",
      title: "Line items (BSEG)",
      description: "Document line item details",
      fields: [],
      isLineItems: true,
    },
  ],
  accounts_payable: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "org", title: "Organizational setup", fields: organizationalSubset },
    { id: "vendor", title: "Vendor master (AP)", fields: vendorMasterFields },
    { id: "txn", title: "AP document header", fields: txnHeaderApFields },
    { id: "lines", title: "Line items", fields: [], isLineItems: true },
  ],
  accounts_receivable: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "org", title: "Organizational setup", fields: organizationalSubset },
    { id: "customer", title: "Customer master (AR)", fields: customerMasterFields },
    { id: "txn", title: "AR document header", fields: txnHeaderArFields },
    { id: "lines", title: "Line items", fields: [], isLineItems: true },
  ],
  asset_management: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "org", title: "Organizational setup", fields: organizationalSubset },
    { id: "asset", title: "Asset master", fields: assetMasterFields },
    { id: "txn", title: "Asset transactions", fields: txnHeaderAssetFields },
  ],
  cost_controlling: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    {
      id: "org",
      title: "Controlling area setup",
      fields: organizationalFields.filter((f) =>
        ["organizational.company_code", "organizational.controlling_area", "organizational.segment"].includes(
          f.path,
        ),
      ),
    },
    { id: "cc", title: "Cost center", fields: costCenterFields },
    { id: "pc", title: "Profit center", fields: profitCenterCoFields },
    { id: "io", title: "Internal order", fields: internalOrderFields },
    { id: "ce", title: "Cost element", fields: costElementFields },
    { id: "at", title: "Activity type", fields: activityTypeFields },
    { id: "skf", title: "Statistical key figure", fields: statisticalKeyFields },
    { id: "txn", title: "CO document fields", fields: txnHeaderCoFields },
  ],
  budgeting: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    {
      id: "org",
      title: "Controlling setup",
      fields: organizationalFields.filter((f) =>
        ["organizational.controlling_area", "organizational.company_code", "organizational.fiscal_year_variant"].includes(
          f.path,
        ),
      ),
    },
    { id: "cc", title: "Cost center", fields: costCenterFields },
    {
      id: "report",
      title: "Budget & forecasting",
      fields: reportingFields.filter((f) =>
        ["reporting.budget_vs_actual", "reporting.forecasts", "reporting.kpi_cost_variances"].includes(
          f.path,
        ),
      ),
    },
  ],
  financial_reporting: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    { id: "report", title: "Reporting & analytics", fields: reportingFields },
  ],
  compliance_tax: [
    { id: "core", title: "Record identity", fields: coreRecordFields },
    {
      id: "org",
      title: "Tax & company setup",
      fields: [
        ...organizationalSubset,
        { path: "organizational.posting_keys", label: "Posting Keys" },
      ],
    },
    { id: "txn", title: "Tax document header", fields: txnHeaderTaxFields },
    {
      id: "lines",
      title: "Line items (tax)",
      fields: lineItemFields.filter((f) =>
        ["line_item_number", "gl_account", "amount_document_currency", "tax_code", "withholding_tax"].includes(
          f.path,
        ),
      ),
      isLineItems: true,
    },
    { id: "report", title: "Compliance reporting", fields: reportingComplianceFields },
  ],
}

export const FINANCE_FEATURE_OPTIONS = [
  { value: "general_ledger", label: "General Ledger" },
  { value: "accounts_payable", label: "Accounts Payable" },
  { value: "accounts_receivable", label: "Accounts Receivable" },
  { value: "financial_reporting", label: "Financial Reporting" },
  { value: "budgeting", label: "Budgeting & Forecasting" },
  { value: "asset_management", label: "Asset Management" },
  { value: "cost_controlling", label: "Cost Controlling" },
  { value: "compliance_tax", label: "Compliance & Taxation" },
] as const

export function getFinanceSectionsForFeature(featureCode: string): FinanceSectionDef[] {
  return FEATURE_SECTIONS[featureCode] ?? FEATURE_SECTIONS.general_ledger
}
