import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent_errors import public_agent_error_message
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies.auth import require_permission
from app.models.promotion_run import PromotionRun
from app.models.user import User
from app.schemas.promotion import (
    PromotionConfirmBody,
    PromotionRunCreateBody,
    PromotionRunDetailResponse,
    PromotionRunResponse,
)
from app.services.promotion_runner import confirm_promotion_run, execute_promotion_run

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/promotion-runs")

PromotionRoles = require_permission("sales.promotions.manage")

_AGENT_FAILURE_DETAIL = "Promotion agent run failed. Check server logs."


@router.post("", response_model=PromotionRunResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_promotion_run(
    request: Request,
    body: PromotionRunCreateBody,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(PromotionRoles)],
) -> PromotionRunResponse:
    try:
        run, warnings = await execute_promotion_run(
            db,
            user_id=user.id,
            body=body,
        )
    except BaseException as exc:
        logger.exception("Promotion agent run failed")
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=_AGENT_FAILURE_DETAIL,
        ) from exc
    return PromotionRunResponse(
        id=run.id,
        status=run.status.value,
        warnings=warnings,
        error_message=None,
    )


@router.get("/{run_id}", response_model=PromotionRunDetailResponse)
async def get_promotion_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PromotionRoles)],
) -> PromotionRunDetailResponse:
    result = await db.execute(select(PromotionRun).where(PromotionRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Promotion run not found")
    return PromotionRunDetailResponse(
        id=run.id,
        status=run.status.value,
        created_at=run.created_at,
        proposals_json=run.proposals_json,
        approved_json=run.approved_json,
        error_message=public_agent_error_message(run.error_message),
    )


@router.post("/{run_id}/confirm", response_model=PromotionRunDetailResponse)
@limiter.limit("30/hour")
async def confirm_promotion_run_endpoint(
    request: Request,
    run_id: int,
    body: PromotionConfirmBody,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(PromotionRoles)],
) -> PromotionRunDetailResponse:
    try:
        run = await confirm_promotion_run(db, run_id=run_id, body=body)
    except LookupError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Promotion run not found") from None
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PromotionRunDetailResponse(
        id=run.id,
        status=run.status.value,
        created_at=run.created_at,
        proposals_json=run.proposals_json,
        approved_json=run.approved_json,
        error_message=public_agent_error_message(run.error_message),
    )
