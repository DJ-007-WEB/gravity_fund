from datetime import date
from sqlalchemy import String, ForeignKey, Integer, Date, Numeric, BigInteger, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(50), nullable=False)  # equity, bond, commodity, cash

    # One-to-Many relationship with HistoricalPrice
    prices: Mapped[list["HistoricalPrice"]] = relationship(
        "HistoricalPrice", back_populates="asset", cascade="all, delete-orphan"
    )


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Financial metrics are best stored in Numeric/Float for precision
    open: Mapped[float] = mapped_column(Numeric(precision=12, scale=4), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(precision=12, scale=4), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(precision=12, scale=4), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(precision=12, scale=4), nullable=False)
    adj_close: Mapped[float] = mapped_column(Numeric(precision=12, scale=4), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Inverse relationship linking price back to its Asset
    asset: Mapped["Asset"] = relationship("Asset", back_populates="prices")

    # Table arguments define custom indexes and constraints
    __table_args__ = (
        # Ensure we don't have multiple price rows for the same asset on the same date
        UniqueConstraint("asset_id", "date", name="uq_historical_prices_asset_date"),
        # Speed up timeseries queries filtering by asset and date range
        Index("idx_historical_prices_asset_date", "asset_id", "date"),
    )
