import json
import asyncpg
from typing import AsyncGenerator
from app.core.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec(
        "json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        if not settings.crm_db_dsn:
            raise RuntimeError("CRM_DB_DSN not configured")

        _pool = await asyncpg.create_pool(
            dsn=settings.crm_db_dsn,
            min_size=1,
            max_size=10,
            command_timeout=30,
            init=_init_connection,   # 👈 🔥 ESTA es la clave
        )
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency: yields a connection from the global pool.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn