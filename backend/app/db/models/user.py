from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.portfolio import Portfolio


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # One-to-One relationship with UserProfile.
    # uselist=False makes it a 1:1 mapping instead of 1:Many.
    # cascade="all, delete-orphan" ensures profile is deleted when the user is deleted.
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    
    # One-to-Many relationship with Portfolios.
    portfolios: Mapped[list["Portfolio"]] = relationship(
        "Portfolio", back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    # The user_id is both the Primary Key and the Foreign Key referencing the users table.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    annual_income: Mapped[float] = mapped_column(nullable=False)
    monthly_expenses: Mapped[float] = mapped_column(nullable=False)
    investment_horizon_years: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # JSONB is native to PostgreSQL and lets us store arbitrary JSON structures while supporting
    # indexes and fast query paths.
    risk_tolerance_answers: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    risk_score: Mapped[float] = mapped_column(nullable=False)
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Inverse side of the One-to-One relationship.
    user: Mapped["User"] = relationship("User", back_populates="profile")
