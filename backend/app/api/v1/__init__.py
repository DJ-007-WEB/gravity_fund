from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.profiles import router as profile_router

# The main API Router for v1 endpoints
api_router = APIRouter()

api_router.include_router(health_router, tags=["system"])

# Mount authentication endpoints under /api/v1/auth
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])
