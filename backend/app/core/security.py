import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from uuid import uuid4
from jose import JWTError, jwt
from app.core.config import settings

# HS256 stands for HMAC using SHA-256 hash algorithm.
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    """
    Generate a signed JWT with a unique token ID, issued-at time, subject, and expiration.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate an access token's signature and required claims.

    Raises JWTError when the token is invalid, expired, or missing required claims.
    """
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])

    user_id = payload.get("sub")
    jti = payload.get("jti")
    issued_at = payload.get("iat")

    if not isinstance(user_id, str) or not user_id.isdigit() or int(user_id) <= 0:
        raise JWTError("Invalid subject claim")

    if not isinstance(jti, str) or not jti.strip():
        raise JWTError("Invalid token ID claim")

    if issued_at is None:
        raise JWTError("Missing issued-at claim")

    return payload
