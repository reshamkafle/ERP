import pytest
from fastapi import HTTPException

from app.models.role import Role, RoleType
from app.services.role_security import assert_role_mutable, assert_role_type_assignable


def test_assert_role_type_assignable_rejects_super_admin() -> None:
    with pytest.raises(HTTPException) as exc:
        assert_role_type_assignable(RoleType.SUPER_ADMIN)
    assert exc.value.status_code == 400


def test_assert_role_type_assignable_allows_employee() -> None:
    assert_role_type_assignable(RoleType.EMPLOYEE) is None


def test_assert_role_mutable_rejects_system_role() -> None:
    role = Role(name="System", role_type=RoleType.ADMIN, is_system=True)
    with pytest.raises(HTTPException) as exc:
        assert_role_mutable(role)
    assert exc.value.status_code == 400


def test_assert_role_mutable_allows_custom_role() -> None:
    role = Role(name="Custom", role_type=RoleType.EMPLOYEE, is_system=False)
    assert_role_mutable(role) is None
