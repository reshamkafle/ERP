"""Idempotent security-related schema sync."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection


async def sync_security_schema(conn: AsyncConnection) -> None:
    def _missing_token_version(sync_conn) -> bool:
        insp = inspect(sync_conn)
        cols = {c["name"] for c in insp.get_columns("users")}
        return "token_version" not in cols

    missing = await conn.run_sync(_missing_token_version)
    if missing:
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN token_version INTEGER NOT NULL DEFAULT 0"),
        )
