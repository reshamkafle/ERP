import pytest

from app.agents.promotion_graph import run_promotion_graph
from app.testing.agent_signals import make_promotion_signals


@pytest.mark.asyncio
async def test_promotion_graph_rule_fallback_chain() -> None:
    out = await run_promotion_graph(signals=make_promotion_signals(bundle_count=1), max_projects=10)
    merged = out.get("merged_projects") or []
    assert len(merged) == 1
    proj = merged[0]
    assert proj.get("anchor", {}).get("product_id") == 1
    rel = proj.get("related_items") or []
    assert len(rel) == 1
    assert rel[0]["product_id"] == 2
    assert float(rel[0].get("discount_percent") or 0) >= 0
    assert int(rel[0].get("duration_days") or 0) >= 1


@pytest.mark.asyncio
async def test_promotion_graph_empty_bundles() -> None:
    signals_obj = make_promotion_signals(bundle_count=0)
    signals_obj.bundle_candidates = []
    signals_obj.warnings = ["no data"]
    out = await run_promotion_graph(signals=signals_obj, max_projects=5)
    assert (out.get("merged_projects") or []) == []


@pytest.mark.asyncio
async def test_promotion_graph_multiple_bundles() -> None:
    out = await run_promotion_graph(signals=make_promotion_signals(bundle_count=2), max_projects=10)
    merged = out.get("merged_projects") or []
    assert len(merged) >= 2


@pytest.mark.asyncio
async def test_promotion_graph_margin_floor() -> None:
    out = await run_promotion_graph(signals=make_promotion_signals(bundle_count=1), max_projects=5)
    for proj in out.get("merged_projects") or []:
        for rel in proj.get("related_items") or []:
            assert float(rel.get("discount_percent") or 0) >= 0
            assert int(rel.get("duration_days") or 0) >= 1
