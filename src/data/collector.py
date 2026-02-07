import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict
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
        
    def get_smart_data(self, ticker: str) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Smart Analysis를 위한 멀티 타임프레임 데이터(일봉 + 1시간봉)를 한 번에 수집
        """
        results = {
            "daily": self.get_ohlcv(ticker, period="1y", interval="1d"),
            "hourly": self.get_ohlcv(ticker, period="60d", interval="60m")
        }
        return results

    def get_ohlcv(self, ticker: str, period: str = "1y", interval: str = "1d", retries: int = 3) -> Optional[pd.DataFrame]:
        """
        OHLCV 데이터를 수집하며, 실패 시 재시도 로직을 포함함.
        """
        for attempt in range(retries):
            try:
                logger.info(f"Fetching {interval} data for {ticker} (Attempt {attempt+1}/{retries})...")
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
                
                # [방어코드] yfinance 반환값 검증
                if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                    if attempt < retries - 1:
                        time.sleep(1)
                        continue
                    logger.warning(f"No data found for {ticker} with interval {interval}")
                    return None
                    
                # Clean data
                df.index.name = 'Date'
                df.reset_index(inplace=True)
                
                # 날짜 타입 변환
                if 'Date' in df.columns:
                    try:
                        if interval in ["1d", "1wk", "1mo"]:
                            df['Date'] = pd.to_datetime(df['Date']).dt.date
                        else:
                            df['Date'] = pd.to_datetime(df['Date'])
                    except Exception as e:
                        logger.warning(f"Date conversion failed: {e}")

                # Save to CSV
                save_path = self.data_dir / f"{ticker}_{interval}.csv"
                df.to_csv(save_path, index=False)
                
                # DB 저장 (에러 무시)
                try:
                    if self.db and interval in ["1d"]:
                        self.db.save_price_history(ticker, df)
                except:
                    pass
                    
                return df
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt+1}: {e}")
                if attempt < retries - 1:
                    import time
                    time.sleep(1)
                else:
                    return None
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
