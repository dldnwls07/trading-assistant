from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any
import logging
import pandas as pd
import json

# 프로젝트 모듈
from src.data.collector import MarketDataCollector
from src.data.storage import get_storage
from src.data.parser import FinancialParser
from src.agents.analyst import StockAnalyst
from src.agents.ai_analyzer import AIAnalyzer, get_stock_events

# 로깅
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Assistant API",
    description="Local Trading Analysis Server for Chrome Extension",
    version="1.0.0"
)

# CORS (크롬 확장 프로그램에서 접근 가능하도록 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (로컬 개발 편의성)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 전역 인스턴스 (싱글톤) ===
storage = get_storage()
collector = MarketDataCollector(use_db=True)
parser = FinancialParser(use_db=True)
analyst = StockAnalyst()
ai_analyzer = AIAnalyzer()

# === 모델 정의 ===
class AnalysisResponse(BaseModel):
    ticker: str
    interval: str
    signal: str
    final_score: float
    technical: Dict[str, Any]
    fundamental: Dict[str, Any]
    entry_points: Dict[str, Any]
    full_report: Optional[str] = None
    events: Dict[str, Any] = {}
    
    # Pydantic V2 설정 (임의의 타입 허용)
    model_config = ConfigDict(arbitrary_types_allowed=True)

# === API 엔드포인트 ===

@app.get("/")
async def root():
    return {"status": "ok", "message": "Trading Assistant Server is running"}

@app.get("/analyze/{ticker}")
async def analyze_ticker(ticker: str):
    """
    Smart Analysis 수행 (Daily + Hourly + AI)
    - 종목명(삼성전자) 입력 시 자동으로 티커(005930.KS) 매핑
    """
    try:
        # 1. 티커 매핑 (종목명 -> 티커)
        final_ticker = ticker
        import yfinance as yf
        
        # 한국어 포함 여부 체크
        is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in ticker)
        
        # [특별 조치] 자주 검색하는 한글 종목 하드 매핑 (yf.Search 실패 대비)
        korean_map = {
            "삼성전자": "005930.KS",
            "삼성전자우": "005935.KS",
            "sk하이닉스": "000660.KS",
            "하이닉스": "000660.KS",
            "에코프로": "086520.KQ",
            "에코프로비엠": "247540.KQ",
            "카카오": "035720.KS",
            "네이버": "035420.KS",
            "현대차": "005380.KS",
            "기아": "000270.KS"
        }
        
        if ticker in korean_map:
            final_ticker = korean_map[ticker]
            logger.info(f"Direct mapping hit: {ticker} -> {final_ticker}")
        else:
            try:
                search = yf.Search(ticker, max_results=8)
                quotes = search.quotes
                if quotes:
                    if is_korean:
                        for res in quotes:
                            sym = res.get('symbol', '')
                            if sym.endswith('.KS') or sym.endswith('.KQ'):
                                final_ticker = sym
                                logger.info(f"Searched Korean stock: {ticker} -> {final_ticker}")
                                break
                        else:
                            final_ticker = quotes[0].get('symbol', ticker)
                    else:
                        final_ticker = quotes[0].get('symbol', ticker)
            except Exception as e:
                logger.error(f"Ticker Search API failed: {e}")

        logger.info(f"Smart Analyzing {final_ticker} (Original: {ticker})...")
        
        # 2. 데이터 수집
        daily_df = collector.get_ohlcv(final_ticker, period="1y", interval="1d")
        hourly_df = collector.get_ohlcv(final_ticker, period="60d", interval="60m")
        
        if daily_df is None or daily_df.empty:
            logger.error(f"Data collection failed for final_ticker: {final_ticker}")
            raise HTTPException(status_code=404, detail=f"[{final_ticker}] 종목 데이터를 찾을 수 없습니다. 정확한 티커(예: AAPL, 005930.KS)를 입력해 보세요.")
            
        # 2. 재무 데이터 수집
        financials = storage.get_financials(ticker)
        if not financials:
            parser.fetch_and_save_financials(ticker)
            financials = storage.get_financials(ticker)
            
        # 3. 종합 스마트 분석 실행
        analysis_result = analyst.analyze_ticker(ticker, daily_df, financials, hourly_df)
        
        # 4. 이벤트 정보 추가
        events = get_stock_events(ticker)
        analysis_result['events'] = events
        
        # 5. 응답 구성 (JSON 직렬화)
        return safe_serialize(analysis_result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{ticker}")
async def get_history(ticker: str, interval: str = "1d"):
    """
    차트 시각화를 위한 OHLCV 데이터 반환
    """
    try:
        period = "1y" if interval == "1d" else "60d"
        df = collector.get_ohlcv(ticker, period=period, interval=interval)
        
        if df is None or df.empty:
            return {"ticker": ticker, "data": []}
            
        # Lightweight Charts 포맷 {time, open, high, low, close}
        history = []
        df = df.sort_index() # 시간 순서 보장
        
        for idx, row in df.iterrows():
            # 타임스탬프 처리 (날짜 형식 보장)
            try:
                if hasattr(idx, 'strftime'):
                    time_val = idx.strftime("%Y-%m-%d")
                elif isinstance(idx, (int, float, str)) and interval == "1d":
                    # 인덱스가 숫자인 경우 (DB 유실 등), 실제 날짜 컬럼이 있는지 확인
                    if 'Date' in row:
                        date_obj = pd.to_datetime(row['Date'])
                        time_val = date_obj.strftime("%Y-%m-%d")
                    else:
                        # 최후의 수단: 인덱스로부터 날짜 유추 (오늘부터 역산)
                        from datetime import datetime, timedelta
                        time_val = (datetime.now() - timedelta(days=len(df)-1-int(idx))).strftime("%Y-%m-%d")
                else:
                    time_val = int(idx.timestamp()) if hasattr(idx, 'timestamp') else int(time.time())
            except:
                time_val = str(idx)

            history.append({
                "time": time_val,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"])
            })
            
        return {"ticker": ticker, "interval": interval, "data": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        return {"ticker": ticker, "data": [], "error": str(e)}

@app.get("/search")
async def search_ticker(query: str):
    """
    티커 검색 (종목명 -> 티커 변환)
    """
    try:
        import yfinance as yf
        search = yf.Search(query, max_results=5)
        results = search.quotes
        
        candidates = []
        for res in results:
            candidates.append({
                "symbol": res.get("symbol"),
                "shortname": res.get("shortname"),
                "longname": res.get("longname"),
                "exchange": res.get("exchange"),
                "type": res.get("quoteType")
            })
            
        return {"query": query, "candidates": candidates}
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"query": query, "candidates": []}

def safe_serialize(data):
    """JSON 직렬화 불가능한 객체(NaN, Timestamp 등) 처리"""
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_serialize(v) for v in data]
    elif isinstance(data, (pd.Timestamp, pd.Period)):
        return str(data)
    elif pd.isna(data):  # NaN -> None
        return None
    elif isinstance(data, (pd.Series, pd.DataFrame)):
        return data.to_dict()
    else:
        return data

# 실행용: uvicorn src.api.server:app --reload
