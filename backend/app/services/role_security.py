"""Guards for role create/update to prevent privilege escalation."""

from fastapi import HTTPException, status

from app.models.role import Role, RoleType

_SUPER_ADMIN_FORBIDDEN = (
    "SUPER_ADMIN role type cannot be created or assigned via the API"
)
_SYSTEM_ROLE_READONLY = "System roles cannot be modified"


def assert_role_type_assignable(role_type: RoleType) -> None:
    if role_type == RoleType.SUPER_ADMIN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=_SUPER_ADMIN_FORBIDDEN)


def assert_role_mutable(role: Role) -> None:
    if role.is_system:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=_SYSTEM_ROLE_READONLY)
