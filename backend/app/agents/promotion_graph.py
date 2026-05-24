"""LangGraph promotion: relations specialist -> pricing specialist -> supervisor merge."""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RelatedItemOut(BaseModel):
    product_id: int = Field(ge=1)
    sku: str = ""
    name: str = ""
    relationship_note: str = ""


class RelationProjectOut(BaseModel):
    project_id: str = ""
    anchor_product_id: int = Field(ge=1)
    related_items: list[RelatedItemOut] = Field(default_factory=list)
    rationale: str = ""
    confidence: str = "medium"


class RelationSpecialistResult(BaseModel):
    projects: list[RelationProjectOut] = Field(default_factory=list)


class PricingLineOut(BaseModel):
    product_id: int = Field(ge=1)
    sku: str = ""
    name: str = ""
    discount_kind: str = Field(description="percent or fixed")
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    discount_amount: str | None = Field(default=None, description="Decimal string for fixed off")
    duration_days: int = Field(ge=1, le=365, default=14)
    rationale: str = ""


class PricingProjectOut(BaseModel):
    project_id: str = ""
    anchor_product_id: int = Field(ge=1)
    lines: list[PricingLineOut] = Field(default_factory=list)
    confidence: str = "medium"


class PricingSpecialistResult(BaseModel):
    projects: list[PricingProjectOut] = Field(default_factory=list)


class SupervisorProjectOut(BaseModel):
    project_id: str = ""
    anchor: dict[str, Any] = Field(default_factory=dict)
    related_items: list[dict[str, Any]] = Field(default_factory=list)
    discount_kind: str = "percent"
    discount_percent: float | None = None
    discount_amount: str | None = None
    duration_days: int = 14
    start_date: str | None = None
    end_date: str | None = None
    rationale: str = ""
    confidence: str = "medium"


class SupervisorResult(BaseModel):
    projects: list[SupervisorProjectOut] = Field(default_factory=list)
    merge_notes: str = ""


class PromotionGraphState(TypedDict, total=False):
    signals: dict[str, Any]
    max_projects: int
    relation_projects: list[dict[str, Any]]
    pricing_projects: list[dict[str, Any]]
    merged_projects: list[dict[str, Any]]
    merge_notes: str
    fallback_used: bool


def _llm() -> ChatOpenAI | None:
    from app.core.llm_url import validate_llm_base_url

    settings = get_settings()
    if not settings.llm_base_url or not settings.llm_model:
        return None
    try:
        base_url = validate_llm_base_url(settings.llm_base_url)
    except ValueError as exc:
        logger.warning("Invalid LLM_BASE_URL: %s", exc)
        return None
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=base_url,
        api_key=settings.llm_api_key or "EMPTY",
        temperature=0.2,
    )


