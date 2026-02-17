from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List, Any
import logging
import pandas as pd
import json
import os
import asyncio
import traceback
from datetime import datetime
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from src.utils.notifications import send_alert, get_notifier

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
from src.agents.chartist import ChartMaster
from src.utils.serializer import safe_serialize

# 로깅
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager
from src.data.loader import krx_loader
import certifi

# === SSL Certificate Patch (Fix curl: 77 / certifi mismatch) ===
# certifi 경로가 잘못 잡히는 현상을 방지하기 위해 강제로 설정합니다.
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
logger.info(f"🛡️ SSL Certificate Path Patched: {certifi.where()}")

# === Lifespan Manager (Application Lifecycle) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("🚀 System Startup Initiated...")
    
    # 1. DB Initialization
    await storage.initialize()
    
    # 2. Background Data Loading (Non-blocking)
    # 별도 스레드에서 KRX 데이터 로딩 시작
    asyncio.create_task(load_krx_bg())
    
    # 3. System Alert (로그로 대체)
    logger.info("✅ Trading Assistant v2.0 서버가 준비되었습니다.")
    
    # 4. Background Workers (Alerts & AutoTrader)
    from src.api.alert_worker import check_alerts
    from src.agents.auto_trader import AutoTrader
    
    # 워커 루프 정의 (예외 처리 포함)
    async def alert_loop():
        logger.info("⏰ AlertWorker loop started.")
        while True:
            try:
                await check_alerts()
            except Exception as e:
                logger.error(f"Alert loop error: {e}")
            await asyncio.sleep(60) # 1분 주기

    async def trader_loop():
        logger.info("🤖 AutoTrader loop started.")
        trader = AutoTrader()
        while True:
            try:
                await trader.run_once()
            except Exception as e:
                logger.error(f"Trader loop error: {e}")
            
            # 트레이딩 인터벌 (기본 1시간)
            interval = int(os.getenv("TRADE_INTERVAL", "3600"))
            await asyncio.sleep(interval)

    # 백그라운드 태스크로 워커 실행
    alert_task = asyncio.create_task(alert_loop())
    trader_task = asyncio.create_task(trader_loop())
    
    yield # Server runs here
    
    # --- Shutdown ---
    logger.info("🛑 Server is shutting down...")
    
    # 워커 종료 (Optional: Cancel tasks if needed)
    alert_task.cancel()
    trader_task.cancel()
    
    # DB 연결 종료 등 정리 작업
    # await storage.close() 

app = FastAPI(
    title="Trading Assistant API v2.0",
    description="AI-Powered Trading Analysis Server - Web, Mobile, Extension Ready",
    version="2.0.0",
    lifespan=lifespan
)

