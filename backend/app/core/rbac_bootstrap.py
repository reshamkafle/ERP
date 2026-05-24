from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permissions_catalog import PERMISSION_CATALOG, SYSTEM_ROLES
from app.models.permission import Permission
from app.models.role import Department, Role, RolePermission, RoleType, UserRoleAssignment
from app.models.user import User, UserRole


async def seed_permissions(session: AsyncSession) -> dict[str, Permission]:
    result = await session.execute(select(Permission))
    existing = {p.code: p for p in result.scalars().all()}
    for defn in PERMISSION_CATALOG:
        if defn.code not in existing:
            perm = Permission(
                code=defn.code,
                name=defn.name,
                module=defn.module,
                description=defn.description or None,
            )
            session.add(perm)
            existing[defn.code] = perm
    await session.flush()
    return existing


async def seed_system_roles(session: AsyncSession, permissions: dict[str, Permission]) -> dict[str, Role]:
    roles_by_name: dict[str, Role] = {}
    result = await session.execute(
        select(Role).options(
            selectinload(Role.permission_links).selectinload(RolePermission.permission)
        )
    )
    for role in result.scalars().all():
        roles_by_name[role.name] = role

    for spec in SYSTEM_ROLES:
        role = roles_by_name.get(spec["name"])
        if role is None:
            dept = spec.get("department")
            role = Role(
                name=spec["name"],
                role_type=RoleType[spec["role_type"]],
                department=Department(dept) if dept else None,
                is_system=spec["is_system"],
            )
            session.add(role)
            await session.flush()
            roles_by_name[spec["name"]] = role

        desired_ids = {permissions[c].id for c in spec["permission_codes"] if c in permissions}
        link_result = await session.execute(
            select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
        )
        current_ids = set(link_result.scalars().all())
        for pid in desired_ids - current_ids:
            session.add(RolePermission(role_id=role.id, permission_id=pid))

    await session.flush()
    return roles_by_name


async def assign_legacy_user_roles(session: AsyncSession, roles_by_name: dict[str, Role]) -> None:
    """Map users with legacy enum to system roles if they have no assignments."""
    legacy_map = {
        UserRole.ADMIN: "Super Admin",
        UserRole.MANAGER: "Manager",
        UserRole.CASHIER: "Cashier",
    }
    result = await session.execute(select(User))
    users = result.scalars().all()
    for user in users:
        subq = await session.execute(
            select(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
        )
        if subq.scalars().first() is not None:
            continue
        role_name = legacy_map.get(user.role)
        if role_name and role_name in roles_by_name:
            session.add(
                UserRoleAssignment(user_id=user.id, role_id=roles_by_name[role_name].id)
            )
    await session.flush()
