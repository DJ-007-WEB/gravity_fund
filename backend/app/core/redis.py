import redis.asyncio as aioredis
from app.core.config import settings

# Initialize a Redis connection pool.
# Using decode_responses=True automatically decodes binary data from Redis into UTF-8 strings.
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)
