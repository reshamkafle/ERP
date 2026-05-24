"""Double-submit CSRF cookie helpers for cookie-based session auth."""

import secrets

from fastapi import Response

from app.core.config import get_settings

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=CSRF_COOKIE,
        value=token,
        httponly=False,
        secure=settings.is_deployed,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def clear_csrf_cookie(response: Response) -> None:
    settings = get_settings()
    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
        secure=settings.is_deployed,
        samesite="lax",
    )
