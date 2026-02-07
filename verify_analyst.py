import logging
import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from data.storage import DataStorage
from data.collector import MarketDataCollector
from agents.analyst import StockAnalyst

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_analysis():
    logger.info("Starting Analysis Verification...")
    
    ticker = "AAPL"
    storage = DataStorage("trading_assistant.db")
    collector = MarketDataCollector(use_db=True)
    
    # 1. Ensure we have data
    logger.info("Checking for data...")
    price_df = collector.get_daily_ohlcv(ticker, period="1y")
    financials = storage.get_financials(ticker)
    
    if price_df is None or len(price_df) < 50:
        logger.error("Insufficient price data!")
        return
        
    if not financials:
        logger.error("No financials found! (Run verify_parser.py first or ensure data is there)")
        # Attempt to parse if missing? 
        # For verification script, we assume previous steps passed, but fine.
        return

    logger.info(f"Data loaded. Price rows: {len(price_df)}, Financial records: {len(financials)}")
    
    # 2. Analyze
    analyst = StockAnalyst()
    result = analyst.analyze_ticker(ticker, price_df, financials)
    
    logger.info("-" * 30)
    logger.info(f"Ticker: {result['ticker']}")
    logger.info(f"Signal: {result['signal']}")
    logger.info(f"Score:  {result['final_score']}")
    logger.info("-" * 30)
    logger.info(f"Technical Summary: {result['technical'].get('summary')}")
    logger.info(f"Fundamental Summary: {result['fundamental'].get('summary')}")
    logger.info("-" * 30)

if __name__ == "__main__":
    verify_analysis()
