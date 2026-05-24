from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.preferences import LayoutPreferences, UserPreferencesRead, UserPreferencesUpdate
from app.services.permission_service import get_user_permissions

router = APIRouter(prefix="/users/me")

ALLOWED_NAV_SLUGS = frozenset(
    {
        "dashboard",
        "reports",
        "inventory",
        "bom",
        "documents",
        "customers",
        "sales",
        "pos",
        "suppliers",
        "purchases",
        "promotions",
    }
)

REPORT_NAV_PERMISSIONS = frozenset(
    {
        "reports.reports.read",
        "reports.merchandiser.read",
        "reports.finance.read",
        "reports.marketing.read",
        "reports.warehouse.read",
        "reports.it.read",
        "reports.manager.read",
    }
)

NAV_SLUG_PERMISSIONS: dict[str, str] = {
    "dashboard": "reports.dashboard.read",
    "reports": "reports.reports.read",
    "inventory": "warehouse.inventory.read",
    "bom": "warehouse.bom.read",
    "documents": "warehouse.documents.read",
    "customers": "sales.customers.read",
    "sales": "sales.orders.read",
    "pos": "sales.pos.use",
    "suppliers": "warehouse.suppliers.read",
    "purchases": "warehouse.purchases.read",
    "promotions": "sales.promotions.manage",
}


def _default_layout() -> LayoutPreferences:
    return LayoutPreferences()


def _layout_from_json(data: dict) -> LayoutPreferences:
    return LayoutPreferences(
        theme=data.get("theme", "light"),
        sidebar_collapsed=data.get("sidebar_collapsed", False),
        hidden_nav_slugs=data.get("hidden_nav_slugs", []),
    )


async def _validate_hidden_nav(
    db: AsyncSession, user: User, slugs: list[str]
) -> list[str]:
    perms = await get_user_permissions(db, user)
    validated: list[str] = []
    for slug in slugs:
        if slug not in ALLOWED_NAV_SLUGS:
            continue
        required = NAV_SLUG_PERMISSIONS.get(slug)
        if slug == "reports":
            if not REPORT_NAV_PERMISSIONS.intersection(perms):
                continue
        elif required and required not in perms:
            continue
        validated.append(slug)
    return validated


@router.get("/preferences", response_model=UserPreferencesRead)
async def get_preferences(
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> UserPreferencesRead:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current.id)
    )
    pref = result.scalar_one_or_none()
    if pref is None or not pref.layout_json:
        return UserPreferencesRead(layout=_default_layout())
    return UserPreferencesRead(layout=_layout_from_json(pref.layout_json))


@router.patch("/preferences", response_model=UserPreferencesRead)
async def update_preferences(
    body: UserPreferencesUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("profile.layout.configure"))],
) -> UserPreferencesRead:
    hidden = await _validate_hidden_nav(db, current, body.layout.hidden_nav_slugs)
    layout_data = {
        "theme": body.layout.theme,
        "sidebar_collapsed": body.layout.sidebar_collapsed,
        "hidden_nav_slugs": hidden,
    }
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current.id)
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        pref = UserPreference(user_id=current.id, layout_json=layout_data)
        db.add(pref)
    else:
        pref.layout_json = layout_data
    await db.commit()
    return UserPreferencesRead(layout=_layout_from_json(layout_data))
