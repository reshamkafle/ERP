from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_permission
from app.models.permission import Permission
from app.models.role import Role, RolePermission, UserPermissionOverride, UserRoleAssignment
from app.models.user import User
from app.schemas.access_control import (
    PermissionRead,
    RoleCreate,
    RolePermissionsUpdate,
    RoleRead,
    RoleUpdate,
    UserAccessRead,
    UserPermissionsUpdate,
    UserRoleAssign,
    UserRoleRead,
)
from app.models.role import RoleType
from app.services.permission_delegation import (
    assert_not_self_user_target,
    assert_role_not_assigned_to_grantor,
    validate_permission_grant,
    validate_role_assignment,
    validate_user_permission_update,
)
from app.core.permissions_catalog import LEGACY_ROLE_PERMISSIONS
from app.services.permission_service import (
    apply_permission_overrides,
    role_codes_from_assignments,
    set_user_effective_permissions,
)
from app.services.role_security import assert_role_mutable, assert_role_type_assignable

router = APIRouter(prefix="/access")


def _role_to_read(role: Role) -> RoleRead:
    codes = [link.permission.code for link in role.permission_links]
    return RoleRead(
        id=role.id,
        name=role.name,
        role_type=role.role_type,
        department=role.department,
        is_system=role.is_system,
        description=role.description,
        permission_codes=codes,
    )


def _assignment_to_read(assignment: UserRoleAssignment) -> UserRoleRead:
    role = assignment.role
    return UserRoleRead(
        role_id=role.id,
        role_name=role.name,
        role_type=role.role_type,
        department=role.department,
    )


@router.get("/permissions", response_model=list[PermissionRead])
async def list_permissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("system.roles.manage", "system.users.manage"))],
) -> list[PermissionRead]:
    result = await db.execute(select(Permission).order_by(Permission.module, Permission.code))
    return [PermissionRead.model_validate(p) for p in result.scalars().all()]


@router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("system.roles.manage", "system.users.manage"))],
) -> list[RoleRead]:
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permission_links).selectinload(RolePermission.permission))
        .order_by(Role.name)
    )
    return [_role_to_read(r) for r in result.scalars().all()]


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("system.roles.manage"))],
) -> RoleRead:
    existing = await db.execute(select(Role).where(Role.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    assert_role_type_assignable(body.role_type)
    role = Role(
        name=body.name,
        role_type=body.role_type,
        department=body.department,
        description=body.description,
        is_system=False,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return RoleRead(
        id=role.id,
        name=role.name,
        role_type=role.role_type,
        department=role.department,
        is_system=role.is_system,
        description=role.description,
        permission_codes=[],
    )


@router.patch("/roles/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int,
    body: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("system.roles.manage"))],
) -> RoleRead:
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permission_links).selectinload(RolePermission.permission))
    )
    role = result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")
    assert_role_mutable(role)
    await assert_role_not_assigned_to_grantor(db, current, role_id)
    if body.role_type is not None:
        assert_role_type_assignable(body.role_type)
    if body.name is not None:
        role.name = body.name
    if body.role_type is not None:
        role.role_type = body.role_type
    if body.department is not None:
        role.department = body.department
    if body.description is not None:
        role.description = body.description
    await db.commit()
    await db.refresh(role)
    return _role_to_read(role)


@router.put("/roles/{role_id}/permissions", response_model=RoleRead)
async def set_role_permissions(
    role_id: int,
    body: RolePermissionsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("system.roles.manage"))],
) -> RoleRead:
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permission_links).selectinload(RolePermission.permission))
    )
    role = result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")
    assert_role_mutable(role)

    if role.is_system and role.role_type == RoleType.SUPER_ADMIN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot modify Super Admin permissions")

    await assert_role_not_assigned_to_grantor(db, current, role_id)

    requested = set(body.permission_codes)
    await validate_permission_grant(db, current, requested)

    perm_result = await db.execute(select(Permission).where(Permission.code.in_(requested)))
    perms = {p.code: p for p in perm_result.scalars().all()}
    unknown = requested - set(perms.keys())
    if unknown:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown permissions: {', '.join(sorted(unknown))}",
        )

    role.permission_links.clear()
    await db.flush()
    for code in requested:
        db.add(RolePermission(role_id=role.id, permission_id=perms[code].id))

    await db.commit()
    result = await db.execute(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permission_links).selectinload(RolePermission.permission))
    )
    return _role_to_read(result.scalar_one())


