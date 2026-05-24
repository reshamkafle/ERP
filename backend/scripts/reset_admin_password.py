#!/usr/bin/env python3
"""Reset the bootstrap admin password to match backend/.env ADMIN_PASSWORD."""
import asyncio
import sys

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User


async def main() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == settings.admin_email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            print(f"No user found for {settings.admin_email}")
            sys.exit(1)
        user.hashed_password = get_password_hash(settings.admin_password)
        user.is_active = True
        await session.commit()
        print(f"Reset password for {settings.admin_email}")
        print(f"Use password from ADMIN_PASSWORD in backend/.env")


if __name__ == "__main__":
    asyncio.run(main())
