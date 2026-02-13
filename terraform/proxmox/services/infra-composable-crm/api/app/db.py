from __future__ import annotations

import asyncpg
from typing import AsyncGenerator, Optional

from fastapi import Request


async def init_db_pool(dsn: str, min_size: int = 1, max_size: int = 10) -> asyncpg.Pool:
    """
    Create the asyncpg pool.
    Keep it small by default; you can tune later.
    """
    return await asyncpg.create_pool(
        dsn=dsn,
        min_size=min_size,
        max_size=max_size,
        command_timeout=30,
    )


async def get_db(request: Request) -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency: yields an asyncpg connection from app.state.db_pool
    """
    pool: Optional[asyncpg.Pool] = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("DB pool is not initialized (app.state.db_pool is missing)")

    async with pool.acquire() as conn:
        yield conn
