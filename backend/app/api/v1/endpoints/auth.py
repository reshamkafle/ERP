import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_cookies import ACCESS_TOKEN_COOKIE, clear_access_token_cookie, set_access_token_cookie
from app.core.csrf import clear_csrf_cookie, generate_csrf_token, set_csrf_cookie
from app.core.database import get_db
from app.core.login_lockout import clear_failures, is_locked, record_failure
from app.core.rate_limit import limiter
from app.core.security import create_access_token, decode_token
from app.crud.user import authenticate_user
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.access_control import UserPermissionsRead
from app.schemas.token import LoginRequest
from app.schemas.user import LoginResponse, UserPublic
from app.services.permission_service import get_user_permissions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    locked, seconds_remaining = is_locked(body.email)
    if locked:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked. Try again in {seconds_remaining} seconds.",
        )

    user = await authenticate_user(db, body.email, body.password)
    if user is None:
        record_failure(body.email)
        client_ip = request.client.host if request.client else "unknown"
        logger.warning("Failed login email=%s ip=%s", body.email, client_ip)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    clear_failures(body.email)
    token = create_access_token(
        str(user.id),
        role=user.role.value,
        token_version=int(user.token_version),
    )
    set_access_token_cookie(response, token)
    set_csrf_cookie(response, generate_csrf_token())
    codes = await get_user_permissions(db, user)
    return LoginResponse(
        user=UserPublic.model_validate(user),
        permissions=sorted(codes),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> None:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if token:
        payload = decode_token(token)
        if payload and payload.get("sub") is not None:
            try:
                user_id = int(str(payload["sub"]))
                token_version = int(payload.get("tv", 0))
            except (TypeError, ValueError):
                user_id = None
                token_version = None
            if user_id is not None and token_version is not None:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user is not None and int(user.token_version) == token_version:
                    user.token_version = int(user.token_version) + 1
                    await db.commit()
    clear_access_token_cookie(response)
    clear_csrf_cookie(response)


@router.get("/me", response_model=UserPublic)
async def read_me(current: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current)


@router.get("/me/permissions", response_model=UserPermissionsRead)
async def read_my_permissions(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPermissionsRead:
    codes = await get_user_permissions(db, current)
    return UserPermissionsRead(permissions=sorted(codes))
