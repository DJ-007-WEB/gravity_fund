import secrets
import logging
from app.core.config import settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

OTP_MAX_ATTEMPTS = 5


class OTPServiceUnavailable(Exception):
    """Raised when the OTP service cannot reach Redis."""


def generate_otp_code() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP code."""
    return f"{secrets.randbelow(1000000):06d}"


async def store_otp_in_redis(email: str, otp_code: str) -> bool:
    """Store OTP in Redis with expiration defined in config."""
    key = f"otp:{email.lower().strip()}"
    attempts_key = f"otp_attempts:{email.lower().strip()}"
    ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60
    try:
        await redis_client.set(key, otp_code, ex=ttl_seconds)
        await redis_client.delete(attempts_key)
        return True
    except Exception as e:
        logger.error(f"Failed to store OTP in Redis: {e}")
        raise OTPServiceUnavailable from e


async def verify_otp_from_redis(email: str, otp_code: str) -> bool:
    """Verify submitted OTP and invalidate it after too many failed attempts or successful use."""
    normalized_email = email.lower().strip()
    key = f"otp:{normalized_email}"
    attempts_key = f"otp_attempts:{normalized_email}"
    ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60

    try:
        stored_otp = await redis_client.get(key)
        if not stored_otp:
            return False

        if stored_otp == otp_code.strip():
            await redis_client.delete(key)
            await redis_client.delete(attempts_key)
            return True

        attempts = await redis_client.incr(attempts_key)
        if attempts == 1:
            await redis_client.expire(attempts_key, ttl_seconds)

        if attempts >= OTP_MAX_ATTEMPTS:
            await redis_client.delete(key)
            await redis_client.delete(attempts_key)

        return False
    except OTPServiceUnavailable:
        raise
    except Exception as e:
        logger.error(f"Failed to verify OTP from Redis: {e}")
        raise OTPServiceUnavailable from e
