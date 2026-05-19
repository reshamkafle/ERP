"""LangGraph procurement: parallel specialists + supervisor merge (no DB in graph)."""

from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LineSuggestion(BaseModel):
    product_id: int = Field(ge=1)
    suggested_qty: int = Field(ge=1, le=10_000)
    rationale: str = ""


class SpecialistLines(BaseModel):
    lines: list[LineSuggestion] = Field(default_factory=list)


class SupervisorResult(BaseModel):
    lines: list[LineSuggestion] = Field(default_factory=list)
    merge_notes: str = ""


class ProcurementGraphState(TypedDict, total=False):
    signals: dict[str, Any]
    sales_lookback_days: int
    max_lines_per_supplier: int
    threshold_lines: list[dict[str, Any]]
    velocity_lines: list[dict[str, Any]]
    promotion_lines: list[dict[str, Any]]
    merged_lines: list[dict[str, Any]]
    merge_notes: str
    fallback_used: bool


def _product_lookup(signals: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for key in ("threshold_candidates", "velocity_candidates", "promotion_candidates"):
        for row in signals.get(key) or []:
            pid = int(row["product_id"])
            if pid not in out:
                out[pid] = {
                    "cost_price": row["cost_price"],
                    "default_supplier_id": row.get("default_supplier_id"),
                    "sku": row.get("sku", ""),
                }
    return out


def _llm() -> ChatOpenAI | None:
    settings = get_settings()
    if not settings.llm_base_url or not settings.llm_model:
        return None
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=settings.llm_base_url.rstrip("/"),
        api_key=settings.llm_api_key or "EMPTY",
        temperature=0.2,
    )


def _serialize_signals(signals_obj: Any) -> dict[str, Any]:
    """Turn ProcurementSignals dataclass into JSON-friendly dict."""
    from app.services.procurement_signals import (
        ProcurementSignals,
        PromotionProduct,
        ThresholdProduct,
        VelocityProduct,
    )

    if not isinstance(signals_obj, ProcurementSignals):
        raise TypeError("signals must be ProcurementSignals")

    def td(t: ThresholdProduct) -> dict[str, Any]:
        return {
            "product_id": t.product_id,
            "sku": t.sku,
            "name": t.name,
            "stock": t.stock,
            "low_stock_threshold": t.low_stock_threshold,
            "cost_price": str(t.cost_price),
            "default_supplier_id": t.default_supplier_id,
        }

    def vd(v: VelocityProduct) -> dict[str, Any]:
        return {
            "product_id": v.product_id,
            "sku": v.sku,
            "name": v.name,
            "quantity_sold": v.quantity_sold,
            "stock": v.stock,
            "cost_price": str(v.cost_price),
            "default_supplier_id": v.default_supplier_id,
        }

    def pd(p: PromotionProduct) -> dict[str, Any]:
        return {
            "product_id": p.product_id,
            "sku": p.sku,
            "name": p.name,
            "stock": p.stock,
            "cost_price": str(p.cost_price),
            "default_supplier_id": p.default_supplier_id,
        }

    return {
        "threshold_candidates": [td(t) for t in signals_obj.threshold_candidates],
        "velocity_candidates": [vd(v) for v in signals_obj.velocity_candidates],
        "promotion_candidates": [pd(p) for p in signals_obj.promotion_candidates],
    }


async def _specialist_threshold(state: ProcurementGraphState) -> dict[str, Any]:
    llm = _llm()
    signals = state["signals"]
    payload = json.dumps(signals.get("threshold_candidates", []), indent=2)
    if not signals.get("threshold_candidates"):
        return {"threshold_lines": []}
    if llm is None:
        return {"threshold_lines": []}
    try:
        structured = llm.with_structured_output(SpecialistLines)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a procurement specialist for reordering when stock is below "
                        "the configured low_stock_threshold. Propose integer purchase quantities "
                        "to restore healthy cover (avoid tiny orders). Output JSON lines only."
                    ),
                ),
                HumanMessage(
                    content=f"Below-threshold candidates (JSON):\n{payload}\n"
                    "Return lines: product_id, suggested_qty, rationale.",
                ),
            ],
        )
        return {"threshold_lines": [ln.model_dump() for ln in result.lines]}
    except Exception:
        logger.exception("threshold specialist LLM failed")
        return {"threshold_lines": [], "fallback_used": True}


