from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permissions_catalog import ALL_PERMISSION_CODES, LEGACY_ROLE_PERMISSIONS
from app.models.permission import Permission
from app.models.role import Role, RolePermission, RoleType, UserPermissionOverride, UserRoleAssignment
from app.models.user import User, UserRole


def role_codes_from_assignments(assignments: list[UserRoleAssignment]) -> set[str]:
    if not assignments:
        return set()
    codes: set[str] = set()
    for assignment in assignments:
        role = assignment.role
        if role.role_type == RoleType.SUPER_ADMIN:
            return set(ALL_PERMISSION_CODES)
        for link in role.permission_links:
            codes.add(link.permission.code)
    return codes


def apply_permission_overrides(base: set[str], overrides: dict[str, bool]) -> set[str]:
    effective = set(base)
    for code, granted in overrides.items():
        if granted:
            effective.add(code)
        else:
            effective.discard(code)
    return effective


async def get_role_based_permissions(session: AsyncSession, user: User) -> set[str]:
    """Permissions from assigned roles, or legacy fallback when none assigned."""
    result = await session.execute(
        select(UserRoleAssignment)
        .where(UserRoleAssignment.user_id == user.id)
        .options(
            selectinload(UserRoleAssignment.role).selectinload(Role.permission_links).selectinload(
                RolePermission.permission
            )
        )
    )
    assignments = result.scalars().all()
    if not assignments:
        return set(LEGACY_ROLE_PERMISSIONS.get(user.role, frozenset()))
    return role_codes_from_assignments(assignments)


async def get_user_permission_overrides(session: AsyncSession, user_id: int) -> dict[str, bool]:
    result = await session.execute(
        select(UserPermissionOverride)
        .where(UserPermissionOverride.user_id == user_id)
        .options(selectinload(UserPermissionOverride.permission))
    )
    return {row.permission.code: row.granted for row in result.scalars().all()}


async def get_user_permissions(session: AsyncSession, user: User) -> set[str]:
    """Effective permissions: roles (or legacy) plus per-user overrides."""
    role_codes = await get_role_based_permissions(session, user)
    overrides = await get_user_permission_overrides(session, user.id)
    return apply_permission_overrides(role_codes, overrides)


async def user_has_permission(session: AsyncSession, user: User, code: str) -> bool:
    return code in await get_user_permissions(session, user)


async def get_permission_ids_by_codes(
    session: AsyncSession, codes: set[str],
) -> dict[str, int]:
    if not codes:
        return {}
    result = await session.execute(select(Permission).where(Permission.code.in_(codes)))
    return {p.code: p.id for p in result.scalars().all()}


def assert_can_delegate(grantor_codes: set[str], requested_codes: set[str]) -> None:
    """Raise ValueError if grantor cannot assign requested permissions."""
    if not requested_codes.issubset(grantor_codes):
        missing = requested_codes - grantor_codes
        raise ValueError(
            f"Cannot grant permissions you do not hold: {', '.join(sorted(missing))}"
        )


async def role_permission_codes(session: AsyncSession, role_id: int) -> set[str]:
    result = await session.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(
            selectinload(Role.permission_links).selectinload(RolePermission.permission)
        )
    )
    role = result.scalar_one_or_none()
    if role is None:
        return set()
    if role.role_type == RoleType.SUPER_ADMIN:
        return set(ALL_PERMISSION_CODES)
    return {link.permission.code for link in role.permission_links}


async def set_user_effective_permissions(
    session: AsyncSession,
    user: User,
    desired_codes: set[str],
) -> set[str]:
    """Persist overrides so the user's effective permissions match desired_codes."""
    role_codes = await get_role_based_permissions(session, user)
    current_overrides = await get_user_permission_overrides(session, user.id)

    result = await session.execute(
        select(UserPermissionOverride)
        .where(UserPermissionOverride.user_id == user.id)
        .options(selectinload(UserPermissionOverride.permission))
    )
    override_rows = {row.permission.code: row for row in result.scalars().all()}

    relevant = role_codes | desired_codes | set(current_overrides.keys())
    perm_ids = await get_permission_ids_by_codes(session, relevant)

    for code in relevant:
        has_role = code in role_codes
        wants = code in desired_codes
        perm_id = perm_ids.get(code)
        if perm_id is None:
            continue

        if has_role and wants:
            row = override_rows.pop(code, None)
            if row is not None:
                await session.delete(row)
        elif has_role and not wants:
            row = override_rows.pop(code, None)
            if row is None:
                session.add(UserPermissionOverride(user_id=user.id, permission_id=perm_id, granted=False))
            else:
                row.granted = False
        elif not has_role and wants:
            row = override_rows.pop(code, None)
            if row is None:
                session.add(UserPermissionOverride(user_id=user.id, permission_id=perm_id, granted=True))
            else:
                row.granted = True
        else:
            row = override_rows.pop(code, None)
            if row is not None:
                await session.delete(row)

    await session.flush()
    return apply_permission_overrides(role_codes, await get_user_permission_overrides(session, user.id))
