"""Read-only API helpers to resolve ids after Selenium UI creates (no creates here)."""

from __future__ import annotations

import httpx


def product_id_by_sku(api_client: httpx.Client, sku: str) -> int:
    res = api_client.get("/api/v1/inventory", params={"search": sku, "limit": 5})
    res.raise_for_status()
    items = res.json().get("items") or []
    for item in items:
        if item.get("sku") == sku:
            return int(item["id"])
    raise LookupError(f"Product not found for SKU {sku}")
