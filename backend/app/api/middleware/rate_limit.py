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
        # 1. Extract the client's host IP address
        client_ip = request.client.host if request.client else "unknown"

        # 2. Extract the current request path (so limits are per-route, not global)
        path = request.url.path

        # 3. Create a unique key name in Redis namespace
        key = f"ratelimit:{client_ip}:{path}"

        # 4. Increment the counter and set its expiration atomically.
        current = await redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            self.seconds,
        )

        # 5. If the count exceeds our threshold, block the request
        if current > self.times:
            # Query the remaining time until the limit resets
            ttl = await redis_client.ttl(key)
            retry_after = ttl if ttl > 0 else self.seconds

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )
