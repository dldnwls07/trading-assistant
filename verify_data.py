import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from data.collector import MarketDataCollector
from data.storage import DataStorage, Stock, PriceHistory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_system():
    logger.info("Starting verification...")
    
    # 1. Initialize DB
    logger.info("Initializing Storage...")
    storage = DataStorage("test_trading.db")
    
    # 2. Collect Data
    logger.info("Initializing Collector...")
    collector = MarketDataCollector(data_dir="./test_data", use_db=True)
    # Patch collector to use our test db
    collector.db = storage
    
    ticker = "AAPL"
    logger.info(f"Fetching data for {ticker}...")
    df = collector.get_daily_ohlcv(ticker, period="5d")
    
    if df is None or df.empty:
        logger.error("Failed to fetch data!")
        return
        
    logger.info(f"Fetched {len(df)} rows.")
    
    # 3. Verify DB Content
    session = storage.get_session()
    stock = session.query(Stock).filter_by(ticker=ticker).first()
    
    if stock:
        logger.info(f"Stock {stock.ticker} found in DB.")
    else:
        logger.error("Stock not found in DB!")
        
    prices = session.query(PriceHistory).filter_by(ticker=ticker).all()
    logger.info(f"Found {len(prices)} price records in DB.")
    
    if len(prices) == len(df):
        logger.info("SUCCESS: Data count matches.")
    else:
        logger.error(f"MISMATCH: DF has {len(df)} rows, DB has {len(prices)} records.")
        
    session.close()
    
    # Clean up (optional, maybe keep for inspection)
    # os.remove("test_trading.db")

if __name__ == "__main__":
    verify_system()
