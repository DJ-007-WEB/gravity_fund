import asyncio
import sys
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure the 'backend' folder is in Python's search path so it can resolve the 'app' module imports.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.redis import redis_client

async def test_postgres():
    print("Connecting to PostgreSQL...")
    # 1. Initialize our async database connection engine
    # echo=True prints all executed SQL statements to the console so we can see the exact communication.
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # 2. Acquire an active connection from the pool
    async with engine.connect() as conn:
        # Execute a minimal query 'SELECT 1' to verify communication
        result = await conn.execute(text("SELECT 1"))
        # .scalar() returns the first column of the first row
        val = result.scalar()
        print(f"PostgreSQL connection successful! (Result of SELECT 1: {val})")
    
    # 3. Clean up the engine and close any open connections in the pool
    await engine.dispose()

async def test_redis():
    print("Connecting to Redis...")
    # 1. Set a temporary key 'test_connection_key' that expires in 60 seconds (ex=60)
    await redis_client.set("test_connection_key", "Redis is connected and working!", ex=60)
    
    # 2. Retrieve that key's value to verify read works
    value = await redis_client.get("test_connection_key")
    print(f"Redis connection successful! (Retrieved value: '{value}')")
    
    # 3. Clean up and delete the test key
    await redis_client.delete("test_connection_key")
    
    # 4. Explicitly close the Redis connection pool
    await redis_client.aclose()

async def main():
    try:
        await test_postgres()
        print("-" * 50)
        await test_redis()
        print("-" * 50)
        print("All infrastructure connections verified successfully!")
    except Exception as e:
        print(f"Verification failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
