from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import redis_client
from app.api.v1.router import api_router
from app.api.middleware.request_id import RequestIdMiddleware
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Release network resources only after in-flight requests have completed.
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="Gravity Fund API",
    description="Quantitative Retail Wealth Optimization Platform",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.add_middleware(RequestIdMiddleware)

# Register the master versioned router under /api/v1 prefix
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Gravity Fund API"}
