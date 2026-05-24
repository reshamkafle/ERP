"""Integration tests for RBAC user seed."""

from __future__ import annotations

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.bootstrap import seed_admin_user
from app.core.permissions_catalog import ALL_PERMISSION_CODES
from app.core.rbac_bootstrap import seed_permissions, seed_system_roles
from app.core.seed_rbac_users import seed_rbac_users
from app.core.seed_rbac_users_manifest import SEED_USERS
from app.models.user import User
from app.services.permission_service import get_user_permissions


async def _bootstrap_rbac_catalog(session: AsyncSession) -> None:
    await seed_admin_user(session)
    perms = await seed_permissions(session)
    await seed_system_roles(session, perms)


async def _clear_rbac_seed_users(session: AsyncSession) -> None:
    await session.execute(delete(User).where(User.email.like("rbac-%@seed.local")))
    await session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_seed_rbac_users_covers_all_permissions(db_session: AsyncSession) -> None:
    await _clear_rbac_seed_users(db_session)
    await _bootstrap_rbac_catalog(db_session)
    result = await seed_rbac_users(db_session)
    await db_session.commit()

    assert result.created_users == 50
    assert result.skipped_users == 0

    count_result = await db_session.execute(
        select(func.count())
        .select_from(User)
        .where(User.email.like("rbac-%@seed.local"))
    )
    assert count_result.scalar_one() == 50

    union: set[str] = set()
    for spec in SEED_USERS:
        user_result = await db_session.execute(
            select(User).where(User.email == spec.email)
        )
        user = user_result.scalar_one()
        union |= await get_user_permissions(db_session, user)

    assert union == ALL_PERMISSION_CODES


@pytest.mark.asyncio
@pytest.mark.integration
async def test_seed_rbac_users_idempotent(db_session: AsyncSession) -> None:
    await _clear_rbac_seed_users(db_session)
    await _bootstrap_rbac_catalog(db_session)
    first = await seed_rbac_users(db_session)
    await db_session.commit()
    second = await seed_rbac_users(db_session)
    await db_session.commit()

    assert first.created_users == 50
    assert second.created_users == 0
    assert second.skipped_users == 50
