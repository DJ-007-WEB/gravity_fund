import hashlib

from fastapi import Request, HTTPException, status
from app.core.redis import redis_client


RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])

if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

return current
"""


class RateLimiter:
    """
    A Redis-backed rate limiting dependency for FastAPI routes.

    The request counter and its initial expiration are updated atomically
    using a Redis Lua script so the counter cannot be created without its TTL.
    """

    def __init__(self, times: int, seconds: int):
        """
        :param times: Number of allowed requests in the time window.
        :param seconds: Length of the time window in seconds.
        """
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"ratelimit:{client_ip}:{path}"

        current = await redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            self.seconds,
        )

        if current > self.times:
            ttl = await redis_client.ttl(key)
            retry_after = ttl if ttl > 0 else self.seconds

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )


class AccountRateLimiter:
    """
    Rate limiter keyed by a normalized account identifier (email) instead of
    only by client IP. The identifier is hashed before being stored in Redis.

    This protects authentication endpoints when an attacker distributes
    requests across multiple IP addresses.
    """

    def __init__(self, times: int, seconds: int, field_name: str, source: str):
        self.times = times
        self.seconds = seconds
        self.field_name = field_name
        self.source = source

    async def __call__(self, request: Request):
        if self.source == "form":
            form = await request.form()
            identifier = form.get(self.field_name)
        elif self.source == "json":
            try:
                payload = await request.json()
            except ValueError:
                identifier = None
            else:
                identifier = payload.get(self.field_name)
        else:
            raise RuntimeError("Unsupported rate limiter request source")

        if not isinstance(identifier, str):
            return

        identifier = identifier.strip().lower()
        if not identifier:
            return

        identifier_hash = hashlib.sha256(identifier.encode("utf-8")).hexdigest()
        key = f"ratelimit:account:{self.field_name}:{identifier_hash}"

        current = await redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            self.seconds,
        )

        if current > self.times:
            ttl = await redis_client.ttl(key)
            retry_after = ttl if ttl > 0 else self.seconds

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )
