import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from .storage import DataStorage

# Setup logger

# Setup logger
logger = logging.getLogger(__name__)

class MarketDataCollector:
    """
    Collects market data using yfinance.
    Adheres to the "Advisory Only" principle by providing data for analysis, not execution.
    """
    
    def __init__(self, data_dir: str = "./data", use_db: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = DataStorage() if use_db else None
        
    def get_ohlcv(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetches OHLCV data for a given ticker with a specific interval.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            period: Data period (e.g., '1y', 'max', '5d')
            interval: Data interval (e.g., '1m', '5m', '1h', '1d', '1wk')
            
        Returns:
            DataFrame with OHLCV data or None if failed.
        """
        try:
            logger.info(f"Fetching {interval} data for {ticker} (Period: {period})...")
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data found for {ticker} with interval {interval}")
                return None
                
            # Clean data
            df.reset_index(inplace=True)
            if interval in ["1d", "1wk", "1mo"]:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            else:
                # 분/시간 데이터는 시간 정보가 중요함
                df['Date'] = pd.to_datetime(df['Date'])
            
            # Save to CSV for cache/inspection
            save_path = self.data_dir / f"{ticker}_{interval}.csv"
            df.to_csv(save_path, index=False)
            
            # Save to DB (Intraday 데이터는 DB 스키마 확장이 필요할 수 있으나 일단 저장 시도)
            if self.db and interval in ["1d", "1wk"]:
                self.db.save_price_history(ticker, df)
                
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_market_status(self) -> str:
        """
        Checks if the US market is open (simplified).
        """
        # TODO: Implement robust market status check using exchange calendars
        return "Unknown"

if __name__ == "__main__":
    # Test execution
    logging.basicConfig(level=logging.INFO)
    collector = MarketDataCollector()
    data = collector.get_daily_ohlcv("AAPL")
    if data is not None:
        print(data.head())
