from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: UserRole
    is_active: bool


class LoginResponse(BaseModel):
    """Session token is set only via HttpOnly cookie; not returned in JSON."""

    user: UserPublic
    permissions: list[str] = []
