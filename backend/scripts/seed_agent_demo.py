#!/usr/bin/env python3
"""Seed Postgres with demo data for agent simulation (idempotent)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.bootstrap import seed_admin_user
from app.core.database import AsyncSessionLocal, init_db
from app.testing.seed_agent_demo import DEMO_SKUS, ensure_procurement_run_enum_sync, seed_agent_demo_data


async def main() -> None:
    ensure_procurement_run_enum_sync()
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session)
        result = await seed_agent_demo_data(session)
        await session.commit()
    if result.get("skipped"):
        print(f"Demo seed skipped: {result.get('reason')}")
    else:
        print("Agent demo seed complete.")
        print(f"  SKUs: {', '.join(DEMO_SKUS)}")
        print(f"  supplier_id={result.get('supplier_id')}")


if __name__ == "__main__":
    asyncio.run(main())
