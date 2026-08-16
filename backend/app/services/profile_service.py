from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.user import User, UserProfile
from app.schemas.profile import ProfileUpsert
from app.services.risk_scoring import calculate_risk_assessment


async def get_user_with_profile(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    return result.scalar_one()


async def upsert_profile(
    db: AsyncSession, user: User, profile_in: ProfileUpsert
) -> UserProfile:
    assessment = calculate_risk_assessment(profile_in.risk_tolerance_answers)
    profile = user.profile

    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    profile.age = profile_in.age
    profile.annual_income = profile_in.annual_income
    profile.monthly_expenses = profile_in.monthly_expenses
    profile.investment_horizon_years = profile_in.investment_horizon_years
    profile.risk_tolerance_answers = profile_in.risk_tolerance_answers.model_dump()
    profile.risk_score = assessment.risk_score
    profile.risk_category = assessment.risk_category
    profile.suggested_equity_allocation_range = assessment.suggested_equity_allocation_range

    await db.commit()
    await db.refresh(profile)
    return profile
