from fastapi import APIRouter
from app.db.pool import get_pool

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/ready")
async def ready():
    pool = await get_pool()
    async with pool.acquire() as conn:
        v = await conn.fetchval("SELECT 1;")
    return {"db": "ok" if v == 1 else "down"}
