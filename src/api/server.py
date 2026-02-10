from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any
import logging
import pandas as pd
import json
import os
from datetime import datetime

# 프로젝트 모듈
from src.data.collector import MarketDataCollector
from src.data.storage import get_storage
from src.data.parser import FinancialParser
from src.agents.analyst import StockAnalyst
from src.agents.ai_analyzer import AIAnalyzer, get_stock_events
from src.agents.chat_assistant import ChatAssistant
from src.agents.event_calendar import EventCalendar
from src.agents.portfolio_analyzer import PortfolioAnalyzer
from src.agents.screener import StockScreener

# 로깅
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Assistant API v2.0",
    description="AI-Powered Trading Analysis Server - Web, Mobile, Extension Ready",
    version="2.0.0"
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

# 신규 기능 인스턴스
chat_assistant = ChatAssistant(gemini_api_key=os.getenv("GEMINI_API_KEY"))
event_calendar = EventCalendar()
portfolio_analyzer = PortfolioAnalyzer()
screener = StockScreener()

# === 모델 정의 ===
class AnalysisRequest(BaseModel):
    ticker: str

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

def get_final_ticker(ticker: str) -> str:
    """종목명이나 숫자를 yfinance 티커(symbol)로 변환"""
    import yfinance as yf
    
    # 1. 이미 규격에 맞는 티커인 경우 바로 반환
    if ticker.endswith(('.KS', '.KQ')) or (ticker.isupper() and len(ticker) <= 5):
        return ticker

    # 2. 숫자로만 된 6자리 코드라면 .KS 자동 부여
    if ticker.isdigit() and len(ticker) == 6:
        return f"{ticker}.KS"

    # 3. 하드 매핑 체크
    korean_map = {
        "삼성전자": "005930.KS", "삼성전자우": "005935.KS",
        "sk하이닉스": "000660.KS", "하이닉스": "000660.KS",
        "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
        "카카오": "035720.KS", "네이버": "035420.KS",
        "현대차": "005380.KS", "기아": "000270.KS",
        "셀트리온": "068270.KS", "포스코홀딩스": "005490.KS",
        "lg에너지솔루션": "373220.KS", "삼성sdi": "006400.KS"
    }
    if ticker in korean_map:
        return korean_map[ticker]

    # 4. 검색 API 시도
    try:
        is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in ticker)
        search = yf.Search(ticker, max_results=5)
        quotes = search.quotes
        if quotes:
            if is_korean:
                for res in quotes:
                    sym = res.get('symbol', '')
                    if sym.endswith(('.KS', '.KQ')):
                        return sym
            return quotes[0].get('symbol', ticker)
    except Exception as e:
        logger.error(f"Ticker mapping error for {ticker}: {e}")
    
    return ticker

async def run_analysis(ticker: str):
    """실제 분석 로직 공통 엔진"""
    # 1. 티커 매핑
    final_ticker = get_final_ticker(ticker)
    logger.info(f"Analyzing mapped ticker: {final_ticker} (Input: {ticker})")
    
    # 종목명 가져오기 (yf.Ticker 사용)
    import yfinance as yf
    display_name = final_ticker
    try:
        stock = yf.Ticker(final_ticker)
        info = stock.info
        name = info.get('longName') or info.get('shortName') or final_ticker
        display_name = f"{name} ({final_ticker})"
    except:
        pass

    # 2. 데이터 수집
    daily_df = collector.get_ohlcv(final_ticker, period="1y", interval="1d")
    hourly_df = collector.get_ohlcv(final_ticker, period="60d", interval="60m")
    
    if daily_df is None or daily_df.empty:
        raise HTTPException(status_code=404, detail=f"[{final_ticker}] 데이터를 찾을 수 없습니다.")
        
    # 3. 재무 데이터 수집
    financials = storage.get_financials(final_ticker)
    if not financials:
        parser.fetch_and_save_financials(final_ticker)
        financials = storage.get_financials(final_ticker)
        
    # 4. 종합 스마트 분석 실행
    analysis_result = analyst.analyze_ticker(final_ticker, daily_df, financials, hourly_df)
    analysis_result['display_name'] = display_name
    
    # 5. 이벤트 정보 추가
    events = get_stock_events(final_ticker)
    analysis_result['events'] = events
    
    return safe_serialize(analysis_result)

@app.post("/analyze")
async def analyze_post(req: AnalysisRequest):
    """POST 방식 분석 엔드포인트"""
    try:
        return await run_analysis(req.ticker)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{ticker}")
async def analyze_get(ticker: str):
    """GET 방식 분석 엔드포인트 (기존 호환성)"""
    try:
        return await run_analysis(ticker)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{ticker}")
