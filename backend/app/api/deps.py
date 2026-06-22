from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator that yields a database session.
    Guarantees the session is closed after the request completes.
    """
    async with SessionLocal() as session:
        yield session
