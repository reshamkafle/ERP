"""API fallback for inventory types that are awkward to create via the multi-tab UI."""

from __future__ import annotations

import httpx


def create_inventory_item(
    api_client: httpx.Client,
    *,
    sku: str,
    name: str,
    item_type: str,
    initial_stock: int = 0,
    price: str = "0",
    cost_price: str = "0",
    low_stock_threshold: int = 1,
) -> dict:
    res = api_client.post(
        "/api/v1/inventory",
        json={
            "sku": sku,
            "name": name,
            "lifecycle_status": "ACTIVE",
            "item_type": item_type,
            "initial_stock": initial_stock,
            "price": price,
            "cost_price": cost_price,
            "low_stock_threshold": low_stock_threshold,
        },
    )
    res.raise_for_status()
    return res.json()