async def get_history(ticker: str, interval: str = "1d"):
    """
    차트 시각화를 위한 OHLCV 데이터 반환
    """
    try:
        # 티커 매핑 수행 (한글명 -> 티커)
        final_ticker = get_final_ticker(ticker)
        
        # 인터벌에 따른 적절한 데이터 기간(period) 설정
        period_map = {
            "1m": "1d",
            "5m": "5d",
            "15m": "7d",
            "30m": "30d",
            "60m": "60d",
            "1h": "60d",
            "4h": "120d", # yfinance는 4h를 직접 지원하지 않으므로 1h를 가져가나 기간을 늘림
            "1d": "2y",
            "1wk": "max",
            "1mo": "max",
            "1y": "max"  # 1y 캔들은 없으므로 1mo 사용 후 프론트에서 처리
        }
        period = period_map.get(interval, "1y")
        
        # 4h 요청 시 yfinance 대응을 위해 1h로 변경 (데이터는 충분히 가져옴)
        actual_interval = "1h" if interval == "4h" else ("1mo" if interval == "1y" else interval)
        
        # 소문자 접미사 대문자로 정규화
        if final_ticker.endswith('.ks'): final_ticker = final_ticker[:-3] + '.KS'
        if final_ticker.endswith('.kq'): final_ticker = final_ticker[:-3] + '.KQ'

        df = collector.get_ohlcv(final_ticker, period=period, interval=actual_interval)
        
        # 데이터가 없는 경우 상위 인터벌로 대체 시도
        if (df is None or df.empty) and interval in ["1m", "5m", "15m", "30m", "60m"]:
            logger.info(f"Interval {interval} failed for {ticker}, falling back to daily.")
            df = collector.get_ohlcv(final_ticker, period="1y", interval="1d")
            interval = "1d"

        if df is None or df.empty:
            return {"ticker": final_ticker, "data": []}
            
        # 기술적 지표 계산 (TechnicalAnalyzer 활용)
        from src.agents.analyst import TechnicalAnalyzer
        ta = TechnicalAnalyzer()
        
        # 지표 추가를 위한 데이터프레임 복사 및 연산
        calc_df = df.copy()
        if 'Date' in calc_df.columns:
            calc_df.set_index(pd.to_datetime(calc_df['Date']), inplace=True)
        
        # 이동평균선
        calc_df['sma20'] = calc_df['Close'].rolling(window=20).mean()
        calc_df['sma50'] = calc_df['Close'].rolling(window=50).mean()
        calc_df['sma200'] = calc_df['Close'].rolling(window=200).mean()
        
        # RSI
        calc_df['rsi'] = ta.calculate_rsi(calc_df)
        
        # MACD
        macd_df = ta.calculate_macd(calc_df)
        calc_df = calc_df.join(macd_df)
        
        # 볼린저 밴드
        bb_df = ta.calculate_bollinger(calc_df)
        calc_df = calc_df.join(bb_df)

        # 인덱스를 Datetime으로 확실히 변환 (정렬 및 시간 추출을 위해)
        if not isinstance(calc_df.index, pd.DatetimeIndex):
            calc_df.index = pd.to_datetime(calc_df.index)
        
        # NaT 인덱스 제거
        calc_df = calc_df[calc_df.index.notnull()]
        
        # JSON 직렬화를 위해 오름차순 정렬 보장
        calc_df.sort_index(inplace=True)
        
        history = []
        for idx, row in calc_df.iterrows():
            # 인덱스가 날짜이므로 직접 변환
            try:
                time_val = idx.strftime('%Y-%m-%d %H:%M:%S' if actual_interval != '1d' else '%Y-%m-%d')
            except:
                time_val = str(idx)

            history.append({
                "time": time_val,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
                # 지표 데이터 추가 (NaN 처리 포함)
                "sma20": float(row["sma20"]) if not pd.isna(row["sma20"]) else None,
                "sma50": float(row["sma50"]) if not pd.isna(row["sma50"]) else None,
                "sma200": float(row["sma200"]) if not pd.isna(row["sma200"]) else None,
                "rsi": float(row["rsi"]) if not pd.isna(row["rsi"]) else None,
                "macd": float(row["MACD"]) if not pd.isna(row["MACD"]) else None,
                "macd_signal": float(row["Signal"]) if not pd.isna(row["Signal"]) else None,
                "macd_hist": float(row["Hist"]) if not pd.isna(row["Hist"]) else None,
                "bb_upper": float(row["BB_Upper"]) if not pd.isna(row["BB_Upper"]) else None,
                "bb_lower": float(row["BB_Lower"]) if not pd.isna(row["BB_Lower"]) else None,
            })
            
        return {"ticker": final_ticker, "interval": interval, "data": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        return {"ticker": ticker, "data": [], "error": str(e)}

@app.get("/search")
async def search_ticker(query: str):
    """
    티커 검색 (Autocomplete용)
    """
    try:
        import yfinance as yf
        if not query or len(query) < 1:
            return {"query": query, "candidates": []}
            
        search = yf.Search(query, max_results=8)
        results = search.quotes
        
        candidates = []
        for res in results:
            sym = res.get("symbol", "")
            is_kr = sym.endswith((".KS", ".KQ"))
            candidates.append({
                "symbol": sym,
                "name": res.get("shortname") or res.get("longname") or sym,
                "exchange": res.get("exchange"),
                "is_korean": is_kr
            })
            
        # 한국어 검색어라면 한국 주식을 우선순위로 정렬
        is_korean_query = any(ord('가') <= ord(char) <= ord('힣') for char in query)
        if is_korean_query:
            candidates.sort(key=lambda x: x['is_korean'], reverse=True)
            
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

# ============================================
# 신규 API 엔드포인트 (v2.0)
# ============================================

# === AI 채팅 ===
class ChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    AI 채팅 (Gemini Flash)
    """
    try:
        response = chat_assistant.chat(req.message, req.context)
        return {
            "message": req.message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/suggestions")
async def chat_suggestions(ticker: Optional[str] = None):
    """
    추천 질문 생성
    """
    try:
        context = {"ticker": ticker} if ticker else None
        suggestions = chat_assistant.suggest_questions(context)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return {"suggestions": []}

@app.delete("/api/chat/history")
async def clear_chat_history():
    """
    채팅 히스토리 초기화
    """
    try:
        chat_assistant.clear_history()
        return {"status": "ok", "message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 경제 캘린더 ===
@app.get("/api/calendar")
async def get_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tickers: Optional[str] = None
):
    """
    경제 이벤트 캘린더
    """
    try:
        from datetime import datetime, timedelta
        
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        ticker_list = None
        if tickers:
            ticker_list = [t.strip().upper() for t in tickers.split(",")]
        
        calendar_data = event_calendar.get_calendar(
            start_date=start_date,
            end_date=end_date,
            tickers=ticker_list
        )
        
        return safe_serialize(calendar_data)
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 포트폴리오 분석 ===
class PortfolioRequest(BaseModel):
    holdings: List[Dict[str, Any]]  # [{"ticker": "AAPL", "shares": 10, "avg_price": 150}]

@app.post("/api/portfolio/analyze")
async def analyze_portfolio(req: PortfolioRequest):
    """
    포트폴리오 AI 분석
    """
    try:
        result = portfolio_analyzer.analyze_portfolio(req.holdings)
        return safe_serialize(result)
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === AI 추천 종목 ===
@app.get("/api/screener/recommendations")
async def get_recommendations(
    style: Optional[str] = "balanced",
    market: Optional[str] = "US",
    limit: int = 10
):
    """
    AI 추천 종목 스크리닝
    """
    try:
        recommendations = screener.get_recommendations(
            style=style,
            market=market,
            limit=limit
        )
        return safe_serialize(recommendations)
    except Exception as e:
        logger.error(f"Screener error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screener/top-movers")
async def get_top_movers(market: str = "US"):
    """
    급등/급락 종목
    """
    try:
        movers = screener.get_top_movers(market=market)
        return safe_serialize(movers)
    except Exception as e:
        logger.error(f"Top movers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 다중 시간 프레임 분석 ===
@app.get("/api/multi-timeframe/{ticker}")
async def multi_timeframe_analysis(ticker: str):
    """
    다중 시간 프레임 종합 분석
    """
    try:
        final_ticker = get_final_ticker(ticker)
        
        # 여러 시간 프레임 데이터 수집
        timeframes = {
            "1h": collector.get_ohlcv(final_ticker, period="60d", interval="60m"),
            "4h": collector.get_ohlcv(final_ticker, period="120d", interval="1h"),
            "1d": collector.get_ohlcv(final_ticker, period="1y", interval="1d"),
            "1wk": collector.get_ohlcv(final_ticker, period="5y", interval="1wk"),
        }
        
        # 각 시간 프레임별 분석
        analyses = {}
        for interval, df in timeframes.items():
            if df is not None and not df.empty:
                # 간단한 기술적 분석
                from src.agents.analyst import TechnicalAnalyzer
                ta = TechnicalAnalyzer()
                
                analysis = {
                    "interval": interval,
                    "current_price": float(df['Close'].iloc[-1]),
                    "trend": "상승" if df['Close'].iloc[-1] > df['Close'].iloc[-20] else "하락",
                    "rsi": float(ta.calculate_rsi(df).iloc[-1]) if len(df) > 14 else None,
                }
                analyses[interval] = analysis
        
        return {
            "ticker": final_ticker,
            "timeframes": safe_serialize(analyses),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Multi-timeframe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 헬스 체크 ===
@app.get("/api/health")
async def health_check():
    """
    API 서버 상태 확인
    """
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "ai_chat": chat_assistant.use_ai,
            "calendar": True,
            "portfolio": True,
            "screener": True,
            "multi_timeframe": True
        },
        "timestamp": datetime.now().isoformat()
    }

# 실행용: uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
