"""Idempotent seed of 50 RBAC test users with full permission coverage."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.permissions_catalog import ALL_PERMISSION_CODES
from app.core.rbac_bootstrap import seed_permissions, seed_system_roles
from app.core.security import get_password_hash
from app.core.seed_rbac_users_manifest import (
    CUSTOM_ROLE_BY_NAME,
    CUSTOM_ROLES,
    SEED_USERS,
    CustomRoleSpec,
    SeedUserSpec,
)
from app.models.permission import Permission
from app.models.role import Role, RolePermission, RoleType, UserRoleAssignment
from app.models.user import User
from app.services.permission_service import get_user_permissions

SEED_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "seed-output"
CREDENTIALS_FILE = SEED_OUTPUT_DIR / "rbac-users.md"


@dataclass
class SeedRbacResult:
    created_users: int
    skipped_users: int
    created_roles: int
    credentials_path: Path | None


async def _upsert_custom_role(
    session: AsyncSession,
    spec: CustomRoleSpec,
    permissions: dict[str, Permission],
    roles_by_name: dict[str, Role],
) -> tuple[Role, bool]:
    role = roles_by_name.get(spec.name)
    created = False
    if role is None:
        role = Role(
            name=spec.name,
            role_type=spec.role_type,
            department=spec.department,
            is_system=False,
            description=spec.description or None,
        )
        session.add(role)
        await session.flush()
        roles_by_name[spec.name] = role
        created = True

    desired_ids = {
        permissions[c].id for c in spec.permission_codes if c in permissions
    }
    link_result = await session.execute(
        select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
    )
    current_ids = set(link_result.scalars().all())
    for pid in desired_ids - current_ids:
        session.add(RolePermission(role_id=role.id, permission_id=pid))
    await session.flush()
    return role, created


async def _ensure_custom_roles(
    session: AsyncSession,
    permissions: dict[str, Permission],
    roles_by_name: dict[str, Role],
) -> int:
    created = 0
    for spec in CUSTOM_ROLES:
        _, was_created = await _upsert_custom_role(session, spec, permissions, roles_by_name)
        if was_created:
            created += 1
    return created


async def _assign_role_if_missing(
    session: AsyncSession,
    user_id: int,
    role_id: int,
) -> None:
    existing = await session.execute(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role_id,
        )
    )
    if existing.scalar_one_or_none() is None:
        session.add(UserRoleAssignment(user_id=user_id, role_id=role_id))


async def seed_rbac_users(session: AsyncSession) -> SeedRbacResult:
    """Create 50 seed users and custom roles; idempotent by email / role name."""
    settings = get_settings()
    password_hash = get_password_hash(settings.seed_user_password)

    permissions = await seed_permissions(session)
    roles_by_name = await seed_system_roles(session, permissions)
    created_roles = await _ensure_custom_roles(session, permissions, roles_by_name)

    created_users = 0
    skipped_users = 0
    seeded_users: list[tuple[SeedUserSpec, User]] = []

    for spec in SEED_USERS:
        result = await session.execute(select(User).where(User.email == spec.email))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                email=spec.email,
                hashed_password=password_hash,
                role=spec.legacy_role,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            created_users += 1
        else:
            skipped_users += 1

        role = roles_by_name.get(spec.role_name)
        if role is None:
            custom = CUSTOM_ROLE_BY_NAME.get(spec.role_name)
            if custom is None:
                raise ValueError(f"Unknown role for seed user {spec.email}: {spec.role_name}")
            role, _ = await _upsert_custom_role(
                session, custom, permissions, roles_by_name
            )
        await _assign_role_if_missing(session, user.id, role.id)
        seeded_users.append((spec, user))

    await session.flush()

    # Coverage: union of effective permissions across all 50 seed users.
    union: set[str] = set()
    for _, user in seeded_users:
        union |= await get_user_permissions(session, user)

    missing = ALL_PERMISSION_CODES - union
    if missing:
        raise RuntimeError(
            "Seed RBAC users do not cover all permissions. Missing: "
            + ", ".join(sorted(missing))
        )

    roles_with_perms = await load_roles_with_permissions(session)
    credentials_path = _write_credentials_file(
        seeded_users,
        roles_with_perms,
        settings.seed_user_password,
    )

    return SeedRbacResult(
        created_users=created_users,
        skipped_users=skipped_users,
        created_roles=created_roles,
        credentials_path=credentials_path,
    )


def _permission_codes_for_role(role_name: str, role: Role) -> list[str]:
    custom = CUSTOM_ROLE_BY_NAME.get(role_name)
    if custom is not None:
        return list(custom.permission_codes)
    if role.role_type == RoleType.SUPER_ADMIN:
        return sorted(ALL_PERMISSION_CODES)
    return sorted(
        link.permission.code
        for link in role.permission_links
        if link.permission is not None
    )


def _write_credentials_file(
    seeded_users: list[tuple[SeedUserSpec, User]],
    roles_by_name: dict[str, Role],
    password: str,
) -> Path:
    SEED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# RBAC seed users (dev only)",
        "",
        f"Shared password: `{password}`",
        "",
        "| # | Email | Role | Key permissions |",
        "|---|-------|------|-----------------|",
    ]
    for spec, _user in seeded_users:
        role = roles_by_name[spec.role_name]
        codes = _permission_codes_for_role(spec.role_name, role)
        if len(codes) > 8:
            perm_summary = ", ".join(codes[:6]) + f", … (+{len(codes) - 6} more)"
        else:
            perm_summary = ", ".join(codes) if codes else "—"
        lines.append(
            f"| {spec.index:02d} | `{spec.email}` | {spec.role_name} | {perm_summary} |"
        )
    lines.extend(
        [
            "",
            "Re-run: `cd backend && python scripts/seed_rbac_users.py`",
            "",
        ]
    )
    CREDENTIALS_FILE.write_text("\n".join(lines), encoding="utf-8")
    return CREDENTIALS_FILE


async def load_roles_with_permissions(session: AsyncSession) -> dict[str, Role]:
    result = await session.execute(
        select(Role).options(
            selectinload(Role.permission_links).selectinload(RolePermission.permission)
        )
    )
    return {role.name: role for role in result.scalars().all()}
