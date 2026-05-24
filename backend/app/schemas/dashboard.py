from decimal import Decimal

from pydantic import BaseModel, Field


class DocumentFlowChartPoint(BaseModel):
    label: str
    count: int


class DocumentFlowCardMetrics(BaseModel):
    id: str
    total: int
    new_count: int
    chart: list[DocumentFlowChartPoint] = Field(default_factory=list)


class DocumentFlowMetricsResponse(BaseModel):
    period: str
    new_days: int
    cards: list[DocumentFlowCardMetrics]


class ManagerOverviewChartPoint(BaseModel):
    label: str
    revenue: Decimal
    purchase_spend: Decimal


class ExceptionAlertRow(BaseModel):
    severity: str
    category: str
    message: str


class ManagerOverviewResponse(BaseModel):
    period: str
    total_revenue: Decimal
    total_purchase_spend: Decimal
    inventory_value: Decimal
    low_stock_count: int
    open_po_count: int
    chart: list[ManagerOverviewChartPoint] = Field(default_factory=list)
    alerts: list[ExceptionAlertRow] = Field(default_factory=list)
