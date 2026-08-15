from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.profile import ProfileUpsert, UserProfileResponse
from app.services.profile_service import upsert_profile

router = APIRouter()


async def _user_with_profile(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    return result.scalar_one()


@router.get("", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user = await _user_with_profile(db, current_user.id)
    if user.profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return user.profile


@router.put("", response_model=UserProfileResponse)
async def put_profile(
    profile_in: ProfileUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await _user_with_profile(db, current_user.id)
    return await upsert_profile(db, user, profile_in)