# === CORS (Production Security - No Wildcards) ===
origins = [
    "http://localhost:5173",  # Vite Dev Server
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Fallback Port
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://localhost:8000",  # Frontend Served
    "http://127.0.0.1:8000",  # Frontend Served (IP)
    "chrome-extension://*",   # Extension Support
    "https://trading-assistant-all-in-one.onrender.com", # Production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["https://trading-assistant-all-in-one.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
chart_master = ChartMaster()

async def load_krx_bg():
    """백그라운드에서 KRX 데이터 로딩"""
    if krx_loader:
        await asyncio.to_thread(krx_loader.load)



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

# === API 엔드포인트 ===

# === API 엔드포인트 ===

@app.get("/api/health")
async def health_check():
    """GitHub Actions 및 Render 헬스체크용 엔드포인트"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


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

from src.services.integration_service import get_integration_service
integration_service = get_integration_service()

async def notify_analysis_result(ticker: str, result: Dict[str, Any]):
    """분석 완료 시 디스코드 알림 발송 (Background Task)"""
    try:
        final_score = result.get("final_score", 0)
        signal = result.get("signal", "HOLD")
        full_report_str = result.get("full_report", "")
        
        # 리포트 요약 (첫 2문장 또는 100자)
        summary = full_report_str[:150].replace('\n', ' ') + "..." if len(full_report_str) > 150 else full_report_str
        
        message = (
            f"📊 **Analysis Completed: {ticker}**\n"
            f"• Score: `{final_score}`\n"
            f"• Signal: `{signal}`\n"
            f"• Summary: {summary}\n"
        )
        
        color_map = {
            "STRONG_BUY": 5763719,  # Green
            "BUY": 3066993,         # Light Green
            "SELL": 15158332,       # Red
            "STRONG_SELL": 10038562 # Dark Red
        }
        color = color_map.get(signal, 9807270) # Default Grey
        
        notifier = get_notifier()
        await notifier.send_message(content=message, title=f"🔍 Analyzed: {ticker}", color=color)
        
    except Exception as e:
        logger.error(f"Notification error: {e}")

async def run_analysis(ticker: str, lang: str = "ko"):
    """
    종합 분석 엔진 실행 (IntegrationService 위임)
    - 기획된 Refactoring 2단계: Facade 패턴 적용
    """
    # 1. 티커 매핑 및 정규화
    final_ticker = get_final_ticker(ticker)
    logger.info(f"🔍 Analysis request for {final_ticker} (Input: {ticker})")
    
    # 2. 통합 서비스를 통한 종합 분석 실행
    raw_result = await integration_service.run_comprehensive_analysis(final_ticker)
    
    if raw_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=raw_result.get("message"))
    
    # 3. 추가 메타데이터 보완 (Display Name 등)
    try:
        import yfinance as yf
        stock = yf.Ticker(final_ticker)
        info = stock.info
        name = info.get('longName') or info.get('shortName') or final_ticker
        raw_result["display_name"] = f"{name} ({final_ticker})"
    except:
        raw_result["display_name"] = final_ticker

    # 4. 최종 데이터 직렬화 및 반환
    return safe_serialize(raw_result)

@app.post("/analyze")
async def analyze_post(req: AnalysisRequest, background_tasks: BackgroundTasks):
    """POST 방식 분석 엔드포인트"""
    try:
        # Validate Input
        validate_ticker(req.ticker)
        result = await run_analysis(req.ticker)
        
        # Send Notification in Background
        background_tasks.add_task(notify_analysis_result, req.ticker, result)
        
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis POST error: {e}")
        raise e  # Let global handler handle it

@app.get("/analyze/{ticker}")
async def analyze_get(ticker: str, background_tasks: BackgroundTasks):
    """GET 방식 분석 엔드포인트 (기존 호환성)"""
    try:
        # Validate Input
        validate_ticker(ticker)
        result = await run_analysis(ticker)
        
        # Send Notification in Background
        background_tasks.add_task(notify_analysis_result, ticker, result)
        
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise e

@app.get("/api/analyze/technical/{ticker}")
async def get_technical_analysis(ticker: str):
    """
    차티스트 에이전트의 정밀 기술적 분석 조회
    """
    try:
        from src.api.server import get_final_ticker
        validate_ticker(ticker)
        final_ticker = get_final_ticker(ticker)
        
        df = await collector.get_ohlcv(final_ticker, period="1y", interval="1d")
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Data not found")
            
        analysis = chart_master.analyze_chart(final_ticker, df)
        return JSONResponse(content=safe_serialize(analysis))
    except Exception as e:
        logger.error(f"Technical analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

        df = await collector.get_ohlcv(final_ticker, period=period, interval=actual_interval)
        
        # 데이터가 없는 경우 상위 인터벌로 대체 시도
        if (df is None or df.empty) and interval in ["1m", "5m", "15m", "30m", "60m"]:
            logger.info(f"Interval {interval} failed for {ticker}, falling back to daily.")
            df = await collector.get_ohlcv(final_ticker, period="1y", interval="1d")
            interval = "1d"

        if df is None or df.empty:
            return {"ticker": final_ticker, "data": []}
            
        if interval == "1y":
            logger.info(f"Applying 1Y resampling for {ticker}...")
            try:
                # 1. Date 컬럼/인덱스 확인 및 변환
                if 'Date' in df.columns:
                    # 문자열/객체를 datetime으로 변환 (오류 시 NaT)
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df = df.dropna(subset=['Date']) # NaT 제거
                    df.set_index('Date', inplace=True)
                
                # 인덱스가 여전히 DatetimeIndex가 아니라면 변환 시도
                if not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index, errors='coerce')
                        df = df[df.index.notnull()] # NaT 제거
                    except:
                        pass
                
                # 인덱스 변환 실패 시 리샘플링 불가 -> 원본 반환
                if not isinstance(df.index, pd.DatetimeIndex) or df.empty:
                    logger.warning("Could not convert index to DatetimeIndex for resampling")
                    # 여기서 pass 하면 아래 로직에서 df 그대로 사용됨
                else:
                    logger.info(f"Before resampling: {len(df)} rows")

                    # Resample to Yearly (Annual)
                    agg_dict = {
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }
                    # Filter valid columns
                    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
                    
                    # Try 'YE' first, then 'Y', then 'A'
                    resampled_df = None
                    for rule in ['YE', 'Y', 'A']:
                        try:
                            # kind='timestamp' is default but ensures index type
                            resampled_df = df.resample(rule, kind='timestamp').agg(agg_dict).dropna()
                            if not resampled_df.empty:
                                break
                        except Exception as rule_err:
                            continue
                    
                    if resampled_df is not None and not resampled_df.empty:
                        df = resampled_df
                        logger.info(f"After resampling: {len(df)} rows")
                    else:
                        logger.warning("Resampling resulted in empty DataFrame or failed.")
                    
            except Exception as e:
                logger.error(f"Resampling error completely failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                pass 

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
    elif isinstance(data, (np.floating, np.float32, np.float64)):
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
    경제 이벤트 캘린더 (v2: DB 연동 및 리스크 분석 포함)
    """
    try:
        from datetime import datetime, timedelta
        
        # storage 인스턴스 전달
        ticker_list = None
        if tickers:
            ticker_list = [validate_ticker(t.strip()) for t in tickers.split(",")]
        
        calendar_data = await event_calendar.get_calendar_v2(
            start_date=start_date,
            end_date=end_date,
            tickers=ticker_list,
            lang=lang,
            storage=storage
        )
        
        return safe_serialize(calendar_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/api/calendar/earnings")
async def get_earnings_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    country: str = "US",
    lang: str = "ko"
):
    """
    기업 실적 발표 전용 캘린더
    """
    try:
        from datetime import datetime, timedelta
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 국가별 fetcher 선택
        if country.upper() == "KR":
            events = await asyncio.to_thread(event_calendar.naver_earnings_fetcher.fetch, start, end, lang)
        else:
            events = await asyncio.to_thread(event_calendar.earnings_fetcher.fetch, start, end, lang)
        
        # Sort events by date
        if events:
            events.sort(key=lambda x: x.get('date', '9999-12-31'))
            
        return safe_serialize({
            "period": {"start": start_date, "end": end_date},
            "country": country.upper(),
            "events": events,
            "total_events": len(events)
        })
    except Exception as e:
        logger.error(f"Earnings calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/calendar/analyze")
async def get_event_impact(
    ticker: str,
    event_title: str
):
    """특정 이벤트가 특정 종목에 미치는 역사적 영향 분석"""
    try:
        validate_ticker(ticker)
        impact = await event_calendar.analyze_event_impact(ticker, event_title, storage)
        return safe_serialize(impact)
    except Exception as e:
        logger.error(f"Event impact analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        recommendations = await screener.get_recommendations(
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
        movers = await screener.get_top_movers(market=market)
        return safe_serialize(movers)
    except Exception as e:
        logger.error(f"Top movers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exchange-rate")
async def get_exchange_rate():
    """실시간 USD/KRW 환율 조회"""
    try:
        df = await collector.get_ohlcv("USDKRW=X", period="1d", interval="1m")
        if df is not None and not df.empty:
            rate = float(df['Close'].iloc[-1])
            return {"rate": rate, "ticker": "USDKRW=X", "timestamp": datetime.now().isoformat()}
        return {"rate": 1350.0, "note": "Fallback rate"} # 실패 시 기본값
    except Exception as e:
        logger.error(f"Exchange rate error: {e}")
        return {"rate": 1350.0}

# === 가상 계좌 관리 (Paper Trading) ===
@app.get("/api/virtual/account")
async def get_virtual_account():
    """가상 계좌 잔고 및 정보 조회"""
    try:
        balance = await storage.get_virtual_balance()
        return {
            "balance": balance,
            "currency": "KRW",
            "initial_balance": 10000000.0,
            "total_profit": balance - 10000000.0,
            "profit_rate": ((balance - 10000000.0) / 10000000.0) * 100
        }
    except Exception as e:
        logger.error(f"Virtual account error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/virtual/positions")
async def get_virtual_positions():
    """가상 계좌 보유 종목 조회"""
    try:
        positions = await storage.get_virtual_positions()
        
        # 현재 환율 가져오기
        rate_res = await get_exchange_rate()
        usd_krw = rate_res.get("rate", 1350.0)
        
        processed_positions = []
        for pos in positions:
            ticker = pos['ticker']
            is_usd = not (ticker.endswith(('.KS', '.KQ')) or ticker.isdigit())
            
            df = await collector.get_ohlcv(ticker, period="1d", interval="1m")
            current_price = df['Close'].iloc[-1] if df is not None and not df.empty else pos['avg_price']
            
            # 통화별 가치 계산 (원화 기준 합산을 위해)
            price_in_krw = current_price * usd_krw if is_usd else current_price
            avg_in_krw = pos['avg_price'] * usd_krw if is_usd else pos['avg_price']
            
            profit_krw = (price_in_krw - avg_in_krw) * pos['quantity']
            profit_rate = ((current_price - pos['avg_price']) / pos['avg_price']) * 100
            
            processed_positions.append({
                **pos,
                "is_usd": is_usd,
                "current_price": current_price,
                "current_price_krw": price_in_krw,
                "profit_krw": profit_krw,
                "profit_rate": profit_rate,
                "total_value_native": current_price * pos['quantity'],
                "total_value_krw": price_in_krw * pos['quantity']
            })
            
        return safe_serialize(processed_positions)
    except Exception as e:
        logger.error(f"Virtual positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === 백테스팅 & 최적화 (New) ===
from src.backtest.schemas import BacktestRequest, OptimizeRequest
from src.backtest.engine import BacktestEngine
from src.backtest.optimizer import StrategyOptimizer
from src.backtest.strategies.basic import RsiStrategy, SmaCrossStrategy

# Initialize Engine
backtest_engine = BacktestEngine(initial_capital=10000000)
strategy_optimizer = StrategyOptimizer(backtest_engine)

from src.backtest.strategies.advanced import BollingerStrategy, MacdStrategy

# ... (Previous imports)

@app.post("/api/backtest/run")
async def run_backtest(req: BacktestRequest):
    """
    백테스팅 실행
    """
    try:
        validate_ticker(req.ticker)
        # 1. Fetch Data
        df = await collector.get_ohlcv(req.ticker, period="2y", interval="1d") # Default period
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Historical data not found")
            
        # 2. Select Strategy
        strategy = None
        s_name = req.strategy_name.lower()
        
        if s_name == "rsi":
            period = req.params.get("period", 14)
            buy = req.params.get("buy_threshold", 30)
            sell = req.params.get("sell_threshold", 70)
            strategy = RsiStrategy(period=period, buy_threshold=buy, sell_threshold=sell)
            
        elif s_name in ["sma_cross", "golden_cross"]:
            fast = req.params.get("fast", 20)
            slow = req.params.get("slow", 60)
            strategy = SmaCrossStrategy(fast=fast, slow=slow)
            
        elif s_name == "bollinger":
            period = req.params.get("period", 20)
            std = req.params.get("std_dev", 2.0)
            strategy = BollingerStrategy(period=period, std_dev=std)
            
        elif s_name == "macd":
            fast = req.params.get("fast", 12)
            slow = req.params.get("slow", 26)
            sig = req.params.get("signal", 9)
            strategy = MacdStrategy(fast=fast, slow=slow, signal=sig)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy_name}")
            
        # 3. Run
        result = backtest_engine.run(df, strategy)
        return safe_serialize(result)
        
    except Exception as e:
        logger.error(f"Backtest run error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest/optimize")
async def optimize_strategy(req: OptimizeRequest):
    """
    최적 파라미터 찾기 (Grid Search)
    """
    try:
        validate_ticker(req.ticker)
        df = await collector.get_ohlcv(req.ticker, period="2y", interval="1d")
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Historical data not found")
            
        strategy_cls = None
        s_name = req.strategy_name.lower()
        
        if s_name == "rsi":
            strategy_cls = RsiStrategy
        elif s_name in ["sma_cross", "golden_cross"]:
            strategy_cls = SmaCrossStrategy
        elif s_name == "bollinger":
            strategy_cls = BollingerStrategy
        elif s_name == "macd":
            strategy_cls = MacdStrategy
        else:
             raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy_name}")

        result = strategy_optimizer.optimize(
            df, 
            strategy_cls, 
            search_space=req.search_space,
            target_metric=req.target_metric
        )
        return safe_serialize(result)
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
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
            "1h": await collector.get_ohlcv(final_ticker, period="60d", interval="60m"),
            "4h": await collector.get_ohlcv(final_ticker, period="120d", interval="1h"),
            "1d": await collector.get_ohlcv(final_ticker, period="1y", interval="1d"),
            "1wk": await collector.get_ohlcv(final_ticker, period="5y", interval="1wk"),
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

# === 정적 파일 서빙 및 SPA 라우팅 (최하단 배치) ===
# === 정적 파일 서빙 및 SPA 라우팅 (최하단 배치) ===
# 1. 절대 경로 계산 (실행 위치 기준 우선)
# 배치 파일에서 cd /d "%~dp0"를 하므로 getcwd()가 프로젝트 루트임
project_root = os.getcwd() 
dist_path = os.path.join(project_root, "frontend", "dist")

# Fallback: 만약 CWD가 엉뚱한 곳이면 상대 경로로 다시 시도 (3단계 상위)
if not os.path.exists(dist_path):
    server_file_path = os.path.abspath(__file__)
    # src/api/server.py -> src/api -> src -> project_root (3 steps)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(server_file_path)))
    dist_path = os.path.join(base_dir, "frontend", "dist")

logger.info(f"📂 Checking Frontend Dist Path: {dist_path}")

if os.path.exists(dist_path) and os.path.exists(os.path.join(dist_path, "index.html")):
    logger.info("✅ Frontend dist found! Serving UI...")
    
    # Assets
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    # Root Files (vite.svg, etc)
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

    @app.exception_handler(404)
    async def custom_404_handler(request, exc):
        if request.url.path.startswith("/api"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(os.path.join(dist_path, "index.html"))

else:
    logger.error(f"❌ Frontend dist NOT found at {dist_path}")
    logger.error(f"Current Working Dir: {os.getcwd()}")
    @app.get("/")
    async def root():
        return {
            "status": "ok", 
            "message": "API Server is running (Frontend UI Missing)", 
            "debug_path": dist_path,
            "cwd": os.getcwd()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)

