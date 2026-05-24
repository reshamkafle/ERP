from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    # Plain str so dev seed users (e.g. rbac-01@seed.local) can authenticate.
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1)
