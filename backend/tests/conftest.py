"""Pytest fixtures for agent integration tests."""

from __future__ import annotations

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.bootstrap import seed_admin_user
from app.core.database import AsyncSessionLocal, engine
from app.models.user import User, UserRole
from app.testing.seed_agent_demo import ensure_procurement_run_enum_sync, seed_agent_demo_data

ensure_procurement_run_enum_sync()

_postgres_checked: bool | None = None
_postgres_available: bool = False


async def _check_postgres_once() -> bool:
    global _postgres_checked, _postgres_available
    if _postgres_checked is not None:
        return _postgres_available
    _postgres_checked = True
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        _postgres_available = True
    except Exception:
        _postgres_available = False
    finally:
        await engine.dispose()
    return _postgres_available


@pytest.fixture(autouse=True)
async def _dispose_engine_pool_after_test(request: pytest.FixtureRequest) -> None:
    """Avoid asyncpg 'attached to a different loop' across pytest-asyncio tests."""
    yield
    if "integration" in request.keywords:
        await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncSession:
    if not await _check_postgres_once():
        pytest.skip("PostgreSQL not available (start docker compose up -d postgres)")
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def seeded_db(db_session: AsyncSession) -> AsyncSession:
    await seed_admin_user(db_session)
    await seed_agent_demo_data(db_session)
    await db_session.commit()
    return db_session


@pytest.fixture
async def admin_user(seeded_db: AsyncSession) -> User:
    result = await seeded_db.execute(
        select(User).where(User.role == UserRole.ADMIN).limit(1),
    )
    user = result.scalar_one_or_none()
    if user is None:
        pytest.skip("Admin user not found after seed")
    return user
