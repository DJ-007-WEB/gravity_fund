import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from app.core.config import settings

# HS256 stands for HMAC using SHA-256 hash algorithm.
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its stored bcrypt hash.
    """
    try:
        # bcrypt requires bytes for checking. We encode our strings to utf-8.
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    # bcrypt.gensalt() generates a secure random salt.
    # bcrypt.hashpw hashes the byte representation of the password.
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Decode the resulting bytes back into a UTF-8 string so we can store it in the database.
    return hashed.decode("utf-8")

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Generate a signed JSON Web Token (JWT) with the given subject (User ID).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Payload claims:
    # - sub: Subject (unique identifier of the user)
    # - exp: Expiration timestamp (seconds since epoch)
    to_encode = {"sub": str(subject), "exp": expire}
    
    # Cryptographically sign and encode the token using our secret key
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
