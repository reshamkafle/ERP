"""Authorization tests for purchase endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.main import app
from app.models.permission import Permission
from app.models.role import Role, RolePermission, RoleType, UserRoleAssignment
from app.models.user import User, UserRole


async def _user_with_permissions(
    db: AsyncSession,
    *,
    email: str,
    permission_codes: list[str],
) -> User:
    user = User(
        email=email,
        hashed_password="unused",
        role=UserRole.MANAGER,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    role = Role(name=f"Test {email}", role_type=RoleType.EMPLOYEE, is_system=False)
    db.add(role)
    await db.flush()

    for code in permission_codes:
        perm = (
            await db.execute(select(Permission).where(Permission.code == code))
        ).scalar_one_or_none()
        if perm is None:
            perm = Permission(code=code, name=code, module="test")
            db.add(perm)
            await db.flush()
        db.add(RolePermission(role_id=role.id, permission_id=perm.id))

    db.add(UserRoleAssignment(user_id=user.id, role_id=role.id))
    await db.flush()
    return user


@pytest.mark.asyncio
@pytest.mark.integration
async def test_purchase_read_only_cannot_create(seeded_db: AsyncSession) -> None:
    reader = await _user_with_permissions(
        seeded_db,
        email="purchase-reader@test.local",
        permission_codes=["warehouse.purchases.read"],
    )
    await seeded_db.commit()

    token = create_access_token(str(reader.id), role=reader.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/purchases",
            json={"supplier_id": 1, "items": [{"product_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 403
