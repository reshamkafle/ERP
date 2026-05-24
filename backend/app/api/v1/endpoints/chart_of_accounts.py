from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import chart_of_account as coa_crud
from app.dependencies.auth import require_permission
from app.models.user import User
from app.schemas.accounting import ChartOfAccountListResponse, ChartOfAccountRead

router = APIRouter(prefix="/chart-of-accounts")

GlRead = require_permission("finance.gl.read", "finance.records.read")


@router.get("", response_model=ChartOfAccountListResponse)
async def list_chart_of_accounts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(GlRead)],
) -> ChartOfAccountListResponse:
    items = await coa_crud.list_chart_of_accounts(db)
    return ChartOfAccountListResponse(
        items=[ChartOfAccountRead.model_validate(i) for i in items],
    )
