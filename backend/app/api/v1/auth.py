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
    verify_password,
    create_access_token,
    token_fingerprint,
    ALGORITHM,
)
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.api.deps import get_db, get_current_user, oauth2_scheme
from app.api.middleware.rate_limit import RateLimiter

router = APIRouter()

@router.post(
    "/signup", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    Limited to 10 requests per minute to prevent registration spam.
    """
    # 1. Check if email is already registered
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered."
        )
        
    # 2. Hash the password and save user
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        # The database unique constraint is the authoritative protection against
        # two simultaneous requests registering the same email address.
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email is already registered.",
        )
    await db.refresh(new_user)
    
    return new_user


@router.post(
    "/login", 
    response_model=Token,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user credentials (email/password) and issue a JWT token.
    Accepts standard OAuth2 form-data payload (username=email, password=password).
    Limited to 10 requests per minute to prevent brute-force attacks.
    """
    # 1. Fetch user by email (mapped to form_data.username)
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # 2. Verify email and decrypt password hash
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive."
        )
        
    # 4. Create and return token
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Log out the user by blacklisting their current JWT token in Redis
    for its remaining lifetime.
    """
    try:
        # Decode the token to read its expiration claim
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")
        
        if exp_timestamp:
            now = datetime.now(timezone.utc).timestamp()
            remaining_seconds = int(exp_timestamp - now)
            
            # If the token is still technically valid, store it in Redis blacklist
            if remaining_seconds > 0:
                await redis_client.set(
                    f"blacklist:{token_fingerprint(token)}", "1", ex=remaining_seconds
                )
                
    except JWTError:
        # If token is invalid or corrupt, we ignore and consider it successfully deactivated
        pass
        
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve current authenticated user details.
    """
    return current_user

