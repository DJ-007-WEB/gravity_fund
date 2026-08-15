import logging
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import yfinance as yf
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.asset import Asset, HistoricalPrice

logger = logging.getLogger(__name__)

DEFAULT_UNIVERSE = [
    {
        "ticker": "NIFTYBEES.NS",
        "name": "Nippon India ETF Nifty 50 BeES",
        "asset_class": "equity",
    },
    {
        "ticker": "JUNIORBEES.NS",
        "name": "Nippon India ETF Nifty Next 50 Junior BeES",
        "asset_class": "equity",
    },
    {
        "ticker": "BANKBEES.NS",
        "name": "Nippon India ETF Bank BeES",
        "asset_class": "equity",
    },
    {
        "ticker": "GOLDBEES.NS",
        "name": "Nippon India ETF Gold BeES",
        "asset_class": "commodity",
    },
    {
        "ticker": "LIQUIDBEES.NS",
        "name": "Nippon India ETF Liquid BeES",
        "asset_class": "cash",
    },
    {
        "ticker": "CPSEETF.NS",
        "name": "CPSE ETF",
        "asset_class": "equity",
    },
    {
        "ticker": "SETFNIF50.NS",
        "name": "SBI Nifty 50 ETF",
        "asset_class": "equity",
    },
    {
        "ticker": "LIQUIDETF.NS",
        "name": "DSP Liquid ETF",
        "asset_class": "cash",
    },
    {
        "ticker": "^NSEI",
        "name": "Nifty 50 Index Benchmark",
        "asset_class": "benchmark",
    },
]


async def seed_default_assets(db: AsyncSession) -> List[Asset]:
    """Ensure all default universe assets exist in the database."""
    seeded_assets = []
    for asset_data in DEFAULT_UNIVERSE:
        result = await db.execute(
            select(Asset).where(Asset.ticker == asset_data["ticker"])
        )
        existing = result.scalar_one_or_none()
        if not existing:
            existing = Asset(**asset_data)
            db.add(existing)
            await db.flush()
        seeded_assets.append(existing)

    await db.commit()
    return seeded_assets


