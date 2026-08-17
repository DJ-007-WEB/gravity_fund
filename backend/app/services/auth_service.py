from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash,verify_password
from app.db.models.user import User


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Return the user when the supplied credentials are valid."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user

async def create_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    password: str,
) -> User:
    """Create and persist a new user."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    if result.scalar_one_or_none():
        raise ValueError("A user with this email is already registered.")

    hashed_password = get_password_hash(password)

    user = User(
        email=email,
        full_name=full_name,
        password_hash=hashed_password,
        is_active=True,
    )

    db.add(user)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    await db.refresh(user)

    return user
