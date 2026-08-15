import asyncio
import logging
import sys

from app.db.session import SessionLocal
from app.services.ingestion_service import (
    DEFAULT_UNIVERSE,
    fetch_and_store_historical_prices,
    seed_default_assets,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_seeder(period: str = "5y"):
    logger.info("Initializing market data seeder...")

    async with SessionLocal() as db:
        logger.info("Seeding default asset universe...")
        assets = await seed_default_assets(db)
        logger.info(f"Successfully registered {len(assets)} assets.")

        total_inserted = 0
        failed_tickers = []

        for asset in assets:
            logger.info(f"Ingesting daily historical prices for {asset.ticker} (period: {period})...")
            count, success = await fetch_and_store_historical_prices(
                db, ticker=asset.ticker, period=period
            )
            if success:
                total_inserted += count
                logger.info(f"[{asset.ticker}] Ingested/updated {count} historical price records.")
            else:
                failed_tickers.append(asset.ticker)
                logger.error(f"[{asset.ticker}] Failed to ingest historical price records.")

        logger.info("=" * 60)
        logger.info(f"Seeding completed. Total records processed: {total_inserted}")
        if failed_tickers:
            logger.warning(f"Failed tickers: {', '.join(failed_tickers)}")
        else:
            logger.info("All universe tickers ingested successfully!")


if __name__ == "__main__":
    period = sys.argv[1] if len(sys.argv) > 1 else "5y"
    asyncio.run(run_seeder(period=period))