def validate_and_clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Apply data quality gates specified in MVP_DATA_PLAN.md:
    
    1. Filter out non-positive prices (open, high, low, close <= 0).
    2. Enforce impossible OHLC relations (high >= low, high >= open, high >= close, low <= open, low <= close).
    3. Ensure valid date formats and remove duplicate observation dates.
    """
    if df.empty:
        return pd.DataFrame()

    cleaned = df.copy()

    # Flatten multi-level columns if produced by yfinance
    if isinstance(cleaned.columns, pd.MultiIndex):
        cleaned.columns = cleaned.columns.get_level_values(0)

    # Standardize column naming
    column_mapping = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
    }
    cleaned = cleaned.rename(columns=column_mapping)

    # Fall back for adj_close if not present
    if "adj_close" not in cleaned.columns and "close" in cleaned.columns:
        cleaned["adj_close"] = cleaned["close"]

    required_cols = ["open", "high", "low", "close", "adj_close", "volume"]
    for col in required_cols:
        if col not in cleaned.columns:
            logger.warning(f"Missing required column '{col}' in yfinance response.")
            return pd.DataFrame()

    # Reset index if Date is index
    if "Date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["Date"]).dt.date
    elif isinstance(cleaned.index, pd.DatetimeIndex):
        cleaned["date"] = cleaned.index.date
    else:
        cleaned["date"] = pd.to_datetime(cleaned.index).dt.date

    # Drop NaNs
    cleaned = cleaned.dropna(subset=required_cols + ["date"])

    # Convert numeric columns
    for col in ["open", "high", "low", "close", "adj_close"]:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
    cleaned["volume"] = pd.to_numeric(cleaned["volume"], errors="coerce").fillna(0).astype(int)

    # Quality Gate 1: Non-positive price filtering
    valid_prices_mask = (
        (cleaned["open"] > 0)
        & (cleaned["high"] > 0)
        & (cleaned["low"] > 0)
        & (cleaned["close"] > 0)
        & (cleaned["adj_close"] > 0)
    )
    cleaned = cleaned[valid_prices_mask]

    # Quality Gate 2: OHLC logic rules
    ohlc_valid_mask = (
        (cleaned["high"] >= cleaned["low"])
        & (cleaned["high"] >= cleaned["open"])
        & (cleaned["high"] >= cleaned["close"])
        & (cleaned["low"] <= cleaned["open"])
        & (cleaned["low"] <= cleaned["close"])
    )
    cleaned = cleaned[ohlc_valid_mask]

    # Deduplicate by date keeping the last observation
    cleaned = cleaned.drop_duplicates(subset=["date"], keep="last")

    return cleaned[required_cols + ["date"]]


async def fetch_and_store_historical_prices(
    db: AsyncSession, ticker: str, period: str = "5y"
) -> Tuple[int, bool]:
    """Download prices via yfinance, validate quality, and upsert into historical_prices table."""
    result = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = result.scalar_one_or_none()
    if not asset:
        logger.error(f"Asset with ticker {ticker} not found in database.")
        return 0, False

    try:
        ticker_obj = yf.Ticker(ticker)
        raw_df = ticker_obj.history(period=period, auto_adjust=False)
    except Exception as e:
        logger.error(f"Failed to fetch data for ticker {ticker}: {e}")
        return 0, False

    cleaned_df = validate_and_clean_prices(raw_df)
    if cleaned_df.empty:
        logger.warning(f"No valid price records remaining after quality check for {ticker}.")
        return 0, True

    records = []
    for _, row in cleaned_df.iterrows():
        records.append(
            {
                "asset_id": asset.id,
                "date": row["date"],
                "open": round(float(row["open"]), 4),
                "high": round(float(row["high"]), 4),
                "low": round(float(row["low"]), 4),
                "close": round(float(row["close"]), 4),
                "adj_close": round(float(row["adj_close"]), 4),
                "volume": int(row["volume"]),
            }
        )

    if not records:
        return 0, True

    # Bulk upsert logic compatible with PostgreSQL
    inserted_count = 0
    if db.bind and db.bind.dialect.name == "postgresql":
        stmt = pg_insert(HistoricalPrice).values(records)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_historical_prices_asset_date",
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "adj_close": stmt.excluded.adj_close,
                "volume": stmt.excluded.volume,
            },
        )
        res = await db.execute(stmt)
        inserted_count = len(records)
    else:
        # Fallback for SQLite / generic drivers
        for rec in records:
            res = await db.execute(
                select(HistoricalPrice).where(
                    HistoricalPrice.asset_id == rec["asset_id"],
                    HistoricalPrice.date == rec["date"],
                )
            )
            existing_price = res.scalar_one_or_none()
            if existing_price:
                for k, v in rec.items():
                    setattr(existing_price, k, v)
            else:
                db.add(HistoricalPrice(**rec))
            inserted_count += 1

    await db.commit()
    return inserted_count, True


async def get_market_status(db: AsyncSession) -> List[Dict]:
    """Retrieve market data ingestion status across all registered assets."""
    assets_res = await db.execute(select(Asset).order_by(Asset.ticker))
    assets = assets_res.scalars().all()

    today = date.today()
    status_list = []

    for asset in assets:
        stats_res = await db.execute(
            select(
                func.count(HistoricalPrice.id),
                func.min(HistoricalPrice.date),
                func.max(HistoricalPrice.date),
            ).where(HistoricalPrice.asset_id == asset.id)
        )
        total_records, earliest_date, latest_date = stats_res.one()

        # Stale if no price in the last 4 days (account for weekends/holidays)
        is_stale = (
            latest_date is None or (today - latest_date).days > 4
        )

        status_list.append(
            {
                "ticker": asset.ticker,
                "name": asset.name,
                "asset_class": asset.asset_class,
                "total_records": total_records or 0,
                "earliest_date": earliest_date,
                "latest_date": latest_date,
                "is_stale": is_stale,
            }
        )

    return status_list
