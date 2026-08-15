import secrets
import logging
from app.core.config import settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)


def generate_otp_code() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP code."""
    return f"{secrets.randbelow(1000000):06d}"


async def store_otp_in_redis(email: str, otp_code: str) -> bool:
    """Store OTP in Redis with expiration defined in config."""
    key = f"otp:{email.lower().strip()}"
    ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60
    try:
        await redis_client.set(key, otp_code, ex=ttl_seconds)
        return True
    except Exception as e:
        logger.error(f"Failed to store OTP in Redis: {e}")
        return False


async def verify_otp_from_redis(email: str, otp_code: str) -> bool:
    """Verify submitted OTP code against Redis stored key. Deletes key on successful verification."""
    key = f"otp:{email.lower().strip()}"
    try:
        stored_otp = await redis_client.get(key)
        if not stored_otp:
            return False

        if stored_otp == otp_code.strip():
            # Delete OTP after single successful use
            await redis_client.delete(key)
            return True
            
        return False
    except Exception as e:
        logger.error(f"Failed to verify OTP from Redis: {e}")
        return False
