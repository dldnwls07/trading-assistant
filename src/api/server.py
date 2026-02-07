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

@app.get("/analyze/{ticker}", response_model=AnalysisResponse)
async def analyze_ticker(
    ticker: str, 
    interval: str = Query("1d", description="Timeframe: 15m, 60m, 1d, 1wk")
):
    """
    주식 분석 수행 (기술적 + 기본적 + AI 리포트)
    """
    try:
        # 1. 타임프레임별 기간 자동 설정
        period_map = {
            "15m": "60d",
            "60m": "60d",
            "1d": "1y",
            "1wk": "max"
        }
        period = period_map.get(interval, "1y")
        
        logger.info(f"Analyzing {ticker} ({interval}, {period})...")
        
        # 2. 시세 데이터 수집
        price_df = collector.get_ohlcv(ticker, period=period, interval=interval)
        
        if price_df is None or len(price_df) < 5:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
            
        # 3. 재무 데이터 수집 (일봉 이상일 때만)
        financials = storage.get_financials(ticker)
        if not financials and interval in ["1d", "1wk"]:
            logger.info("Fetching financials...")
            parser.fetch_and_save_financials(ticker)
            financials = storage.get_financials(ticker)
            
        # 4. 종합 분석 실행
        analysis_result = analyst.analyze_ticker(ticker, price_df, financials)
        
        # 5. 이벤트 정보 추가
        events = get_stock_events(ticker)
        analysis_result['events'] = events
        
        # 6. AI 리포트 생성
        try:
            report = ai_analyzer.generate_report(analysis_result)
            analysis_result['full_report'] = report
        except Exception as e:
            logger.warning(f"AI Report failed: {e}")
            analysis_result['full_report'] = "AI 리포트 생성 실패"
            
        # 7. 응답 구성
        # Pydantic 모델에 맞게 데이터 변환
        return AnalysisResponse(
            ticker=analysis_result['ticker'],
            interval=interval,
            signal=analysis_result['signal'],
            final_score=float(analysis_result['final_score']),
            technical=safe_serialize(analysis_result['technical']),
            fundamental=safe_serialize(analysis_result['fundamental']),
            entry_points=safe_serialize(analysis_result['entry_points']),
            full_report=analysis_result.get('full_report'),
            events=safe_serialize(analysis_result.get('events', {}))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/{query}")
async def search_ticker(query: str):
    """
    티커 검색 (종목명 -> 티커 변환)
    """
    try:
        import yfinance as yf
        is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in query)
        
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
