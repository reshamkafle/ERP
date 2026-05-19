"""Fixture factories for procurement and promotion agent graph tests."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.services.procurement_signals import (
    ProcurementSignals,
    PromotionProduct,
    ThresholdProduct,
    VelocityProduct,
)
from app.services.promotion_signals import PromotionSignals


def _product_snapshot(
    *,
    product_id: int,
    sku: str,
    name: str,
    price: str = "20.00",
    cost_price: str = "8.00",
    stock: int = 5,
    category_id: int = 1,
    product_line: str = "DemoLine",
    sub_category: str | None = None,
) -> dict[str, Any]:
    return {
        "product_id": product_id,
        "sku": sku,
        "name": name,
        "price": price,
        "cost_price": cost_price,
        "stock": stock,
        "category_id": category_id,
        "product_line": product_line,
        "sub_category": sub_category,
    }


def make_procurement_signals(
    *,
    include_no_supplier: bool = False,
    warnings: list[str] | None = None,
) -> ProcurementSignals:
    """Signals that exercise threshold, velocity, and promotion specialists."""
    threshold = [
        ThresholdProduct(
            product_id=1,
            sku="DEMO-THR",
            name="Low Stock Widget",
            stock=2,
            low_stock_threshold=10,
            cost_price=Decimal("5.00"),
            default_supplier_id=99,
        ),
    ]
    velocity = [
        VelocityProduct(
            product_id=2,
            sku="DEMO-VEL",
            name="Fast Seller",
            quantity_sold=40,
            stock=8,
            cost_price=Decimal("6.00"),
            default_supplier_id=99,
        ),
    ]
    promotion = [
        PromotionProduct(
            product_id=3,
            sku="DEMO-PRM",
            name="Promo Boost SKU",
            stock=4,
            cost_price=Decimal("7.00"),
            default_supplier_id=99,
        ),
    ]
    if include_no_supplier:
        threshold.append(
            ThresholdProduct(
                product_id=99,
                sku="DEMO-NOSUP",
                name="No Supplier Item",
                stock=1,
                low_stock_threshold=5,
                cost_price=Decimal("3.00"),
                default_supplier_id=None,
            ),
        )
    return ProcurementSignals(
        threshold_candidates=threshold,
        velocity_candidates=velocity,
        promotion_candidates=promotion,
        warnings=list(warnings or []),
    )


def make_promotion_signals(
    *,
    bundle_count: int = 2,
    warnings: list[str] | None = None,
) -> PromotionSignals:
    """Two+ bundle candidates for multi-project supervisor merge."""
    bundles: list[dict[str, Any]] = []
    pairs = [
        (1, "DEMO-ANCHOR-A", "Anchor Alpha", 2, "DEMO-REL-A1", "Related Alpha"),
        (4, "DEMO-ANCHOR-B", "Anchor Beta", 5, "DEMO-REL-B1", "Related Beta"),
        (7, "DEMO-ANCHOR-C", "Anchor Gamma", 8, "DEMO-REL-C1", "Related Gamma"),
    ]
    for i, (aid, asku, aname, rid, rsku, rname) in enumerate(pairs[: max(1, bundle_count)]):
        bundles.append(
            {
                "anchor": _product_snapshot(
                    product_id=aid,
                    sku=asku,
                    name=aname,
                    price="25.00",
                    cost_price="10.00",
                ),
                "related": [
                    _product_snapshot(
                        product_id=rid,
                        sku=rsku,
                        name=rname,
                        price="12.00",
                        cost_price="5.00",
                    ),
                ],
                "affinity_note": f"Co-purchase pair {i + 1}",
            },
        )
    return PromotionSignals(bundle_candidates=bundles, warnings=list(warnings or []))
