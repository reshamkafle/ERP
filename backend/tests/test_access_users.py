"""Authorization tests for user listing and role assignment."""

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
async def test_list_users_requires_read_or_manage(seeded_db: AsyncSession) -> None:
    denied = await _user_with_permissions(
        seeded_db,
        email="no-users-perm@test.local",
        permission_codes=["sales.customers.read"],
    )
    reader = await _user_with_permissions(
        seeded_db,
        email="users-reader@test.local",
        permission_codes=["system.users.read"],
    )
    await seeded_db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        denied_res = await client.get(
            "/api/v1/access/users",
            headers={"Authorization": f"Bearer {create_access_token(str(denied.id), role=denied.role.value)}"},
        )
        reader_res = await client.get(
            "/api/v1/access/users",
            headers={"Authorization": f"Bearer {create_access_token(str(reader.id), role=reader.role.value)}"},
        )

    assert denied_res.status_code == 403
    assert reader_res.status_code == 200
    assert any(u["email"] == reader.email for u in reader_res.json())


@pytest.mark.asyncio
@pytest.mark.integration
async def test_roles_manage_cannot_list_users_without_users_permission(
    seeded_db: AsyncSession,
) -> None:
    roles_only = await _user_with_permissions(
        seeded_db,
        email="roles-only@test.local",
        permission_codes=["system.roles.manage"],
    )
    await seeded_db.commit()

    token = create_access_token(str(roles_only.id), role=roles_only.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        users_res = await client.get(
            "/api/v1/access/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        roles_res = await client.get(
            "/api/v1/access/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert users_res.status_code == 403
    assert roles_res.status_code == 200


@pytest.mark.asyncio
@pytest.mark.integration
async def test_users_manage_can_list_roles_for_assignment(seeded_db: AsyncSession) -> None:
    manager = await _user_with_permissions(
        seeded_db,
        email="users-manager@test.local",
        permission_codes=["system.users.manage"],
    )
    await seeded_db.commit()

    token = create_access_token(str(manager.id), role=manager.role.value)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/access/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