def _lookup_from_signals(signals: dict[str, Any]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for bc in signals.get("bundle_candidates") or []:
        a = bc.get("anchor") or {}
        pid = int(a["product_id"])
        out[pid] = dict(a)
        for r in bc.get("related") or []:
            rid = int(r["product_id"])
            if rid not in out:
                out[rid] = dict(r)
    return out


def _fallback_relation_projects(signals: dict[str, Any]) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []
    for bc in signals.get("bundle_candidates") or []:
        anchor = bc.get("anchor") or {}
        if not anchor.get("product_id"):
            continue
        aid = int(anchor["product_id"])
        rel = bc.get("related") or []
        projects.append(
            {
                "project_id": f"rel-{aid}-{uuid.uuid4().hex[:8]}",
                "anchor_product_id": aid,
                "related_items": [
                    {
                        "product_id": int(r["product_id"]),
                        "sku": r.get("sku", ""),
                        "name": r.get("name", ""),
                        "relationship_note": bc.get("affinity_note", "Related item."),
                    }
                    for r in rel
                    if r.get("product_id") is not None
                ],
                "rationale": "Deterministic bundle from sales affinity and category / line neighbors.",
                "confidence": "medium",
            },
        )
    return projects


def _margin_ok(price: Decimal, cost: Decimal, discount_percent: float) -> bool:
    if price <= 0:
        return False
    try:
        floor = price * (Decimal(1) - Decimal(str(discount_percent)) / Decimal(100))
    except Exception:
        return False
    return floor >= cost


def _fallback_pricing_projects(
    relation_projects: list[dict[str, Any]],
    lookup: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for proj in relation_projects:
        aid = int(proj["anchor_product_id"])
        anchor = lookup.get(aid, {})
        lines: list[dict[str, Any]] = []
        for rel in proj.get("related_items") or []:
            rid = int(rel["product_id"])
            meta = lookup.get(rid, {})
            price = Decimal(str(meta.get("price", "0") or "0"))
            cost = Decimal(str(meta.get("cost_price", "0") or "0"))
            pct = 10.0
            if not _margin_ok(price, cost, pct):
                pct = 5.0
            if not _margin_ok(price, cost, pct):
                pct = 0.0
            lines.append(
                {
                    "product_id": rid,
                    "sku": rel.get("sku") or meta.get("sku", ""),
                    "name": rel.get("name") or meta.get("name", ""),
                    "discount_kind": "percent" if pct > 0 else "fixed",
                    "discount_percent": pct if pct > 0 else None,
                    "discount_amount": None if pct > 0 else "0",
                    "duration_days": 14,
                    "rationale": proj.get("rationale", "")[:200],
                },
            )
        out.append(
            {
                "project_id": proj.get("project_id", ""),
                "anchor_product_id": aid,
                "lines": lines,
                "confidence": proj.get("confidence", "medium"),
            },
        )
    return out


def _flatten_supervisor(
    pricing_projects: list[dict[str, Any]],
    relation_projects: list[dict[str, Any]],
    lookup: dict[int, dict[str, Any]],
    max_projects: int,
) -> list[dict[str, Any]]:
    """Deterministic merge when LLM supervisor unavailable."""
    by_id: dict[str, dict[str, Any]] = {}
    rel_by_pid = {int(p["anchor_product_id"]): p for p in relation_projects}
    for pp in pricing_projects:
        pid_key = pp.get("project_id") or f"pp-{pp['anchor_product_id']}"
        aid = int(pp["anchor_product_id"])
        anchor = dict(lookup.get(aid, {}))
        rel_meta = rel_by_pid.get(aid, {})
        related_items: list[dict[str, Any]] = []
        for ln in pp.get("lines") or []:
            rid = int(ln["product_id"])
            rlook = lookup.get(rid, {})
            related_items.append(
                {
                    "product_id": rid,
                    "sku": ln.get("sku") or rlook.get("sku", ""),
                    "name": ln.get("name") or rlook.get("name", ""),
                    "discount_kind": ln.get("discount_kind", "percent"),
                    "discount_percent": ln.get("discount_percent"),
                    "discount_amount": ln.get("discount_amount"),
                    "duration_days": int(ln.get("duration_days", 14)),
                    "rationale": (ln.get("rationale") or "") + " " + (rel_meta.get("rationale", "")),
                    "confidence": pp.get("confidence", "medium"),
                },
            )
        by_id[pid_key] = {
            "project_id": pid_key,
            "anchor": anchor,
            "related_items": related_items,
            "discount_kind": "percent",
            "discount_percent": None,
            "discount_amount": None,
            "duration_days": max((int(x.get("duration_days", 14)) for x in related_items), default=14),
            "start_date": None,
            "end_date": None,
            "rationale": (rel_meta.get("rationale", "") or "Promotion bundle.")[:500],
            "confidence": pp.get("confidence", "medium"),
        }
    merged = list(by_id.values())[:max(1, max_projects)]
    return merged


async def _specialist_relations(state: PromotionGraphState) -> dict[str, Any]:
    signals = state.get("signals") or {}
    bundles = signals.get("bundle_candidates") or []
    if not bundles:
        return {"relation_projects": [], "fallback_used": True}

    llm = _llm()
    if llm is None:
        return {"relation_projects": _fallback_relation_projects(signals), "fallback_used": True}

    try:
        structured = llm.with_structured_output(RelationSpecialistResult)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a retail merchandising specialist. From bundle_candidates (JSON), "
                        "produce promotion projects: each has anchor_product_id, related_items with "
                        "product_id/sku/name/relationship_note, rationale, confidence. "
                        "Keep related_items tight (cross-sell complements). Drop weak pairs."
                    ),
                ),
                HumanMessage(content=json.dumps({"bundle_candidates": bundles}, indent=2)),
            ],
        )
        raw = [p.model_dump() for p in result.projects]
        if not raw:
            return {"relation_projects": _fallback_relation_projects(signals), "fallback_used": True}
        return {"relation_projects": raw, "fallback_used": False}
    except Exception:
        logger.exception("relation specialist LLM failed")
        return {"relation_projects": _fallback_relation_projects(signals), "fallback_used": True}


