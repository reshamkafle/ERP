from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.services.tax_calculation import line_tax_amount


@dataclass
class LineCalcInput:
    product: Product
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    tax_rate_id: int | None = None


@dataclass
class LineCalcResult:
    gross: Decimal
    discount: Decimal
    net: Decimal
    tax: Decimal
    line_total: Decimal


def _line_discount(gross: Decimal, discount_percent: Decimal, discount_amount: Decimal) -> Decimal:
    pct_discount = (gross * discount_percent / Decimal("100")).quantize(Decimal("0.01"))
    return min(gross, pct_discount + discount_amount)


async def calc_line(
    db: AsyncSession,
    line: LineCalcInput,
    *,
    as_of: date | None = None,
) -> LineCalcResult:
    gross = (line.unit_price * line.quantity).quantize(Decimal("0.01"))
    discount = _line_discount(gross, line.discount_percent, line.discount_amount)
    net = gross - discount
    tax = await line_tax_amount(db, product=line.product, line_subtotal=net, as_of=as_of)
    line_total = net + tax
    return LineCalcResult(gross=gross, discount=discount, net=net, tax=tax, line_total=line_total)


async def calc_sale_totals(
    db: AsyncSession,
    *,
    lines: list[LineCalcInput],
    header_discount_amount: Decimal = Decimal("0"),
    freight_amount: Decimal = Decimal("0"),
    insurance_amount: Decimal = Decimal("0"),
    handling_amount: Decimal = Decimal("0"),
    as_of: date | None = None,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    gross_total = Decimal("0")
    line_discount_total = Decimal("0")
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for line in lines:
        result = await calc_line(db, line, as_of=as_of)
        gross_total += result.gross
        line_discount_total += result.discount
        subtotal += result.net
        tax_total += result.tax
    subtotal = max(Decimal("0"), subtotal - header_discount_amount)
    total_discount = line_discount_total + header_discount_amount
    total = subtotal + tax_total + freight_amount + insurance_amount + handling_amount
    return gross_total, subtotal, tax_total, total, total_discount


def build_order_summary(sale) -> dict:
    total_items = len(sale.items)
    total_quantity = sum(item.quantity for item in sale.items)
    line_discount = sum(
        (item.unit_price * item.quantity).quantize(Decimal("0.01")) - item.net_amount
        for item in sale.items
    )
    total_discount = line_discount + sale.header_discount_amount
    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_net": sale.subtotal,
        "total_tax": sale.tax_amount,
        "total_discount": total_discount.quantize(Decimal("0.01")),
        "freight": sale.freight_amount,
        "insurance": sale.insurance_amount,
        "handling": sale.handling_amount,
        "grand_total": sale.total,
    }
