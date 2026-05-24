"""HttpOnly session cookie helpers for JWT auth."""

from fastapi import Response

from app.core.config import get_settings

ACCESS_TOKEN_COOKIE = "access_token"


def set_access_token_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    max_age = settings.access_token_expire_minutes * 60
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=token,
        httponly=True,
        secure=settings.is_deployed,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def clear_access_token_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE,
        path="/",
        secure=settings.is_deployed,
        samesite="lax",
    )
