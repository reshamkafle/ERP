from unittest.mock import patch

import pytest

from app.agents.procurement_graph import run_procurement_graph
from app.agents.promotion_graph import run_promotion_graph
from app.testing.agent_signals import make_procurement_signals, make_promotion_signals
from tests.mocks.fake_llm import (
    build_procurement_fake_llm,
    build_procurement_failing_llm,
    build_promotion_fake_llm,
    build_promotion_failing_llm,
)


@pytest.mark.asyncio
@patch("app.agents.procurement_graph._llm", return_value=build_procurement_fake_llm())
async def test_procurement_supervisor_uses_llm_merge(_mock_llm: object) -> None:
    out = await run_procurement_graph(
        signals=make_procurement_signals(),
        sales_lookback_days=14,
        max_lines_per_supplier=50,
    )
    merged = out.get("merged_lines") or []
    product_ids = {int(row["product_id"]) for row in merged}
    assert product_ids <= {1, 2, 3}
    assert len(merged) >= 1
    assert out.get("fallback_used") is False
    assert "Mock LLM" in (out.get("merge_notes") or "")


@pytest.mark.asyncio
@patch("app.agents.procurement_graph._llm", return_value=build_procurement_failing_llm())
async def test_procurement_supervisor_llm_failure_falls_back(_mock_llm: object) -> None:
    out = await run_procurement_graph(
        signals=make_procurement_signals(),
        sales_lookback_days=14,
        max_lines_per_supplier=50,
    )
    merged = out.get("merged_lines") or []
    assert len(merged) >= 1
    assert out.get("fallback_used") is True
    assert "failed" in (out.get("merge_notes") or "").lower()


@pytest.mark.asyncio
@patch("app.agents.promotion_graph._llm", return_value=build_promotion_fake_llm())
async def test_promotion_graph_mock_llm_path(_mock_llm: object) -> None:
    out = await run_promotion_graph(
        signals=make_promotion_signals(bundle_count=2),
        max_projects=10,
    )
    merged = out.get("merged_projects") or []
    assert len(merged) >= 1
    assert out.get("fallback_used") is False
    assert "Mock" in (out.get("merge_notes") or "")


@pytest.mark.asyncio
@patch("app.agents.promotion_graph._llm", return_value=build_promotion_failing_llm())
async def test_promotion_supervisor_llm_failure_falls_back(_mock_llm: object) -> None:
    out = await run_promotion_graph(
        signals=make_promotion_signals(bundle_count=2),
        max_projects=10,
    )
    merged = out.get("merged_projects") or []
    assert len(merged) >= 1
    assert out.get("fallback_used") is True
    assert "failed" in (out.get("merge_notes") or "").lower() or "Deterministic" in (
        out.get("merge_notes") or ""
    )
