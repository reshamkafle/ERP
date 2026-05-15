from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.crud.user import authenticate_user
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.token import LoginRequest
from app.schemas.user import LoginResponse, UserPublic

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    user = await authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(str(user.id), role=user.role.value)
    return LoginResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
async def read_me(current: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current)
