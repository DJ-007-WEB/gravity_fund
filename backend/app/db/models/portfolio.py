from datetime import datetime
from typing import Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Can be 'pending', 'optimized', 'failed'
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    
    # Store inputs (e.g. max weight constraint, risk model selection)
    optimization_params: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Store output weights (e.g. {"NIFTYBEES.NS": 0.45, "GOLDBEES.NS": 0.20})
    result_weights: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Store output metrics (e.g. {"sharpe_ratio": 1.25, "max_drawdown": -0.15})
    risk_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationship linking back to the owning User
    user: Mapped["User"] = relationship("User", back_populates="portfolios")
