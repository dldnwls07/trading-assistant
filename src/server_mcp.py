import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

# 기존 프로젝트 모듈 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agents.core.analyst import StockAnalyst
from src.data.collector import MarketDataCollector
from src.agents.analysis.ai_analyzer import AIAnalyzer
from src.agents.analysis.portfolio_analyzer import PortfolioAnalyzer
from src.agents.analysis.screener import StockScreener
from src.agents.event_calendar_api.event_calendar import EventCalendar
from src.data.storage import get_storage

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trading-api")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Trading Assistant API",
    description="Provides stock analysis, historical data, and market insights.",
    version="1.0.0"
)

# --- Security ---
API_KEY = os.environ.get("API_KEY", "trading-assistant-secret-2024")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Service Instances (Singletons) ---
collector = MarketDataCollector()
analyst = StockAnalyst()
ai_analyzer = AIAnalyzer()
portfolio = PortfolioAnalyzer()
screener = StockScreener()
calendar = EventCalendar()
storage = get_storage()


# ---------------------------------------------------------
# 🚀 API Endpoints
# ---------------------------------------------------------

@app.get("/search", dependencies=[Depends(get_api_key)])
async def search_ticker(query: str):
    """
    Search for stock tickers.
    """
    try:
        # This is a simplified search. In a real app, you'd use a search index.
        results = collector.search_symbols(query)
        return {"candidates": results}
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Search failed.")

@app.get("/analyze/{ticker}", dependencies=[Depends(get_api_key)])
async def get_analysis(ticker: str, lang: str = "en"):
    """
    Get a comprehensive analysis for a given stock ticker.
    """
    try:
        df = await collector.get_ohlcv(ticker, period="1y", interval="1d")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Data not found for ticker '{ticker}'. Check the symbol.")
        
        financials = collector.get_financials(ticker)
        result = analyst.analyze_ticker(ticker, df, financials=financials)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Analysis failed for ticker '{ticker}': {e}")
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal server error.")


@app.get("/history/{ticker}", dependencies=[Depends(get_api_key)])
async def get_history(ticker: str, interval: str = "1d"):
    """
    Get historical OHLCV data for a given stock ticker.
    """
    try:
        # Validate interval
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo', '1y']
        if interval not in valid_intervals:
            raise HTTPException(status_code=400, detail=f"Invalid interval. Use one of {valid_intervals}")

        df = await collector.get_ohlcv(ticker, interval=interval, period="max")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for ticker '{ticker}' with interval '{interval}'.")
        
        import pandas as pd
        # Convert DataFrame to list of dicts for JSON response
        df_reset = df.reset_index()
        # Ensure the date column is datetime and convert timestamp to string
        if 'Date' in df_reset.columns:
            df_reset['Date'] = pd.to_datetime(df_reset['Date']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        elif 'index' in df_reset.columns:
            df_reset['index'] = pd.to_datetime(df_reset['index']).dt.strftime('%Y-%m-%dT%H:%M:%S')

        records = df_reset.to_dict('records')
        
        return {"data": records}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"History retrieval failed for ticker '{ticker}': {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve historical data.")


# ---------------------------------------------------------
# 🚀 서버 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    # Use uvicorn to run the FastAPI app
    # Host '0.0.0.0' makes it accessible on the network
    # Port 8000 is the default for many web development setups
    uvicorn.run(app, host="0.0.0.0", port=8001)
