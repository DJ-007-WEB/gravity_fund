from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

# The main API Router for v1 endpoints
api_router = APIRouter()

# Mount authentication endpoints under /api/v1/auth
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
