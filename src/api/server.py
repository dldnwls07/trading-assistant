from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
from src.utils.serializer import safe_serialize

# 로깅
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trading Assistant API v2.0",
    description="AI-Powered Trading Analysis Server - Web, Mobile, Extension Ready",
    version="2.0.0"
)

# CORS (Production Security - No Wildcards)
origins = [
    "http://localhost:5173",  # Vite Dev Server
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "chrome-extension://*",   # Extension Support (Restrict ID in prod)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], # Limit Methods
    allow_headers=["Content-Type", "Authorization"], # Limit Headers
)

# === Rate Limiting (DoS Protection) ===
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# === Input Validation ===
import re
def validate_ticker(ticker: str):
    """Sanitize and validate ticker input"""
    if not ticker or len(ticker) > 20:
        raise HTTPException(status_code=400, detail="Invalid ticker length")
    # Alphanumeric + . for KRX tickers + ^ for indices + = for currencies
    if not re.match(r"^[A-Za-z0-9\.\^\=]+$", ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    return ticker.upper()

# === Global Exception Handler ===
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc} Path: {request.url.path}")
    # Production: Hide details
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_id": datetime.now().timestamp()},
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

# 전역 데이터
class KRXLoader:
    def __init__(self):
        self.df = None
        self.loading = False
    
    def load(self):
        if self.loading or self.df is not None: return
        self.loading = True
        try:
            import FinanceDataReader as fdr
            logger.info("Loading KRX data...")
            self.df = fdr.StockListing('KRX')
            logger.info(f"Loaded {len(self.df)} KRX symbols.")
        except Exception as e:
            logger.error(f"Failed to load KRX data: {e}")
        finally:
            self.loading = False

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        if self.df is None: return []
        try:
            q = query.strip()
            # 이름 또는 코드로 검색
            mask = self.df['Name'].astype(str).str.contains(q, case=False, na=False) | \
                   self.df['Code'].astype(str).str.contains(q, case=False, na=False)
            results = self.df[mask].head(limit)
            
            candidates = []
            for _, row in results.iterrows():
                market = row['Market']
                code = str(row['Code'])
                
                # 접미사 결정
                suffix = ".KS" if market in ['KOSPI', 'KOSPI200'] else ".KQ"
                
                # 6자리 숫자인 경우에만 접미사 추가, 아니면 그대로 (ETF 등 확인 필요)
                # TIGER ETF 같은 경우도 6자리 숫자 코드를 가짐
                symbol = f"{code}{suffix}" if code.isdigit() and len(code) == 6 else code
                
                candidates.append({
                    "symbol": symbol,
                    "name": row['Name'],
                    "exchange": market,
                    "is_korean": True
                })
            return candidates
        except Exception as e:
            logger.error(f"KRX Search error: {e}")
            return []

krx_loader = KRXLoader()
screener = StockScreener()

@app.on_event("startup")
async def startup_event():
    import asyncio
    global screener
    screener = StockScreener() # Ensure initialized
    asyncio.create_task(load_krx_bg())

async def load_krx_bg():
    if krx_loader:
        krx_loader.load()

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

from src.agents.multi_timeframe import MultiTimeframeAnalyzer
multi_analyzer = MultiTimeframeAnalyzer()

async def run_analysis(ticker: str, lang: str = "ko"):
    """실제 분석 로직 공통 엔진 (30+ 정밀 데이터 통합 버전)"""
    # 1. 티커 매핑
    final_ticker = get_final_ticker(ticker)
    logger.info(f"Analyzing mapped ticker: {final_ticker} (Input: {ticker})")
    
    # 종목 정보 가져오기
    import yfinance as yf
    display_name = final_ticker
    try:
        stock = yf.Ticker(final_ticker)
        info = stock.info
        name = info.get('longName') or info.get('shortName') or final_ticker
        display_name = f"{name} ({final_ticker})"
    except:
        pass

    # 2. 다중 시간 프레임 분석 (30+ 데이터 포인트 자동 생성)
    # 한국 주식은 KOSPI(^KS11), 미국 주식은 S&P 500(^GSPC) 기준
    index_symbol = "^KS11" if final_ticker.endswith(('.KS', '.KQ')) else "^GSPC"
    multi_res = multi_analyzer.analyze_all_timeframes(final_ticker, index_ticker=index_symbol)
    
    # 3. 추가 데이터 (재무, 이벤트)
    financials = storage.get_financials(final_ticker)
    if not financials:
        parser.fetch_and_save_financials(final_ticker)
        financials = storage.get_financials(final_ticker)
    events = get_stock_events(final_ticker)
    
    # 4. 종합 데이터 병합
    full_data = {
        **multi_res,
        "display_name": display_name,
        "fundamental": analyst.fund.analyze(financials) if financials else {"score": 50, "summary": "재무 정보 없음"},
        "events": events,
        "final_score": multi_res.get("consensus", {}).get("avg_score", 50),
        "signal": multi_res.get("consensus", {}).get("consensus", "중립")
    }

    # 5. AI 수석 분석가 리포트 생성 (30+ 데이터 기반 판단)
    full_data['full_report'] = ai_analyzer.generate_report(full_data, lang=lang)
    
    return safe_serialize(full_data)

