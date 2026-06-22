from fastapi import Request, HTTPException, status
from app.core.redis import redis_client

class RateLimiter:
    """
    A Redis-backed rate limiting dependency for FastAPI routes.
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
        
        # 4. Atomically increment the request count in Redis.
        # If the key does not exist, Redis creates it with value 0, then increments it to 1.
        current = await redis_client.incr(key)
        
        # 5. If this is the first request of the window, set its expiration time
        if current == 1:
            await redis_client.expire(key, self.seconds)
            
        # 6. If the count exceeds our threshold, block the request
        if current > self.times:
            # Query the remaining time until the limit resets
            ttl = await redis_client.ttl(key)
            retry_after = ttl if ttl > 0 else self.seconds
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