@router.get("/me/roles", response_model=list[UserRoleRead])
async def list_my_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
) -> list[UserRoleRead]:
    """Roles assigned to the current user (for self-grant prevention in Access Control UI)."""
    result = await db.execute(
        select(UserRoleAssignment)
        .where(UserRoleAssignment.user_id == current.id)
        .options(selectinload(UserRoleAssignment.role))
    )
    return [_assignment_to_read(a) for a in result.scalars().all()]


@router.get("/users", response_model=list[UserAccessRead])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("system.users.read", "system.users.manage"))],
) -> list[UserAccessRead]:
    users_result = await db.execute(select(User).order_by(User.email))
    users = users_result.scalars().all()

    assignments_result = await db.execute(
        select(UserRoleAssignment).options(
            selectinload(UserRoleAssignment.role)
            .selectinload(Role.permission_links)
            .selectinload(RolePermission.permission)
        )
    )
    assignments_by_user: dict[int, list[UserRoleAssignment]] = {}
    for assignment in assignments_result.scalars().all():
        assignments_by_user.setdefault(assignment.user_id, []).append(assignment)

    overrides_result = await db.execute(
        select(UserPermissionOverride).options(selectinload(UserPermissionOverride.permission))
    )
    overrides_by_user: dict[int, dict[str, bool]] = {}
    for override in overrides_result.scalars().all():
        overrides_by_user.setdefault(override.user_id, {})[override.permission.code] = (
            override.granted
        )

    return [
        UserAccessRead(
            id=user.id,
            email=user.email,
            legacy_role=user.role,
            is_active=user.is_active,
            roles=[_assignment_to_read(a) for a in assignments_by_user.get(user.id, [])],
            permission_codes=sorted(
                apply_permission_overrides(
                    role_codes_from_assignments(assignments_by_user.get(user.id, []))
                    or LEGACY_ROLE_PERMISSIONS.get(user.role, frozenset()),
                    overrides_by_user.get(user.id, {}),
                )
            ),
        )
        for user in users
    ]


@router.get("/users/{user_id}/roles", response_model=list[UserRoleRead])
async def list_user_roles(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("system.users.manage"))],
) -> list[UserRoleRead]:
    result = await db.execute(
        select(UserRoleAssignment)
        .where(UserRoleAssignment.user_id == user_id)
        .options(selectinload(UserRoleAssignment.role))
    )
    return [_assignment_to_read(a) for a in result.scalars().all()]


@router.put("/users/{user_id}/permissions", response_model=UserAccessRead)
async def set_user_permissions(
    user_id: int,
    body: UserPermissionsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("system.users.manage"))],
) -> UserAccessRead:
    user_result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.role_assignments).selectinload(UserRoleAssignment.role),
        )
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    desired = set(body.permission_codes)
    await validate_user_permission_update(db, current, user, desired)

    unknown = desired - {
        p.code
        for p in (
            await db.execute(select(Permission).where(Permission.code.in_(desired)))
        ).scalars().all()
    }
    if unknown:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown permissions: {', '.join(sorted(unknown))}",
        )

    effective = await set_user_effective_permissions(db, user, desired)
    await db.commit()

    assignments = (
        await db.execute(
            select(UserRoleAssignment)
            .where(UserRoleAssignment.user_id == user_id)
            .options(selectinload(UserRoleAssignment.role))
        )
    ).scalars().all()

    return UserAccessRead(
        id=user.id,
        email=user.email,
        legacy_role=user.role,
        is_active=user.is_active,
        roles=[_assignment_to_read(a) for a in assignments],
        permission_codes=sorted(effective),
    )


@router.post("/users/{user_id}/roles", status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_id: int,
    body: UserRoleAssign,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("system.users.manage"))],
) -> UserRoleRead:
    user_result = await db.execute(select(User).where(User.id == user_id))
    if user_result.scalar_one_or_none() is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    role_result = await db.execute(select(Role).where(Role.id == body.role_id))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")

    await validate_role_assignment(db, current, user_id, body.role_id)

    existing = await db.execute(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == body.role_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Role already assigned")

    db.add(UserRoleAssignment(user_id=user_id, role_id=body.role_id))
    await db.commit()
    return UserRoleRead(
        role_id=role.id,
        role_name=role.name,
        role_type=role.role_type,
        department=role.department,
    )


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(
    user_id: int,
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(require_permission("system.users.manage"))],
) -> None:
    assert_not_self_user_target(current, user_id)
    await validate_role_assignment(db, current, user_id, role_id)
    result = await db.execute(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    await db.delete(assignment)
    await db.commit()
