import asyncio
import logging
import sys
import os
import json

# Add current path to sys.path so src module can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import settings
from src.services.integration_service import get_integration_service
from src.api.utils import get_final_ticker

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_integration():
    ticker = "ORCL"
    final_ticker = get_final_ticker(ticker)
    logger.info(f"Testing integration service for {ticker} -> {final_ticker}")
    
    integration_service = get_integration_service()
    
    try:
        result = await integration_service.run_comprehensive_analysis(final_ticker)
        logger.info(f"Result Status: {result.get('status')}")
        if result.get('status') == 'error':
            logger.error(f"Error Message: {result.get('message')}")
        else:
            logger.info("Keys in result: " + ", ".join(result.keys()))
    except Exception as e:
        logger.error(f"Test Failed with exception: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_integration())
