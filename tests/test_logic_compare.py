
import pandas as pd
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.getcwd())

from src.agents.analyst import StockAnalyst
from src.agents.multi_timeframe import MultiTimeframeAnalyzer
from src.data.collector import MarketDataCollector

def test_integration_logic():
    ticker = "AAPL"
    collector = MarketDataCollector(use_db=False)
    analyst = StockAnalyst()
    multi = MultiTimeframeAnalyzer()
    
    print(f"--- [Testing Core Logic for {ticker}] ---")
    
    # 1. Fetch Data
    daily_df = collector.get_ohlcv(ticker, period="1y", interval="1d")
    hourly_df = collector.get_ohlcv(ticker, period="60d", interval="60m")
    
    if daily_df is None or daily_df.empty:
        print("Data fetch failed. Ensure internet connection.")
        return

    # 2. Check traditional analyst (What server.py currently uses)
    print("\n--- [1. StockAnalyst Output (Current Server Logic)] ---")
    analysis_result = analyst.analyze_ticker(ticker, daily_df, financials=None, hourly_df=hourly_df)
    print(f"Keys in result: {list(analysis_result.keys())}")
    
    # Check if short/mid/long exists in StockAnalyst output
    has_tf = any(k in str(analysis_result.keys()).lower() for k in ["short", "medium", "long"])
    print(f"Detected Multi-Timeframe Keys? : {has_tf}")

    # 3. Check MultiTimeframeAnalyzer (What we should use)
    print("\n--- [2. MultiTimeframeAnalyzer Output (The Missing Part)] ---")
    multi_result = multi.analyze_all_timeframes(ticker)
    print(f"Keys in multi-result: {list(multi_result.keys())}")
    
    if "short_term" in multi_result:
        print("✅ MultiTimeframeAnalyzer HAS the short/med/long terms.")
    else:
        print("❌ MultiTimeframeAnalyzer is missing keys.")

if __name__ == "__main__":
    test_integration_logic()