@app.post("/analyze")
async def analyze_post(req: AnalysisRequest):
    """POST 방식 분석 엔드포인트"""
    try:
        # Validate Input
        validate_ticker(req.ticker)
        result = await run_analysis(req.ticker)
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis POST error: {e}")
        raise e  # Let global handler handle it

@app.get("/analyze/{ticker}")
async def analyze_get(ticker: str):
    """GET 방식 분석 엔드포인트 (기존 호환성)"""
    try:
        # Validate Input
        validate_ticker(ticker)
        result = await run_analysis(ticker)
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis GET error: {e}")
        raise e

@app.get("/history/{ticker}")
async def get_history(ticker: str, interval: str = "1d"):
    """
    차트 시각화를 위한 OHLCV 데이터 반환
    """
    try:
        # Validate Input
        validate_ticker(ticker)
        
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
            
        # === 전문가급 기술적 지표 계산 (30개 이상) ===
        from src.utils.advanced_indicators import AdvancedIndicators
        
        # 지표 추가를 위한 데이터프레임 복사
        calc_df = df.copy()
        if 'Date' in calc_df.columns:
            calc_df.set_index(pd.to_datetime(calc_df['Date']), inplace=True)
        
        # 모든 지표 한 번에 계산
        calc_df = AdvancedIndicators.calculate_all(calc_df)

        # 인덱스를 Datetime으로 확실히 변환
        if not isinstance(calc_df.index, pd.DatetimeIndex):
            calc_df.index = pd.to_datetime(calc_df.index)
        
        calc_df = calc_df[calc_df.index.notnull()]
        calc_df.sort_index(inplace=True)
        
        history = []
        for idx, row in calc_df.iterrows():
            try:
                time_val = idx.strftime('%Y-%m-%d %H:%M:%S' if actual_interval != '1d' else '%Y-%m-%d')
            except:
                time_val = str(idx)

            # 기본 OHLCV 데이터
            data_point = {
                "time": time_val,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
            }
            
            # === 모든 지표 추가 (NaN 안전 처리) ===
            all_indicators = [
                'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_60', 'sma_100', 'sma_120', 'sma_200',
                'ema_9', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width',
                'kc_upper', 'kc_middle', 'kc_lower',
                'dc_upper', 'dc_middle', 'dc_lower',
                'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
                'rsi', 'rsi_9', 'rsi_25',
                'MACD', 'Signal', 'Hist',
                'stoch_k', 'stoch_d',
                'cci', 'williams_r',
                'adx', 'plus_di', 'minus_di',
                'obv', 'mfi', 'vwap', 'cmf',
                'roc', 'momentum',
                'aroon_up', 'aroon_down', 'aroon_osc',
                'tsi', 'uo', 'atr'
            ]
            
            for indicator in all_indicators:
                if indicator in row.index:
                    val = row[indicator]
                    # MACD 계열은 소문자로 변환
                    key = indicator.lower() if indicator in ['MACD', 'Signal', 'Hist'] else indicator
                    if indicator == 'Signal':
                        key = 'macd_signal'
                    elif indicator == 'Hist':
                        key = 'macd_hist'
                    elif indicator == 'MACD':
                        key = 'macd'
                    data_point[key] = float(val) if not pd.isna(val) else None
            
            history.append(data_point)
            
        return safe_serialize({"ticker": final_ticker, "interval": interval, "data": history})
    except Exception as e:
        logger.error(f"History error: {e}")
        raise e

