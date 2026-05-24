from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_user_permissions
from app.models.user import User
from app.schemas.search import SearchEntityType, SearchResponse
from app.services.search_service import unified_search

router = APIRouter(prefix="/search")


@router.get("", response_model=SearchResponse)
async def global_search(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    permissions: Annotated[set[str], Depends(get_current_user_permissions)],
    q: str = Query(..., min_length=2, max_length=120),
    types: list[SearchEntityType] | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    sale_id: int | None = Query(None, ge=1),
) -> SearchResponse:
    """Return only records the current user may read (permission-scoped per entity type)."""
    type_set = set(types) if types else None
    results = await unified_search(
        db,
        query=q,
        permissions=permissions,
        types=type_set,
        limit=limit,
        sale_id=sale_id,
    )
    return SearchResponse(query=q.strip(), results=results)
