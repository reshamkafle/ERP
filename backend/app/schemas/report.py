from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


ReportPeriod = str  # today | week | month


class SalesChartPoint(BaseModel):
    label: str
    revenue: Decimal
    sale_count: int


class SaleSummaryRow(BaseModel):
    id: int
    created_at: datetime
    item_count: int
    total: Decimal


class SalesReportResponse(BaseModel):
    period: str
    total_revenue: Decimal
    sale_count: int
    chart: list[SalesChartPoint]
    sales: list[SaleSummaryRow]


class TopProductRow(BaseModel):
    product_id: int
    sku: str
    name: str
    quantity_sold: int
    revenue: Decimal


class TopProductsReportResponse(BaseModel):
    products: list[TopProductRow]


class StockValueRow(BaseModel):
    product_id: int
    sku: str
    name: str
    stock: int
    cost_price: Decimal
    line_value: Decimal


class StockValueReportResponse(BaseModel):
    total_value: Decimal
    product_count: int
    items: list[StockValueRow] = Field(default_factory=list)


class PurchaseOrderChartPoint(BaseModel):
    label: str
    spend: Decimal
    po_count: int


class PurchaseOrderSummaryRow(BaseModel):
    id: int
    created_at: datetime
    supplier_name: str | None
    status: str
    total: Decimal


class PurchaseOrdersReportResponse(BaseModel):
    period: str
    total_spend: Decimal
    po_count: int
    open_po_count: int
    open_po_value: Decimal
    chart: list[PurchaseOrderChartPoint]
    purchases: list[PurchaseOrderSummaryRow]


class LowStockRow(BaseModel):
    product_id: int
    sku: str
    name: str
    stock: int
    low_stock_threshold: int
    line_value: Decimal


class DeadStockRow(BaseModel):
    product_id: int
    sku: str
    name: str
    stock: int
    line_value: Decimal


class SellThroughRow(BaseModel):
    product_id: int
    sku: str
    name: str
    units_sold: int
    stock: int
    sell_through_pct: Decimal


class InventoryPerformanceReportResponse(BaseModel):
    low_stock_count: int
    dead_stock_value: Decimal
    total_stock_value: Decimal
    avg_turnover_ratio: Decimal
    low_stock_items: list[LowStockRow] = Field(default_factory=list)
    dead_stock_items: list[DeadStockRow] = Field(default_factory=list)
    sell_through_items: list[SellThroughRow] = Field(default_factory=list)
    open_po_count: int
    open_po_items: list[PurchaseOrderSummaryRow] = Field(default_factory=list)


class CashFlowChartPoint(BaseModel):
    label: str
    inbound: Decimal
    outbound: Decimal


class OutstandingDocumentRow(BaseModel):
    id: int
    party_name: str
    total: Decimal
    amount_paid: Decimal
    outstanding: Decimal


class VendorSpendRow(BaseModel):
    supplier_id: int | None
    supplier_name: str
    total_spend: Decimal
    po_count: int


class FinanceSummaryReportResponse(BaseModel):
    period: str
    payments_in: Decimal
    payments_out: Decimal
    ap_outstanding: Decimal
    ar_outstanding: Decimal
    revenue: Decimal
    cogs_approx: Decimal
    gross_margin_pct: Decimal
    chart: list[CashFlowChartPoint]
    ap_by_supplier: list[OutstandingDocumentRow] = Field(default_factory=list)
    po_spend_by_vendor: list[VendorSpendRow] = Field(default_factory=list)


class StatusCountRow(BaseModel):
    status: str
    count: int


class StageCountRow(BaseModel):
    stage: str
    count: int
    total_value: Decimal


class CustomerGrowthPoint(BaseModel):
    label: str
    count: int


class MarketingFunnelReportResponse(BaseModel):
    total_leads: int
    leads_by_status: list[StatusCountRow]
    total_opportunities: int
    opportunities_by_stage: list[StageCountRow]
    total_customers: int
    new_customers_30d: int
    customer_growth_chart: list[CustomerGrowthPoint]


class RoleSummaryRow(BaseModel):
    role_name: str
    user_count: int


class AgentRunStatusRow(BaseModel):
    run_type: str
    status: str
    count: int


class ItOverviewReportResponse(BaseModel):
    api_status: str
    db_status: str
    active_user_count: int
    role_count: int
    permission_count: int
    roles: list[RoleSummaryRow] = Field(default_factory=list)
    agent_runs: list[AgentRunStatusRow] = Field(default_factory=list)
