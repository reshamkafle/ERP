from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import UserRoleAssignment
from app.models.user import User
from app.services.permission_service import assert_can_delegate, get_user_permissions, role_permission_codes

_SELF_GRANT_MSG = (
    "You cannot assign permissions or roles to yourself. "
    "Another user who already holds those permissions must grant them."
)


def assert_not_self_user_target(grantor: User, target_user_id: int) -> None:
    if grantor.id == target_user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=_SELF_GRANT_MSG)


async def assert_role_not_assigned_to_grantor(
    session: AsyncSession,
    grantor: User,
    role_id: int,
) -> None:
    """Block editing a role's permissions when that role is assigned to the grantor (self-escalation)."""
    result = await session.execute(
        select(UserRoleAssignment.id).where(
            UserRoleAssignment.user_id == grantor.id,
            UserRoleAssignment.role_id == role_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=_SELF_GRANT_MSG,
        )


async def validate_permission_grant(
    session: AsyncSession,
    grantor: User,
    requested_codes: set[str],
) -> None:
    grantor_codes = await get_user_permissions(session, grantor)
    try:
        assert_can_delegate(grantor_codes, requested_codes)
    except ValueError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


async def validate_user_permission_update(
    session: AsyncSession,
    grantor: User,
    target_user: User,
    desired_codes: set[str],
) -> None:
    """Grantor may set user permissions; new grants beyond roles require delegation."""
    assert_not_self_user_target(grantor, target_user.id)
    from app.services.permission_service import get_role_based_permissions

    role_codes = await get_role_based_permissions(session, target_user)
    new_grants = desired_codes - role_codes
    await validate_permission_grant(session, grantor, new_grants)


async def validate_role_assignment(
    session: AsyncSession,
    grantor: User,
    target_user_id: int,
    target_role_id: int,
) -> None:
    """Grantor must hold every permission in the target role; cannot assign roles to self."""
    assert_not_self_user_target(grantor, target_user_id)
    grantor_codes = await get_user_permissions(session, grantor)
    target_codes = await role_permission_codes(session, target_role_id)
    try:
        assert_can_delegate(grantor_codes, target_codes)
    except ValueError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
