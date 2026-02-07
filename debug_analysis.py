import sys
import os
import logging
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.data.collector import MarketDataCollector
from src.agents.analyst import StockAnalyst
from src.agents.ai_analyzer import AIAnalyzer
from src.data.storage import get_storage

# Setup logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_full_flow(ticker="AAPL"):
    logger.info(f"=== Starting Full Flow Test for {ticker} ===")
    
    try:
        # 1. Initialize Components
        logger.info("Initializing components...")
        storage = get_storage()
        collector = MarketDataCollector(use_db=True)
        analyst = StockAnalyst()
        ai = AIAnalyzer()
        
        # 2. Fetch Data (Daily + Hourly)
        logger.info(f"Step 1: Fetching Smart Data for {ticker}...")
        daily_df = collector.get_ohlcv(ticker, period="1y", interval="1d")
        hourly_df = collector.get_ohlcv(ticker, period="60d", interval="60m")
        
        if daily_df is None or daily_df.empty:
            logger.error("FAILED: Daily data is None or empty")
            return
        
        logger.info(f"SUCCESS: Daily data fetched ({len(daily_df)} rows)")
        if hourly_df is not None:
             logger.info(f"SUCCESS: Hourly data fetched ({len(hourly_df)} rows)")
        else:
             logger.warning("WARNING: Hourly data is None (optional but recommended)")

        # 3. Analyze Ticker
        logger.info("Step 2: Running Smart Analysis Engine...")
        financials = storage.get_financials(ticker)
        analysis_result = analyst.analyze_ticker(ticker, daily_df, financials, hourly_df)
        
        logger.info("SUCCESS: Analysis Result generated")
        logger.info(f" - Signal: {analysis_result.get('signal')}")
        logger.info(f" - Score: {analysis_result.get('final_score')}")
        logger.info(f" - Entry Points: {analysis_result.get('entry_points')}")

        # 4. Generate AI Report
        logger.info("Step 3: Generating AI Report...")
        report = ai.generate_report(analysis_result)
        
        if report and "리포트 생성 실패" not in report:
            logger.info("SUCCESS: AI Report generated")
            print("\n" + "="*50)
            print("AI REPORT PREVIEW:")
            print("="*50)
            print(report[:500] + "...")
            print("="*50)
        else:
            logger.error(f"FAILED: AI Report check failed. Report length: {len(report) if report else 0}")

        logger.info("=== Full Flow Test Completed Successfully ===")

    except Exception as e:
        logger.error(f"CRITICAL FAILURE during test: {e}", exc_info=True)

if __name__ == "__main__":
    test_ticker = "AAPL"
    if len(sys.argv) > 1:
        test_ticker = sys.argv[1]
    test_full_flow(test_ticker)
