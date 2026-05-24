import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent_errors import public_agent_error_message
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies.auth import require_permission
from app.models.procurement_run import ProcurementRun
from app.models.user import User
from app.schemas.procurement import (
    ProcurementRunCreateBody,
    ProcurementRunDetailResponse,
    ProcurementRunResponse,
)
from app.services.procurement_runner import execute_procurement_run

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/procurement-runs")

ProcurementRoles = require_permission("warehouse.procurement.manage")

_AGENT_FAILURE_DETAIL = "Procurement agent run failed. Check server logs."


@router.post("", response_model=ProcurementRunResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_procurement_run(
    request: Request,
    body: ProcurementRunCreateBody,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(ProcurementRoles)],
) -> ProcurementRunResponse:
    try:
        run, draft_ids, warnings = await execute_procurement_run(
            db,
            user_id=user.id,
            body=body,
        )
    except BaseException as exc:
        logger.exception("Procurement agent run failed")
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=_AGENT_FAILURE_DETAIL,
        ) from exc
    return ProcurementRunResponse(
        id=run.id,
        status=run.status.value,
        draft_purchase_ids=draft_ids,
        warnings=warnings,
        error_message=None,
    )


@router.get("/{run_id}", response_model=ProcurementRunDetailResponse)
async def get_procurement_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(ProcurementRoles)],
) -> ProcurementRunDetailResponse:
    result = await db.execute(select(ProcurementRun).where(ProcurementRun.id == run_id))
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Procurement run not found")
    draft_ids = (run.summary_json or {}).get("draft_purchase_ids") or []
    return ProcurementRunDetailResponse(
        id=run.id,
        status=run.status.value,
        created_at=run.created_at,
        summary_json=run.summary_json,
        error_message=public_agent_error_message(run.error_message),
        draft_purchase_ids=list(draft_ids),
    )
