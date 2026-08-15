import pytest
import pandas as pd
from datetime import date, timedelta
from app.services.ingestion_service import validate_and_clean_prices


def test_validate_and_clean_prices_valid():
    dates = [date(2026, 1, 1), date(2026, 1, 2)]
    data = {
        "Open": [100.0, 102.0],
        "High": [105.0, 107.0],
        "Low": [98.0, 101.0],
        "Close": [104.0, 105.0],
        "Adj Close": [104.0, 105.0],
        "Volume": [10000, 15000],
    }
    df = pd.DataFrame(data, index=pd.DatetimeIndex(dates))

    cleaned = validate_and_clean_prices(df)
    assert len(cleaned) == 2
    assert list(cleaned.columns) == ["open", "high", "low", "close", "adj_close", "volume", "date"]
    assert cleaned.iloc[0]["close"] == 104.0


def test_validate_and_clean_prices_filters_invalid_prices():
    dates = [date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3)]
    data = {
        "Open": [100.0, -5.0, 102.0],  # Middle row has negative open
        "High": [105.0, 107.0, 107.0],
        "Low": [98.0, 101.0, 101.0],
        "Close": [104.0, 105.0, 0.0],   # Last row has 0 close
        "Adj Close": [104.0, 105.0, 105.0],
        "Volume": [10000, 15000, 12000],
    }
    df = pd.DataFrame(data, index=pd.DatetimeIndex(dates))

    cleaned = validate_and_clean_prices(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["date"] == date(2026, 1, 1)


def test_validate_and_clean_prices_filters_ohlc_violations():
    dates = [date(2026, 1, 1), date(2026, 1, 2)]
    data = {
        "Open": [100.0, 100.0],
        "High": [105.0, 95.0],  # Second row: High (95) < Open (100) -> invalid
        "Low": [98.0, 90.0],
        "Close": [104.0, 92.0],
        "Adj Close": [104.0, 92.0],
        "Volume": [10000, 15000],
    }
    df = pd.DataFrame(data, index=pd.DatetimeIndex(dates))

    cleaned = validate_and_clean_prices(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["date"] == date(2026, 1, 1)


def test_validate_and_clean_prices_deduplicates_dates():
    dates = [date(2026, 1, 1), date(2026, 1, 1)]  # Duplicate date
    data = {
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [98.0, 99.0],
        "Close": [104.0, 105.0],
        "Adj Close": [104.0, 105.0],
        "Volume": [10000, 15000],
    }
    df = pd.DataFrame(data, index=pd.DatetimeIndex(dates))

    cleaned = validate_and_clean_prices(df)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["close"] == 105.0  # Keeps last
