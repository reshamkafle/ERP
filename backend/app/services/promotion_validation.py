"""Shared promotion discount margin validation."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation


def margin_allows_discount(price: Decimal, cost: Decimal, discount_percent: float) -> bool:
    if price <= 0:
        return False
    try:
        floor = price * (Decimal(1) - Decimal(str(discount_percent)) / Decimal(100))
    except (InvalidOperation, ValueError):
        return False
    return floor >= cost


def validate_project_margins(
    project: dict,
    *,
    product_prices: dict[int, tuple[Decimal, Decimal]],
) -> None:
    """Raise ValueError when a discount would violate margin floor."""
    discount_kind = str(project.get("discount_kind") or "percent")
    if discount_kind != "percent":
        return
    pct = project.get("discount_percent")
    if pct is None:
        return
    try:
        discount_percent = float(pct)
    except (TypeError, ValueError) as exc:
        msg = "Invalid discount_percent"
        raise ValueError(msg) from exc
    if discount_percent < 0 or discount_percent > 100:
        msg = "discount_percent must be between 0 and 100"
        raise ValueError(msg)

    product_ids: set[int] = set()
    anchor = project.get("anchor") or {}
    if anchor.get("product_id") is not None:
        product_ids.add(int(anchor["product_id"]))
    for rel in project.get("related_items") or []:
        if isinstance(rel, dict) and rel.get("product_id") is not None:
            product_ids.add(int(rel["product_id"]))

    for pid in product_ids:
        price, cost = product_prices.get(pid, (Decimal(0), Decimal(0)))
        if not margin_allows_discount(price, cost, discount_percent):
            msg = f"Discount {discount_percent}% violates margin floor for product {pid}"
            raise ValueError(msg)
