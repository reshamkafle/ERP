#!/usr/bin/env python3
"""Truncate all local dev PostgreSQL data and re-seed admin + RBAC only.

Requires ENVIRONMENT=development, localhost database, SEED_DEMO_DATA=false, and --confirm.
Stop uvicorn before running.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse

# Allow `python scripts/clear_database.py` from backend/ without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core.bootstrap import seed_admin_user
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.core.rbac_bootstrap import assign_legacy_user_roles, seed_permissions, seed_system_roles

_ALLOWED_DB_HOSTS = frozenset({"localhost", "127.0.0.1"})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clear all ERP database rows (local dev only).")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required: acknowledge irreversible data loss.",
    )
    return parser.parse_args()


def _assert_safety(settings) -> None:
    if settings.environment.lower() != "development":
        print(f"Refusing: ENVIRONMENT must be 'development' (got {settings.environment!r}).")
        sys.exit(1)

    parsed = urlparse(settings.database_url.replace("+asyncpg", ""))
    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_DB_HOSTS:
        print(f"Refusing: database host must be localhost (got {host!r}).")
        sys.exit(1)

    if settings.seed_demo_data:
        print("Refusing: set SEED_DEMO_DATA=false in backend/.env before running.")
        print("This prevents demo BOM/garment/module data from reloading on backend restart.")
        sys.exit(1)


async def _list_public_tables(session) -> list[str]:
    result = await session.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename != 'alembic_version'
            ORDER BY tablename
            """
        )
    )
    return [row[0] for row in result.fetchall()]


async def _truncate_all(session, tables: list[str]) -> None:
    if not tables:
        return
    quoted = ", ".join(f'"{name}"' for name in tables)
    await session.execute(
        text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"),
    )


async def run_clear() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        tables = await _list_public_tables(session)
        print(f"Truncating {len(tables)} tables (alembic_version preserved)...")
        await _truncate_all(session, tables)

        print("Seeding admin user and RBAC catalog...")
        await seed_admin_user(session)
        perms = await seed_permissions(session)
        roles = await seed_system_roles(session, perms)
        await assign_legacy_user_roles(session, roles)
        await session.commit()

    print("Done.")
    print(f"  Tables truncated: {len(tables)}")
    print(f"  Admin login: {settings.admin_email} (password from ADMIN_PASSWORD in backend/.env)")
    print("  Restart uvicorn; demo seeds are disabled (SEED_DEMO_DATA=false).")


def main() -> None:
    args = _parse_args()
    if not args.confirm:
        print("Refusing: pass --confirm to acknowledge irreversible data loss.")
        sys.exit(1)

    settings = get_settings()
    _assert_safety(settings)
    asyncio.run(run_clear())


if __name__ == "__main__":
    main()
