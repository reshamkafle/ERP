from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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
