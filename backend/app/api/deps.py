from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.db.models.user import User

# Define the OAuth2 scheme. FastAPI will use this to document security requirements in Swagger
# and read the Authorization header from client requests.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator that yields an active database session.
    Guarantees the session is closed after the request completes.
    """
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency that validates the JWT token from the request header,
    checks if it has been blacklisted, and returns the current authenticated User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Check if the token has been blacklisted (invalidated via logout)
    from app.core.security import token_fingerprint

    is_blacklisted = await redis_client.get(f"blacklist:{token_fingerprint(token)}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or logged out. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # 2. Decode the JWT token and extract user claims
        from app.core.security import ALGORITHM
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
        
    # 3. Retrieve the user from the database
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
        
    # 4. Check if the user's account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
        
    return user
