from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.redis import redis_client
from app.api.v1 import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic runs before the app starts receiving requests
    yield
    # Shutdown logic runs before the app finishes terminating
    # Close Redis client connection pool gracefully
    await redis_client.aclose()


app = FastAPI(
    title="Gravity Fund API",
    description="Quantitative Retail Wealth Optimization Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Register the master versioned router under /api/v1 prefix
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Gravity Fund API"}
