from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.redis import redis_client
from app.db.session import engine

router = APIRouter()


@router.get("/health")
async def health():
    """Liveness endpoint: process is able to serve requests."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness():
    """Readiness endpoint: required backing services are reachable."""
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        await redis_client.ping()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Required services are unavailable.",
        ) from exc
    return {"status": "ready"}
