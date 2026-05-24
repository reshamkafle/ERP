"""Validate CSRF token on mutating requests that use session cookies."""

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.auth_cookies import ACCESS_TOKEN_COOKIE
from app.core.csrf import CSRF_COOKIE, CSRF_HEADER

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_CSRF_EXEMPT_PATHS = frozenset(
    {
        "/api/v1/auth/login",
    },
)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in _UNSAFE_METHODS and request.url.path not in _CSRF_EXEMPT_PATHS:
            has_session_cookie = ACCESS_TOKEN_COOKIE in request.cookies
            auth_header = request.headers.get("authorization", "")
            uses_bearer = auth_header.lower().startswith("bearer ")
            if has_session_cookie and not uses_bearer:
                cookie_token = request.cookies.get(CSRF_COOKIE)
                header_token = request.headers.get(CSRF_HEADER)
                if not cookie_token or not header_token or cookie_token != header_token:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF validation failed"},
                    )
        return await call_next(request)
