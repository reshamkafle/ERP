import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_cookies import ACCESS_TOKEN_COOKIE
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.permission_service import get_user_permissions

logger = logging.getLogger(__name__)

http_bearer = HTTPBearer(auto_error=False)


def _extract_bearer_token(creds: HTTPAuthorizationCredentials | None) -> str | None:
    if creds is None or not creds.credentials:
        return None
    if creds.scheme.lower() != "bearer":
        return None
    return creds.credentials


async def get_current_user(
    request: Request,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token = _extract_bearer_token(creds) or request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if creds is not None and creds.credentials and creds.scheme.lower() != "bearer":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    payload = decode_token(token)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    token_version = payload.get("tv", 0)
    try:
        token_version = int(token_version)
    except (TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token version")
    try:
        user_id = int(str(payload["sub"]))
    except (TypeError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled")
    if int(user.token_version) != token_version:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return user


async def get_current_user_permissions(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> set[str]:
    return await get_user_permissions(db, user)


def require_permission(*codes: str):
    """Require at least one of the given permission codes."""

    async def _checker(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        perms = await get_user_permissions(db, user)
        if any(code in perms for code in codes):
            return user
        logger.warning(
            "Permission denied user_id=%s required_any=%s",
            user.id,
            list(codes),
        )
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this resource",
        )

    return _checker


def require_all_permissions(*codes: str):
    """Require all of the given permission codes."""

    async def _checker(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        perms = await get_user_permissions(db, user)
        if all(code in perms for code in codes):
            return user
        logger.warning(
            "Permission denied user_id=%s required_all=%s",
            user.id,
            list(codes),
        )
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for this resource",
        )

    return _checker


# Deprecated: kept for gradual migration references
from app.models.user import UserRole  # noqa: E402


def require_roles(*allowed: UserRole):
    async def _checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="Insufficient permissions for this resource"
            )
        return user

    return _checker
