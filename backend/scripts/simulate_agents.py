#!/usr/bin/env python3
"""Simulate procurement and promotion LangGraph agents (fixtures, mock LLM, or DB)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.procurement_graph import run_procurement_graph
from app.agents.promotion_graph import run_promotion_graph
from app.core.database import AsyncSessionLocal, init_db
from app.schemas.procurement import ProcurementRunCreateBody
from app.schemas.promotion import PromotionRunCreateBody
from app.services.procurement_runner import execute_procurement_run
from app.services.procurement_signals import fetch_procurement_signals
from app.services.promotion_runner import execute_promotion_run
from app.services.promotion_signals import fetch_promotion_signals
from app.testing.agent_signals import make_procurement_signals, make_promotion_signals
from app.testing.seed_agent_demo import seed_agent_demo_data
from sqlalchemy import select

from app.core.bootstrap import seed_admin_user
from app.models.user import User, UserRole
from tests.mocks.fake_llm import build_procurement_fake_llm, build_promotion_fake_llm


def _summarize_procurement(out: dict[str, Any]) -> dict[str, Any]:
    lines = out.get("merged_lines") or []
    return {
        "agent": "procurement",
        "line_count": len(lines),
        "sample": lines[:3],
        "merge_notes": out.get("merge_notes"),
        "fallback_used": out.get("fallback_used"),
    }


def _summarize_promotion(out: dict[str, Any]) -> dict[str, Any]:
    projects = out.get("merged_projects") or []
    return {
        "agent": "promotion",
        "project_count": len(projects),
        "sample": projects[:2],
        "merge_notes": out.get("merge_notes"),
        "fallback_used": out.get("fallback_used"),
    }


async def _run_graphs(
    *,
    use_mock_llm: bool,
    procurement_signals: Any,
    promotion_signals: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    proc_patch = patch("app.agents.procurement_graph._llm", return_value=build_procurement_fake_llm())
    prom_patch = patch("app.agents.promotion_graph._llm", return_value=build_promotion_fake_llm())

    if use_mock_llm:
        with proc_patch, prom_patch:
            proc_out = await run_procurement_graph(
                signals=procurement_signals,
                sales_lookback_days=14,
                max_lines_per_supplier=50,
            )
            prom_out = await run_promotion_graph(
                signals=promotion_signals,
                max_projects=10,
            )
    else:
        proc_out = await run_procurement_graph(
            signals=procurement_signals,
            sales_lookback_days=14,
            max_lines_per_supplier=50,
        )
        prom_out = await run_promotion_graph(
            signals=promotion_signals,
            max_projects=10,
        )
    return proc_out, prom_out


async def _run_with_db(*, use_mock_llm: bool, persist: bool) -> dict[str, Any]:
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
        seed_result = await seed_agent_demo_data(session)
        await session.commit()

        admin = (
            await session.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))
        ).scalar_one_or_none()
        if admin is None:
            msg = "No admin user found; run backend once or seed_agent_demo.py"
            raise RuntimeError(msg)

        proc_signals = await fetch_procurement_signals(session, sales_lookback_days=14, velocity_limit=30)
        prom_signals = await fetch_promotion_signals(
            session,
            sales_lookback_days=30,
            max_anchor_products=15,
            max_related_per_anchor=5,
        )

        proc_graph, prom_graph = await _run_graphs(
            use_mock_llm=use_mock_llm,
            procurement_signals=proc_signals,
            promotion_signals=prom_signals,
        )

        result: dict[str, Any] = {
            "seed": seed_result,
            "graphs": {
                "procurement": _summarize_procurement(proc_graph),
                "promotion": _summarize_promotion(prom_graph),
            },
            "signals": {
                "procurement_threshold": len(proc_signals.threshold_candidates),
                "procurement_velocity": len(proc_signals.velocity_candidates),
                "procurement_promotion": len(proc_signals.promotion_candidates),
                "promotion_bundles": len(prom_signals.bundle_candidates),
            },
        }

        if persist:
            proc_run, draft_ids, proc_warnings = await execute_procurement_run(
                session,
                user_id=admin.id,
                body=ProcurementRunCreateBody(),
            )
            prom_run, prom_warnings = await execute_promotion_run(
                session,
                user_id=admin.id,
                body=PromotionRunCreateBody(),
            )
            result["runners"] = {
                "procurement_run_id": proc_run.id,
                "draft_purchase_ids": draft_ids,
                "procurement_warnings": proc_warnings,
                "promotion_run_id": prom_run.id,
                "promotion_status": prom_run.status.value,
                "promotion_warnings": prom_warnings,
            }
        else:
            await session.rollback()

        return result


async def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate ERP LangGraph agents")
    parser.add_argument("--mock-llm", action="store_true", help="Patch fake LLM for both graphs")
    parser.add_argument("--db", action="store_true", help="Load signals from Postgres")
    parser.add_argument("--persist", action="store_true", help="With --db, commit runner results")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    if args.db:
        payload = await _run_with_db(use_mock_llm=args.mock_llm, persist=args.persist)
    else:
        proc_out, prom_out = await _run_graphs(
            use_mock_llm=args.mock_llm,
            procurement_signals=make_procurement_signals(),
            promotion_signals=make_promotion_signals(),
        )
        payload = {
            "mode": "fixtures",
            "procurement": _summarize_procurement(proc_out),
            "promotion": _summarize_promotion(prom_out),
        }

    if args.json:
        print(json.dumps(payload, indent=2, default=str))
        return

    print("=== Agent simulation ===")
    if args.db:
        print(f"DB mode (persist={args.persist}, mock_llm={args.mock_llm})")
        sig = payload.get("signals", {})
        print(
            f"Signals: threshold={sig.get('procurement_threshold')} "
            f"velocity={sig.get('procurement_velocity')} "
            f"promo_skus={sig.get('procurement_promotion')} "
            f"bundles={sig.get('promotion_bundles')}",
        )
        for key in ("procurement", "promotion"):
            g = payload.get("graphs", {}).get(key, {})
            print(f"\n[{key}] lines/projects={g.get('line_count') or g.get('project_count')}")
            print(f"  fallback_used={g.get('fallback_used')}")
            print(f"  notes: {g.get('merge_notes')}")
        if "runners" in payload:
            r = payload["runners"]
            print(f"\nRunners: procurement_run={r.get('procurement_run_id')} drafts={r.get('draft_purchase_ids')}")
            print(f"         promotion_run={r.get('promotion_run_id')} status={r.get('promotion_status')}")
    else:
        print(f"Fixture mode (mock_llm={args.mock_llm})")
        for key in ("procurement", "promotion"):
            block = payload.get(key, {})
            print(f"\n[{key}] count={block.get('line_count') or block.get('project_count')}")
            print(f"  fallback_used={block.get('fallback_used')}")
            print(f"  notes: {block.get('merge_notes')}")


if __name__ == "__main__":
    asyncio.run(main())
