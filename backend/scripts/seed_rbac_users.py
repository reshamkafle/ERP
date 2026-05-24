#!/usr/bin/env python3
"""Seed 50 RBAC test users with full permission coverage (idempotent)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.bootstrap import seed_admin_user
from app.core.database import AsyncSessionLocal, init_db
from app.core.rbac_bootstrap import (
    assign_legacy_user_roles,
    seed_permissions,
    seed_system_roles,
)
from app.core.seed_rbac_users import seed_rbac_users


async def main() -> None:
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
        perms = await seed_permissions(session)
        roles = await seed_system_roles(session, perms)
        await assign_legacy_user_roles(session, roles)
        result = await seed_rbac_users(session)
        await session.commit()

    print("RBAC user seed complete.")
    print(f"  Users created: {result.created_users}")
    print(f"  Users skipped (already exist): {result.skipped_users}")
    print(f"  Custom roles created: {result.created_roles}")
    if result.credentials_path:
        print(f"  Credentials: {result.credentials_path}")


if __name__ == "__main__":
    asyncio.run(main())