async def _specialist_velocity(state: ProcurementGraphState) -> dict[str, Any]:
    llm = _llm()
    signals = state["signals"]
    payload = json.dumps(signals.get("velocity_candidates", []), indent=2)
    if not signals.get("velocity_candidates"):
        return {"velocity_lines": []}
    if llm is None:
        return {"velocity_lines": []}
    try:
        structured = llm.with_structured_output(SpecialistLines)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a procurement specialist focused on popular / high-velocity SKUs "
                        f"in the last {state.get('sales_lookback_days', 14)} days. "
                        "Suggest extra stock where sell-through warrants it. Cap reasonable quantities."
                    ),
                ),
                HumanMessage(
                    content=f"Velocity candidates (JSON):\n{payload}\n"
                    "Return lines: product_id, suggested_qty, rationale.",
                ),
            ],
        )
        return {"velocity_lines": [ln.model_dump() for ln in result.lines]}
    except Exception:
        logger.exception("velocity specialist LLM failed")
        return {"velocity_lines": [], "fallback_used": True}


async def _specialist_promotion(state: ProcurementGraphState) -> dict[str, Any]:
    llm = _llm()
    signals = state["signals"]
    payload = json.dumps(signals.get("promotion_candidates", []), indent=2)
    if not signals.get("promotion_candidates"):
        return {"promotion_lines": []}
    if llm is None:
        return {"promotion_lines": []}
    try:
        structured = llm.with_structured_output(SpecialistLines)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a procurement specialist for promotional / high-merchandising "
                        "priority SKUs (promotion_reorder_boost). Suggest quantities so stores "
                        "do not stock out during campaigns."
                    ),
                ),
                HumanMessage(
                    content=f"Promotion-boost candidates (JSON):\n{payload}\n"
                    "Return lines: product_id, suggested_qty, rationale.",
                ),
            ],
        )
        return {"promotion_lines": [ln.model_dump() for ln in result.lines]}
    except Exception:
        logger.exception("promotion specialist LLM failed")
        return {"promotion_lines": [], "fallback_used": True}


