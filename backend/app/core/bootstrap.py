from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole


async def seed_admin_user(session: AsyncSession) -> None:
    settings = get_settings()
    result = await session.execute(select(User).where(User.email == settings.admin_email))
    if result.scalar_one_or_none() is not None:
        return
    admin = User(
        email=settings.admin_email,
        hashed_password=get_password_hash(settings.admin_password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    session.add(admin)
    await session.commit()
