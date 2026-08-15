from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class AssetResponse(BaseModel):
    id: int
    ticker: str
    name: str
    asset_class: str

    model_config = {"from_attributes": True}


class HistoricalPriceResponse(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

    model_config = {"from_attributes": True}


class MarketStatusResponse(BaseModel):
    ticker: str
    name: str
    asset_class: str
    total_records: int
    earliest_date: Optional[date] = None
    latest_date: Optional[date] = None
    is_stale: bool


class IngestionRequest(BaseModel):
    tickers: Optional[List[str]] = Field(
        default=None,
        description="List of tickers to ingest. If empty, ingests all default universe tickers.",
    )
    period: str = Field(
        default="5y",
        description="yfinance period format (e.g. '1y', '5y', 'max')",
    )


class IngestionResponse(BaseModel):
    status: str
    processed_assets: int
    inserted_records: int
    failed_assets: List[str] = []
