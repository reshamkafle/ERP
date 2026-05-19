"""Orchestrate procurement signal fetch, LangGraph, and draft purchase persistence."""

from __future__ import annotations

import logging
from collections import defaultdict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.procurement_graph import run_procurement_graph
from app.crud import purchase as purchase_crud
from app.models.enums import ProcurementRunStatus, PurchaseStatus
from app.models.procurement_run import ProcurementRun
from app.schemas.procurement import ProcurementRunCreateBody
from app.schemas.purchase import PurchaseCreate, PurchaseItemLineCreate
from app.services.procurement_signals import fetch_procurement_signals

logger = logging.getLogger(__name__)


async def execute_procurement_run(
    db: AsyncSession,
    *,
    user_id: int,
    body: ProcurementRunCreateBody,
) -> tuple[ProcurementRun, list[int], list[str]]:
    """Returns (run, draft_purchase_ids, warnings)."""
    run = ProcurementRun(
        created_by_id=user_id,
        status=ProcurementRunStatus.IN_PROGRESS,
        summary_json=None,
        error_message=None,
    )
    db.add(run)
    await db.flush()

    warnings: list[str] = []
    caught: BaseException | None = None
    try:
        async with db.begin_nested():
            signals = await fetch_procurement_signals(
                db,
                sales_lookback_days=body.sales_lookback_days,
                velocity_limit=body.velocity_limit,
            )
            warnings.extend(signals.warnings)

            graph_state = await run_procurement_graph(
                signals=signals,
                sales_lookback_days=body.sales_lookback_days,
                max_lines_per_supplier=body.max_lines_per_supplier,
            )
            merged = graph_state.get("merged_lines") or []
            merge_notes = graph_state.get("merge_notes") or ""
            fallback_used = bool(graph_state.get("fallback_used"))

            draft_ids: list[int] = []
            if merged:
                buckets: dict[int, list[dict]] = defaultdict(list)
                for line in merged:
                    sid = int(line["default_supplier_id"])
                    buckets[sid].append(line)

                cap = body.max_lines_per_supplier
                for supplier_id, rows in buckets.items():
                    trimmed = rows[:cap]
                    items: list[PurchaseItemLineCreate] = []
                    for row in trimmed:
                        items.append(
                            PurchaseItemLineCreate(
                                product_id=int(row["product_id"]),
                                quantity=int(row["suggested_qty"]),
                                unit_cost=Decimal(str(row["unit_cost"])),
                            ),
                        )
                    if not items:
                        continue
                    meta = {
                        "merge_notes": merge_notes,
                        "fallback_used": fallback_used,
                        "lines": [
                            {
                                "product_id": int(r["product_id"]),
                                "rationale": r.get("rationale", ""),
                            }
                            for r in trimmed
                        ],
                    }
                    purchase = await purchase_crud.create_purchase(
                        db,
                        PurchaseCreate(supplier_id=supplier_id, items=items),
                        created_by_id=user_id,
                        purchase_status=PurchaseStatus.DRAFT,
                        procurement_run_id=run.id,
                        agent_metadata=meta,
                        commit=False,
                    )
                    draft_ids.append(purchase.id)

            run.status = ProcurementRunStatus.COMPLETED
            run.summary_json = {
                "draft_purchase_ids": draft_ids,
                "merge_notes": merge_notes,
                "fallback_used": fallback_used,
                "message": None if draft_ids else "No lines to order after agent merge.",
            }
            run.error_message = None

    except BaseException as exc:
        caught = exc
        logger.exception("procurement run failed")
        run.status = ProcurementRunStatus.FAILED
        run.error_message = str(exc)[:4000]
        run.summary_json = {"draft_purchase_ids": []}

    await db.commit()
    await db.refresh(run)

    if caught is not None:
        raise caught

    draft_ids = (run.summary_json or {}).get("draft_purchase_ids") or []
    return run, list(draft_ids), warnings
