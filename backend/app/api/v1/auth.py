from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import (
    get_password_hash,
    create_access_token,
    token_fingerprint,
    ALGORITHM,
)
from app.db.models.user import User
from app.schemas.user import Token, OTPRequest, OTPVerify
from app.services.otp_service import generate_otp_code, store_otp_in_redis, verify_otp_from_redis
from app.services.email_service import send_verification_otp_email
from app.services.auth_service import authenticate_user
from app.api.deps import get_db, get_current_user, oauth2_scheme
from app.api.middleware.rate_limit import RateLimiter

router = APIRouter()


@router.post(
    "/request-otp",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Step 1: Check email availability, generate 6-digit OTP, store in Redis, and send email.
    """
    stmt = select(User).where(User.email == data.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered."
        )

    otp_code = generate_otp_code()
    stored = await store_otp_in_redis(data.email, otp_code)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate verification code. Please try again."
        )

    await send_verification_otp_email(data.email, otp_code)
    return {"message": "Verification code sent to your email address."}


@router.post(
    "/verify-otp-and-signup",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))]
)
async def verify_otp_and_signup(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    """
    Step 2: Verify 6-digit OTP code from Redis, create User record in DB, and return JWT token.
    """
    valid = await verify_otp_from_redis(data.email, data.otp_code)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code."
        )

    stmt = select(User).where(User.email == data.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email is already registered."
        )

    hashed_password = get_password_hash(data.password)
    new_user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hashed_password,
        is_active=True
    )

    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email is already registered."
        )
    await db.refresh(new_user)

    access_token = create_access_token(subject=new_user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate user credentials using OAuth2 form data
    and issue a JWT access token.

    The OAuth2 username field contains the user's email.
    """
    user = await authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive."
        )

    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Log out the user by blacklisting their current JWT token in Redis.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")

        if exp_timestamp:
            now = datetime.now(timezone.utc).timestamp()
            remaining_seconds = int(exp_timestamp - now)

            if remaining_seconds > 0:
                await redis_client.set(
                    f"blacklist:{token_fingerprint(token)}", "1", ex=remaining_seconds
                )

    except JWTError:
        pass

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=Token)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve current authenticated user details."""
    return current_user
