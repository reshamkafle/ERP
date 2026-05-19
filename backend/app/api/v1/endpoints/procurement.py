from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.procurement_run import ProcurementRun
from app.models.user import User, UserRole
from app.schemas.procurement import (
    ProcurementRunCreateBody,
    ProcurementRunDetailResponse,
    ProcurementRunResponse,
)
from app.services.procurement_runner import execute_procurement_run

router = APIRouter(prefix="/procurement-runs")

ProcurementRoles = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.post("", response_model=ProcurementRunResponse, status_code=status.HTTP_201_CREATED)
async def create_procurement_run(
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
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=str(exc) or "Procurement agent run failed",
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
        error_message=run.error_message,
        draft_purchase_ids=list(draft_ids),
    )
