import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.bootstrap import seed_admin_user
from app.core.config import get_settings
from app.core.csrf_middleware import CSRFMiddleware
from app.core.database import AsyncSessionLocal, engine, init_db
from app.core.rate_limit import limiter
from app.core.rbac_bootstrap import assign_legacy_user_roles, seed_permissions, seed_system_roles
from app.core.security_headers import SecurityHeadersMiddleware
from app.manufacturing.bom.bootstrap import seed_bom_demo_if_empty
from app.modules.seed import seed_module_records_if_empty
from app.services.garment_planning_bootstrap import seed_garment_planning_if_empty


async def _wait_for_database(max_attempts: int = 30, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            await init_db()
            return
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(delay_seconds)
    if last_error:
        raise last_error


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _wait_for_database()
    bootstrap_settings = get_settings()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
        perms = await seed_permissions(session)
        roles = await seed_system_roles(session, perms)
        await assign_legacy_user_roles(session, roles)
        if bootstrap_settings.seed_demo_data:
            await seed_bom_demo_if_empty(session)
            await seed_garment_planning_if_empty(session)
            await seed_module_records_if_empty(session)
        await session.commit()
    yield
    await engine.dispose()


settings = get_settings()
_openapi_docs = None if settings.is_deployed else "/openapi.json"

app = FastAPI(
    title="ERP API",
    lifespan=lifespan,
    docs_url=None if settings.is_deployed else "/docs",
    redoc_url=None if settings.is_deployed else "/redoc",
    openapi_url=_openapi_docs,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "Accept"],
)

app.include_router(api_router, prefix="/api/v1")
