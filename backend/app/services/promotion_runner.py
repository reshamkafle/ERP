"""Orchestrate promotion signal fetch, LangGraph, and PromotionRun persistence."""

from __future__ import annotations

import logging
from typing import Any

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.promotion_graph import run_promotion_graph
from app.models.enums import PromotionRunStatus
from app.models.product import Product
from app.models.promotion_run import PromotionRun
from app.schemas.promotion import PromotionConfirmBody, PromotionRunCreateBody
from app.services.promotion_signals import fetch_promotion_signals
from app.services.promotion_validation import validate_project_margins

logger = logging.getLogger(__name__)


def _collect_product_ids(projects: list) -> set[int]:
    ids: set[int] = set()
    for proj in projects:
        ids.add(int(proj.anchor.product_id))
        for rel in proj.related_items:
            ids.add(int(rel.product_id))
    return ids


async def execute_promotion_run(
    db: AsyncSession,
    *,
    user_id: int,
    body: PromotionRunCreateBody,
) -> tuple[PromotionRun, list[str]]:
    """Returns (run, warnings)."""
    run = PromotionRun(
        created_by_id=user_id,
        status=PromotionRunStatus.IN_PROGRESS,
        proposals_json=None,
        approved_json=None,
        error_message=None,
    )
    db.add(run)
    await db.flush()

    warnings: list[str] = []
    caught: BaseException | None = None
    try:
        async with db.begin_nested():
            signals = await fetch_promotion_signals(
                db,
                sales_lookback_days=body.sales_lookback_days,
                max_anchor_products=body.max_anchor_products,
                max_related_per_anchor=body.max_related_per_anchor,
                category_id=body.category_id,
                co_purchase_pair_limit=body.co_purchase_pair_limit,
            )
            warnings.extend(signals.warnings)

            graph_state = await run_promotion_graph(
                signals=signals,
                max_projects=body.max_projects,
            )
            merged = graph_state.get("merged_projects") or []
            proposals_json: dict[str, Any] = {
                "merge_notes": graph_state.get("merge_notes") or "",
                "fallback_used": bool(graph_state.get("fallback_used")),
                "signals_warnings": signals.warnings,
                "projects": merged,
            }
            run.proposals_json = proposals_json
            run.status = PromotionRunStatus.DRAFT_REVIEW
            run.error_message = None

    except BaseException as exc:
        caught = exc
        logger.exception("promotion run failed")
        run.status = PromotionRunStatus.FAILED
        run.error_message = str(exc)[:4000]
        run.proposals_json = None

    await db.commit()
    await db.refresh(run)

    if caught is not None:
        raise caught

    return run, warnings


async def confirm_promotion_run(
    db: AsyncSession,
    *,
    run_id: int,
    body: PromotionConfirmBody,
) -> PromotionRun:
    result = await db.execute(select(PromotionRun).where(PromotionRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        msg = "Promotion run not found"
        raise LookupError(msg)

    if run.status != PromotionRunStatus.DRAFT_REVIEW:
        msg = "Run is not awaiting review"
        raise ValueError(msg)

    if body.reject:
        run.status = PromotionRunStatus.REJECTED
        run.approved_json = {"projects": [], "rejected": True}
        await db.commit()
        await db.refresh(run)
        return run

    projects = body.projects
    if not projects:
        run.status = PromotionRunStatus.REJECTED
        run.approved_json = {"projects": [], "rejected": True}
        await db.commit()
        await db.refresh(run)
        return run

    ids = _collect_product_ids(projects)
    if not ids:
        msg = "No product ids in projects payload"
        raise ValueError(msg)

    result = await db.execute(
        select(Product.id, Product.price, Product.cost_price).where(Product.id.in_(ids)),
    )
    rows = result.all()
    found = {int(row[0]) for row in rows}
    missing = ids - found
    if missing:
        msg = f"Unknown product ids: {sorted(missing)[:20]}"
        raise ValueError(msg)

    product_prices = {
        int(row[0]): (Decimal(str(row[1] or 0)), Decimal(str(row[2] or 0))) for row in rows
    }
    project_dicts = [proj.model_dump() for proj in projects]
    for proj in project_dicts:
        validate_project_margins(proj, product_prices=product_prices)

    run.approved_json = {"projects": project_dicts}
    run.status = PromotionRunStatus.APPROVED
    await db.commit()
    await db.refresh(run)
    return run
