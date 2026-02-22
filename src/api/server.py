from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
import asyncio
from datetime import datetime
import certifi
from contextlib import asynccontextmanager

from src.data.loader import krx_loader
from src.api.dependencies import storage, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Routers
from src.domains.analysis.router import router as analysis_router
from src.domains.market_data.router import router as market_data_router
from src.domains.chat.router import router as chat_router
from src.domains.calendar.router import router as calendar_router
from src.domains.portfolio.router import router as portfolio_router
from src.domains.screener.router import router as screener_router
from src.domains.backtest.router import router as backtest_router
from src.domains.tools.router import router as tools_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === SSL Certificate Patch ===
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
logger.info(f"🛡️ SSL Certificate Path Patched: {certifi.where()}")

async def load_krx_bg():
    """백그라운드에서 KRX 데이터 로딩"""
    if krx_loader:
        await asyncio.to_thread(krx_loader.load)

# === Lifespan Manager (Application Lifecycle) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 System Startup Initiated...")
    await storage.initialize()
    asyncio.create_task(load_krx_bg())
    logger.info("✅ Trading Assistant v2.0 서버가 준비되었습니다.")
    
    from src.api.alert_worker import check_alerts
    from src.agents.execution.auto_trader import AutoTrader
    
    async def alert_loop():
        logger.info("⏰ AlertWorker loop started.")
        while True:
            try:
                await check_alerts()
            except Exception as e:
                logger.error(f"Alert loop error: {e}")
            await asyncio.sleep(60)

    async def trader_loop():
        logger.info("🤖 AutoTrader loop started.")
        trader = AutoTrader()
        while True:
            try:
                await trader.run_once()
            except Exception as e:
                logger.error(f"Trader loop error: {e}")
            interval = int(os.getenv("TRADE_INTERVAL", "3600"))
            await asyncio.sleep(interval)

    alert_task = asyncio.create_task(alert_loop())
    trader_task = asyncio.create_task(trader_loop())
    
    yield
    
    logger.info("🛑 Server is shutting down...")
    alert_task.cancel()
    trader_task.cancel()

app = FastAPI(
    title="Trading Assistant API v2.0",
    description="AI-Powered Trading Analysis Server - Web, Mobile, Extension Ready",
    version="2.0.0",
    lifespan=lifespan
)

# === CORS ===
origins = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:5174", "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://localhost:8000", "http://127.0.0.1:8000",
    "chrome-extension://*",
    "https://trading-assistant-all-in-one.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["https://trading-assistant-all-in-one.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Rate Limiting ===
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# === Global Exception Handler ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Error: {exc} Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error_id": datetime.now().timestamp()},
    )

# === API Routers ===
app.include_router(analysis_router)
app.include_router(market_data_router)
app.include_router(chat_router)
app.include_router(calendar_router)
app.include_router(portfolio_router)
app.include_router(screener_router)
app.include_router(backtest_router)
app.include_router(tools_router)

# === 정적 파일 서빙 및 SPA 라우팅 (최하단 배치) ===
project_root = os.getcwd() 
dist_path = os.path.join(project_root, "frontend", "dist")

if not os.path.exists(dist_path):
    server_file_path = os.path.abspath(__file__)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(server_file_path)))
    dist_path = os.path.join(base_dir, "frontend", "dist")

logger.info(f"📂 Checking Frontend Dist Path: {dist_path}")

if os.path.exists(dist_path) and os.path.exists(os.path.join(dist_path, "index.html")):
    logger.info("✅ Frontend dist found! Serving UI...")
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
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
