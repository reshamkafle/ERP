from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import require_roles
from app.models.product import Product
from app.models.user import User, UserRole

router = APIRouter(prefix="/dashboard")


@router.get("/summary")
async def dashboard_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))],
) -> dict[str, str | int]:
    low_stock_count = (
        await db.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.stock < Product.low_stock_threshold),
        )
    ).scalar_one()
    return {
        "heading": "Today at a glance",
        "low_stock_count": low_stock_count,
        "open_pos_sessions": 0,
    }
