import asyncio
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from src.agents.event_calendar_api.calendar_fetchers import (
    FredFetcher,
    TradingEconomicsScraper,
    FinnhubEarningsFetcher,
    NaverEarningsScraper,
)

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def test_fetchers():
    start = datetime.now()
    end = start + timedelta(days=30)
    
    logger.info("=== Testing FRED Fetcher ===")
    fred_key = os.getenv("FRED_API_KEY", "")
    logger.info(f"FRED_API_KEY Present: {bool(fred_key)}")
    fred_fetcher = FredFetcher(fred_key)
    try:
        fred_events = fred_fetcher.fetch(start, end)
        logger.info(f"FRED Result: {len(fred_events)} events found.")
    except Exception as e:
        logger.error(f"FRED Fetcher Failed: {e}", exc_info=True)

    logger.info("\n=== Testing Trading Economics Scraper ===")
    te_scraper = TradingEconomicsScraper()
    try:
        te_events = te_scraper.fetch(start, end)
        logger.info(f"TE Result: {len(te_events)} events found.")
    except Exception as e:
        logger.error(f"TE Scraper Failed: {e}", exc_info=True)

    logger.info("\n=== Testing Finnhub Earnings Fetcher ===")
    finnhub_key = os.getenv("FINNHUB_API_KEY", "").strip()
    logger.info(f"FINNHUB_API_KEY Present: {bool(finnhub_key)}")
    finnhub_fetcher = FinnhubEarningsFetcher(finnhub_key)
    try:
        finnhub_events = finnhub_fetcher.fetch(start, end)
        logger.info(f"Finnhub Result: {len(finnhub_events)} events found.")
    except Exception as e:
        logger.error(f"Finnhub Fetcher Failed: {e}", exc_info=True)

    logger.info("\n=== Testing Naver Earnings Scraper ===")
    naver_scraper = NaverEarningsScraper()
    try:
        naver_events = naver_scraper.fetch(start, end)
        logger.info(f"Naver Result: {len(naver_events)} events found.")
    except Exception as e:
        logger.error(f"Naver Scraper Failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_fetchers())
