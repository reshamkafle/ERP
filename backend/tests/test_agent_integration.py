"""Integration tests for agent signal fetch and runners (requires PostgreSQL)."""

from __future__ import annotations

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PromotionRunStatus, ProcurementRunStatus
from app.models.procurement_run import ProcurementRun
from app.models.promotion_run import PromotionRun
from app.models.purchase import Purchase, PurchaseItem
from app.models.user import User
from app.schemas.procurement import ProcurementRunCreateBody
from app.schemas.promotion import PromotionConfirmBody, PromotionRunCreateBody
from app.services.procurement_runner import execute_procurement_run
from app.services.procurement_signals import fetch_procurement_signals
from app.services.promotion_runner import confirm_promotion_run, execute_promotion_run
from app.services.promotion_signals import fetch_promotion_signals
from app.testing.seed_agent_demo import DEMO_SKU_LOW


@pytest.mark.integration
@pytest.mark.asyncio
async def test_procurement_signals_from_seed(seeded_db: AsyncSession) -> None:
    signals = await fetch_procurement_signals(seeded_db, sales_lookback_days=14, velocity_limit=30)
    assert signals.threshold_candidates or signals.velocity_candidates or signals.promotion_candidates
    skus = {c.sku for c in signals.threshold_candidates}
    assert DEMO_SKU_LOW in skus or len(signals.velocity_candidates) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_promotion_signals_from_seed(seeded_db: AsyncSession) -> None:
    signals = await fetch_promotion_signals(
        seeded_db,
        sales_lookback_days=30,
        max_anchor_products=15,
        max_related_per_anchor=5,
    )
    assert len(signals.bundle_candidates) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_procurement_runner_creates_draft(
    seeded_db: AsyncSession,
    admin_user: User,
) -> None:
    run, draft_ids, _warnings = await execute_procurement_run(
        seeded_db,
        user_id=admin_user.id,
        body=ProcurementRunCreateBody(),
    )
    try:
        assert run.status == ProcurementRunStatus.COMPLETED
        assert len(draft_ids) >= 1
    finally:
        if draft_ids:
            await seeded_db.execute(
                delete(PurchaseItem).where(
                    PurchaseItem.purchase_id.in_(
                        select(Purchase.id).where(Purchase.procurement_run_id == run.id),
                    ),
                ),
            )
            await seeded_db.execute(delete(Purchase).where(Purchase.procurement_run_id == run.id))
        await seeded_db.execute(delete(ProcurementRun).where(ProcurementRun.id == run.id))
        await seeded_db.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_promotion_runner_draft_review(
    seeded_db: AsyncSession,
    admin_user: User,
) -> None:
    run, _warnings = await execute_promotion_run(
        seeded_db,
        user_id=admin_user.id,
        body=PromotionRunCreateBody(),
    )
    try:
        assert run.status == PromotionRunStatus.DRAFT_REVIEW
        proposals = (run.proposals_json or {}).get("projects") or []
        assert len(proposals) >= 1
    finally:
        await seeded_db.execute(delete(PromotionRun).where(PromotionRun.id == run.id))
        await seeded_db.commit()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_promotion_runner_confirm_approves(
    seeded_db: AsyncSession,
    admin_user: User,
) -> None:
    run, _warnings = await execute_promotion_run(
        seeded_db,
        user_id=admin_user.id,
        body=PromotionRunCreateBody(),
    )
    projects = (run.proposals_json or {}).get("projects") or []
    assert run.status == PromotionRunStatus.DRAFT_REVIEW
    assert projects
    try:
        approved = await confirm_promotion_run(
            seeded_db,
            run_id=run.id,
            body=PromotionConfirmBody(projects=projects),
        )
        assert approved.status == PromotionRunStatus.APPROVED
        assert len((approved.approved_json or {}).get("projects") or []) == len(projects)
    finally:
        await seeded_db.execute(delete(PromotionRun).where(PromotionRun.id == run.id))
        await seeded_db.commit()