async def _specialist_pricing(state: PromotionGraphState) -> dict[str, Any]:
    relation_projects = state.get("relation_projects") or []
    if not relation_projects:
        return {"pricing_projects": []}

    lookup = _lookup_from_signals(state.get("signals") or {})
    llm = _llm()
    if llm is None:
        return {
            "pricing_projects": _fallback_pricing_projects(relation_projects, lookup),
            "fallback_used": bool(state.get("fallback_used", True)),
        }

    try:
        structured = llm.with_structured_output(PricingSpecialistResult)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You set customer-facing promotion terms for related SKUs. "
                        "Use discount_kind percent or fixed. Respect margin: discounted price should "
                        "not go below cost_price from catalog hints in the JSON. "
                        "duration_days 1-90 typical. One PricingProjectOut per relation project; "
                        "lines align with related SKUs."
                    ),
                ),
                HumanMessage(
                    content=json.dumps(
                        {"catalog": lookup, "relation_projects": relation_projects},
                        indent=2,
                    ),
                ),
            ],
        )
        raw = [p.model_dump() for p in result.projects]
        if not raw:
            return {
                "pricing_projects": _fallback_pricing_projects(relation_projects, lookup),
                "fallback_used": True,
            }
        return {"pricing_projects": raw, "fallback_used": bool(state.get("fallback_used", False))}
    except Exception:
        logger.exception("pricing specialist LLM failed")
        return {
            "pricing_projects": _fallback_pricing_projects(relation_projects, lookup),
            "fallback_used": True,
        }


async def _supervisor(state: PromotionGraphState) -> dict[str, Any]:
    pricing_projects = state.get("pricing_projects") or []
    relation_projects = state.get("relation_projects") or []
    lookup = _lookup_from_signals(state.get("signals") or {})
    max_projects = int(state.get("max_projects", 30))

    if not pricing_projects:
        return {"merged_projects": [], "merge_notes": "No pricing projects.", "fallback_used": True}

    llm = _llm()
    if llm is None:
        merged = _flatten_supervisor(pricing_projects, relation_projects, lookup, max_projects)
        return {
            "merged_projects": merged,
            "merge_notes": "Deterministic supervisor merge (LLM disabled).",
            "fallback_used": True,
        }

    try:
        structured = llm.with_structured_output(SupervisorResult)
        result = await structured.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You merge promotion projects into a final list for manager review. "
                        "Each project: project_id, anchor (product dict), related_items (each item "
                        "includes discount_kind, discount_percent or discount_amount, duration_days, "
                        "rationale, confidence), top-level discount summary optional, merge_notes. "
                        f"Cap at {max_projects} projects; dedupe by anchor."
                    ),
                ),
                HumanMessage(
                    content=json.dumps(
                        {"pricing_projects": pricing_projects, "relation_projects": relation_projects},
                        indent=2,
                    ),
                ),
            ],
        )
        merged: list[dict[str, Any]] = []
        for p in result.projects:
            d = p.model_dump()
            merged.append(d)
        merged = merged[:max_projects]
        if not merged:
            merged = _flatten_supervisor(pricing_projects, relation_projects, lookup, max_projects)
            return {
                "merged_projects": merged,
                "merge_notes": (result.merge_notes or "") + " | Used rule fallback (empty supervisor).",
                "fallback_used": True,
            }
        return {
            "merged_projects": merged,
            "merge_notes": result.merge_notes or "",
            "fallback_used": bool(state.get("fallback_used", False)),
        }
    except Exception:
        logger.exception("supervisor LLM failed")
        merged = _flatten_supervisor(pricing_projects, relation_projects, lookup, max_projects)
        return {
            "merged_projects": merged,
            "merge_notes": "Supervisor LLM failed; used deterministic merge.",
            "fallback_used": True,
        }


def build_promotion_graph() -> Any:
    g = StateGraph(PromotionGraphState)
    g.add_node("specialist_relations", _specialist_relations)
    g.add_node("specialist_pricing", _specialist_pricing)
    g.add_node("supervisor", _supervisor)
    g.add_edge(START, "specialist_relations")
    g.add_edge("specialist_relations", "specialist_pricing")
    g.add_edge("specialist_pricing", "supervisor")
    g.add_edge("supervisor", END)
    return g.compile()


def _serialize_signals(signals_obj: Any) -> dict[str, Any]:
    from app.services.promotion_signals import PromotionSignals

    if not isinstance(signals_obj, PromotionSignals):
        raise TypeError("signals must be PromotionSignals")
    return {
        "bundle_candidates": list(signals_obj.bundle_candidates),
        "warnings": list(signals_obj.warnings),
    }


async def run_promotion_graph(
    *,
    signals: Any,
    max_projects: int,
) -> PromotionGraphState:
    from app.services.promotion_signals import PromotionSignals

    if not isinstance(signals, PromotionSignals):
        raise TypeError("signals must be PromotionSignals")

    graph = build_promotion_graph()
    initial: PromotionGraphState = {
        "signals": _serialize_signals(signals),
        "max_projects": max_projects,
    }
    return await graph.ainvoke(initial)