def _deterministic_fallback_merge(state: ProcurementGraphState) -> list[dict[str, Any]]:
    signals = state["signals"]
    lookup = _product_lookup(signals)
    merged: list[dict[str, Any]] = []
    seen: set[int] = set()

    for row in signals.get("threshold_candidates", []):
        pid = int(row["product_id"])
        if pid in seen:
            continue
        seen.add(pid)
        stock = int(row["stock"])
        low = max(1, int(row["low_stock_threshold"]))
        qty = max(1, low * 2 - stock)
        info = lookup.get(pid, row)
        sup = info.get("default_supplier_id")
        if sup is None:
            continue
        merged.append(
            {
                "product_id": pid,
                "suggested_qty": min(qty, 10_000),
                "unit_cost": str(row["cost_price"]),
                "default_supplier_id": int(sup),
                "rationale": "Rule fallback: below threshold reorder",
            },
        )

    for key, qty_fn in (
        ("velocity_candidates", lambda r: max(1, min(int(r["quantity_sold"]) // 2, 200))),
        ("promotion_candidates", lambda r: max(1, max(1, int(r.get("stock", 0))) + 12)),
    ):
        for row in signals.get(key, []):
            pid = int(row["product_id"])
            if pid in seen:
                continue
            seen.add(pid)
            sup = row.get("default_supplier_id")
            if sup is None:
                continue
            merged.append(
                {
                    "product_id": pid,
                    "suggested_qty": min(qty_fn(row), 10_000),
                    "unit_cost": str(row["cost_price"]),
                    "default_supplier_id": int(sup),
                    "rationale": f"Rule fallback from {key}",
                },
            )
    return merged


def _enrich_lines(raw: list[dict[str, Any]], lookup: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw:
        pid = int(row["product_id"])
        qty = int(row["suggested_qty"])
        info = lookup.get(pid)
        if info is None or info.get("default_supplier_id") is None:
            continue
        out.append(
            {
                "product_id": pid,
                "suggested_qty": qty,
                "unit_cost": str(row.get("unit_cost") or info["cost_price"]),
                "default_supplier_id": int(info["default_supplier_id"]),
                "rationale": row.get("rationale", ""),
            },
        )
    return out


async def _supervisor(state: ProcurementGraphState) -> dict[str, Any]:
    llm = _llm()
    lookup = _product_lookup(state["signals"])

    parts = {
        "threshold": state.get("threshold_lines") or [],
        "velocity": state.get("velocity_lines") or [],
        "promotion": state.get("promotion_lines") or [],
    }
    fallback_used = bool(state.get("fallback_used"))

    if llm is None or not any(parts.values()):
        merged = _deterministic_fallback_merge(state)
        return {
            "merged_lines": merged[: state.get("max_lines_per_supplier", 50) * 20],
            "merge_notes": "Deterministic merge (LLM unavailable or specialists empty).",
            "fallback_used": True,
        }

    try:
        structured = llm.with_structured_output(SupervisorResult)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You merge procurement suggestions from three specialists into one list. "
                        "Rules: one line per product_id; choose a single sensible suggested_qty "
                        "(prefer the highest defensible qty capped at 500); dedupe. "
                        "You may drop weak suggestions."
                    ),
                ),
                HumanMessage(
                    content=json.dumps(parts, indent=2),
                ),
            ],
        )
        raw = [ln.model_dump() for ln in result.lines]
        merged = _enrich_lines(raw, lookup)
        if not merged:
            merged = _deterministic_fallback_merge(state)
            fallback_used = True
            notes = (result.merge_notes or "") + " | Fell back to rules (supervisor empty)."
        else:
            notes = result.merge_notes or ""
        return {
            "merged_lines": merged[: 500],
            "merge_notes": notes,
            "fallback_used": fallback_used,
        }
    except Exception:
        logger.exception("supervisor LLM failed")
        merged = _deterministic_fallback_merge(state)
        return {
            "merged_lines": merged[: 500],
            "merge_notes": "Supervisor LLM failed; used rule-based merge.",
            "fallback_used": True,
        }


def build_procurement_graph() -> Any:
    g = StateGraph(ProcurementGraphState)
    g.add_node("specialist_threshold", _specialist_threshold)
    g.add_node("specialist_velocity", _specialist_velocity)
    g.add_node("specialist_promotion", _specialist_promotion)
    g.add_node("supervisor", _supervisor)

    g.add_edge(START, "specialist_threshold")
    g.add_edge(START, "specialist_velocity")
    g.add_edge(START, "specialist_promotion")
    g.add_edge("specialist_threshold", "supervisor")
    g.add_edge("specialist_velocity", "supervisor")
    g.add_edge("specialist_promotion", "supervisor")
    g.add_edge("supervisor", END)
    return g.compile()


async def run_procurement_graph(
    *,
    signals: Any,
    sales_lookback_days: int,
    max_lines_per_supplier: int,
) -> ProcurementGraphState:
    from app.services.procurement_signals import ProcurementSignals

    if not isinstance(signals, ProcurementSignals):
        raise TypeError("signals must be ProcurementSignals")

    graph = build_procurement_graph()
    initial: ProcurementGraphState = {
        "signals": _serialize_signals(signals),
        "sales_lookback_days": sales_lookback_days,
        "max_lines_per_supplier": max_lines_per_supplier,
    }
    return await graph.ainvoke(initial)
