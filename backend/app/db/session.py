from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# create_async_engine creates a pool of connections to the database.
# We use PostgreSQL with the asyncpg driver (defined in DATABASE_URL).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,           # Set to True if you want to see all raw SQL queries printed in console
    future=True,   
    pool_pre_ping = True        # Ensures we use SQLAlchemy 2.0 style APIs
)

# async_sessionmaker is a factory for creating AsyncSession objects.
# expire_on_commit=False prevents SQLAlchemy from automatically expired objects 
# after commit, which is crucial for async execution.
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)
