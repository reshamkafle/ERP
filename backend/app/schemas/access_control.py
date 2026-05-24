from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.role import Department, RoleType
from app.models.user import UserRole


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    module: str
    description: str | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    role_type: RoleType
    department: Department | None
    is_system: bool
    description: str | None = None
    permission_codes: list[str] = []


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    role_type: RoleType = RoleType.EMPLOYEE
    department: Department | None = None
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    role_type: RoleType | None = None
    department: Department | None = None
    description: str | None = None


class RolePermissionsUpdate(BaseModel):
    permission_codes: list[str]


class UserRoleAssign(BaseModel):
    role_id: int


class UserPermissionsRead(BaseModel):
    permissions: list[str]


class UserPermissionsUpdate(BaseModel):
    permission_codes: list[str]


class UserRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int
    role_name: str
    role_type: RoleType
    department: Department | None


class UserAccessRead(BaseModel):
    id: int
    email: str
    legacy_role: UserRole
    is_active: bool
    roles: list[UserRoleRead]
    permission_codes: list[str]
