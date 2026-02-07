import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from data.parser import FinancialParser
from data.storage import DataStorage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_parser():
    logger.info("Starting parser verification...")
    
    # Use the main DB for this test or a test one
    storage = DataStorage("trading_assistant.db")
    parser = FinancialParser(use_db=True)
    
    ticker = "AAPL"
    
    # 1. Fetch and Save
    logger.info(f"Fetching financials for {ticker}...")
    success = parser.fetch_and_save_financials(ticker)
    
    if not success:
        logger.error("Failed to fetch financials!")
        return
        
    # 2. Verify DB
    logger.info("Verifying DB content...")
    financials = storage.get_financials(ticker)
    
    if not financials:
        logger.error("No financials found in DB!")
        return
        
    logger.info(f"Found {len(financials)} financial records.")
    for f in financials[:3]:
        logger.info(f"Period: {f.period}, Rev: {f.revenue}, EPS: {f.eps}")
        
    logger.info("SUCCESS: Financials parsed and saved.")

if __name__ == "__main__":
    verify_parser()