@app.get("/search")
async def search_ticker(query: str):
    """
    티커 검색 (Autocomplete용) - KRX 우선 + Yfinance 보조
    """
    try:
        import yfinance as yf
        if not query or len(query) < 1 or len(query) > 50: # Limit query length
            return {"query": query, "candidates": []}
            
        candidates = []
        
        # 1. 한국어 포함 시 KRX 로더 우선 사용
        is_korean_query = any(ord('가') <= ord(char) <= ord('힣') for char in query)
        is_krx_code = query.isdigit() and len(query) >= 3 # 숫자 코드 검색 시도
        
        if is_korean_query or is_krx_code or (krx_loader and krx_loader.df is not None):
            # KRX 로더가 준비되었으면 일단 검색 시도 (영어일 수도 있음 예: TIGER)
             if krx_loader and krx_loader.df is not None:
                krx_results = krx_loader.search(query, limit=10)
                candidates.extend(krx_results)
            
        # 2. yfinance 검색 (영어 쿼리일 때 혹은 KRX 결과가 적을 때)
        # 단, KRX 결과가 충분하면(>5) 스킵하여 속도 향상
        if len(candidates) < 3 and not is_korean_query:
            try:
                search = yf.Search(query, max_results=8)
                yf_results = search.quotes
                
                for res in yf_results:
                    sym = res.get("symbol", "")
                    
                    # 중복 제거 (이미 KRX에서 찾은 심볼이면 스킵)
                    if any(c['symbol'] == sym for c in candidates):
                        continue
                        
                    is_kr = sym.endswith((".KS", ".KQ"))
                    candidates.append({
                        "symbol": sym,
                        "name": res.get("shortname") or res.get("longname") or sym,
                        "exchange": res.get("exchange"),
                        "is_korean": is_kr
                    })
            except Exception as e:
                logger.warning(f"yfinance search error: {e}")
        
        # 한국 주식 우선 정렬
        candidates.sort(key=lambda x: x['is_korean'], reverse=True)
            
        return {"query": query, "candidates": candidates[:15]}
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"query": query, "candidates": []}

import numpy as np

def safe_serialize(data):
    """JSON 직렬화 불가능한 객체(NaN, Timestamp, Numpy 등) 처리"""
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_serialize(v) for v in data]
    elif isinstance(data, (pd.Timestamp, pd.Period)):
        return str(data)
    elif pd.isna(data):  # NaN, NaT -> None
        return None
    elif isinstance(data, (pd.Series, pd.DataFrame)):
        return data.where(pd.notnull(data), None).to_dict() # NaN 처리 포함
    elif isinstance(data, (np.integer, np.int64)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64)):
        return float(data) if not np.isnan(data) else None
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.bool_, bool)):
        return bool(data)
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
@limiter.limit("10/minute") # Prevent AI Abuse
async def chat(req: ChatRequest, request: Request):
    """
    AI 채팅 (Gemini Flash)
    """
    try:
        # Validate message length
        if len(req.message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long")
        
        # Validate ticker in context if present
        if req.ticker:
            validate_ticker(req.ticker)
            
        response = chat_assistant.chat(req.message, req.context)
        return safe_serialize({
            "message": req.message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise e

@app.get("/api/chat/suggestions")
async def chat_suggestions(ticker: Optional[str] = None):
    """
    추천 질문 생성
    """
    try:
        context = {"ticker": ticker} if ticker else None
        suggestions = chat_assistant.suggest_questions(context)
        return safe_serialize({"suggestions": suggestions})
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
    tickers: Optional[str] = None,
    lang: str = "ko"
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
            ticker_list = [validate_ticker(t.strip()) for t in tickers.split(",")]
        
        calendar_data = event_calendar.get_calendar(
            start_date=start_date,
            end_date=end_date,
            tickers=ticker_list,
            lang=lang
        )
        
        return safe_serialize(calendar_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        raise e

# === 포트폴리오 분석 ===
class PortfolioRequest(BaseModel):
    holdings: List[Dict[str, Any]]  # [{"ticker": "AAPL", "shares": 10, "avg_price": 150}]

@app.post("/api/portfolio/analyze")
@limiter.limit("20/minute")
async def analyze_portfolio(req: PortfolioRequest, request: Request):
    """
    포트폴리오 AI 분석
    """
    try:
        for holding in req.holdings:
            validate_ticker(holding.get("ticker", "AA"))
            
        result = portfolio_analyzer.analyze_portfolio(req.holdings)
        return safe_serialize(result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        raise e

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
        # Validate Ticker
        validate_ticker(ticker)
        
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
        
        return safe_serialize({
            "ticker": final_ticker,
            "timeframes": analyses,
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Multi-timeframe error: {e}")
        raise e



# === 헬스 체크 ===
# === 트레이딩 사전 ===
@app.get("/api/dictionary")
async def get_trading_dictionary(indicator_id: Optional[str] = None, view: str = "beginner"):
    """
    트레이딩 용어 및 지표 설명 (초보자/전문가 관점 분리)
    """
    from src.utils.dictionary import INDICATOR_DESCRIPTIONS, get_explanation
    
    if indicator_id:
        explanation = get_explanation(indicator_id, view)
        return {"id": indicator_id, "explanation": explanation}
    
    return INDICATOR_DESCRIPTIONS

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
            "multi_timeframe": True,
            "dictionary": True
        },
        "timestamp": datetime.now().isoformat()
    }

# 실행용: uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
