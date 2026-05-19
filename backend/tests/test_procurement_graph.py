import pytest

from app.agents.procurement_graph import run_procurement_graph
from app.testing.agent_signals import make_procurement_signals


@pytest.mark.asyncio
async def test_procurement_graph_rule_fallback_below_threshold() -> None:
    signals_obj = make_procurement_signals()
    signals_obj.threshold_candidates = signals_obj.threshold_candidates[:1]
    signals_obj.velocity_candidates = []
    signals_obj.promotion_candidates = []

    out = await run_procurement_graph(
        signals=signals_obj,
        sales_lookback_days=14,
        max_lines_per_supplier=50,
    )
    merged = out.get("merged_lines") or []
    assert len(merged) == 1
    assert merged[0]["product_id"] == 1
    assert merged[0]["default_supplier_id"] == 99
    assert int(merged[0]["suggested_qty"]) >= 1


@pytest.mark.asyncio
async def test_procurement_graph_merges_all_three_specialists() -> None:
    out = await run_procurement_graph(
        signals=make_procurement_signals(),
        sales_lookback_days=14,
        max_lines_per_supplier=50,
    )
    merged = out.get("merged_lines") or []
    product_ids = {int(row["product_id"]) for row in merged}
    assert product_ids >= {1, 2, 3}


@pytest.mark.asyncio
async def test_procurement_graph_skips_no_supplier() -> None:
    out = await run_procurement_graph(
        signals=make_procurement_signals(include_no_supplier=True),
        sales_lookback_days=14,
        max_lines_per_supplier=50,
    )
    merged = out.get("merged_lines") or []
    assert all(int(row["product_id"]) != 99 for row in merged)
    assert all(row.get("default_supplier_id") is not None for row in merged)
