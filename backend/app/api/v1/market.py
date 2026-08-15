from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.models.asset import Asset, HistoricalPrice
from app.schemas.market import (
    AssetResponse,
    HistoricalPriceResponse,
    IngestionRequest,
    IngestionResponse,
    MarketStatusResponse,
)
from app.services.ingestion_service import (
    DEFAULT_UNIVERSE,
    fetch_and_store_historical_prices,
    get_market_status,
    seed_default_assets,
)

router = APIRouter()


@router.get("/assets", response_model=List[AssetResponse])
async def list_assets(db: AsyncSession = Depends(get_db)):
    """List all registered assets and benchmarks."""
    result = await db.execute(select(Asset).order_by(Asset.ticker))
    assets = result.scalars().all()
    if not assets:
        # Auto-seed default assets if database table is empty
        assets = await seed_default_assets(db)
    return assets


@router.get("/prices/{ticker}", response_model=List[HistoricalPriceResponse])
async def get_asset_prices(
    ticker: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=5000, description="Max number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """Get historical daily price series for a specific asset ticker."""
    asset_res = await db.execute(select(Asset).where(Asset.ticker == ticker))
    asset = asset_res.scalar_one_or_none()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset ticker '{ticker}' not found.",
        )

    query = (
        select(HistoricalPrice)
        .where(HistoricalPrice.asset_id == asset.id)
        .order_by(HistoricalPrice.date.asc())
    )

    if start_date:
        query = query.where(HistoricalPrice.date >= start_date)
    if end_date:
        query = query.where(HistoricalPrice.date <= end_date)

    query = query.limit(limit)
    prices_res = await db.execute(query)
    prices = prices_res.scalars().all()

    return prices


@router.get("/status", response_model=List[MarketStatusResponse])
async def market_status(db: AsyncSession = Depends(get_db)):
    """Check dataset coverage, total price records, and staleness per asset."""
    return await get_market_status(db)


@router.post("/ingest", response_model=IngestionResponse)
async def trigger_ingestion(
    request: IngestionRequest = IngestionRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Trigger manual market data ingestion for default or specified tickers."""
    # Ensure default assets exist
    await seed_default_assets(db)

    target_tickers = (
        request.tickers
        if request.tickers
        else [item["ticker"] for item in DEFAULT_UNIVERSE]
    )

    processed = 0
    total_records = 0
    failed = []

    for ticker in target_tickers:
        count, success = await fetch_and_store_historical_prices(
            db, ticker=ticker, period=request.period
        )
        if success:
            processed += 1
            total_records += count
        else:
            failed.append(ticker)

    return IngestionResponse(
        status="completed" if not failed else "partial_success",
        processed_assets=processed,
        inserted_records=total_records,
        failed_assets=failed,
    )
