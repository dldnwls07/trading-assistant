from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from src.api.utils import validate_ticker, get_final_ticker, safe_serialize
from src.api.dependencies import chart_master, collector
from src.services.integration_service import get_integration_service
from src.services.analysis_service import AnalysisService
from src.utils.notifications import get_notifier

logger = logging.getLogger(__name__)

router = APIRouter()
integration_service = get_integration_service()
analysis_service = AnalysisService(collector, chart_master, integration_service)

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
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    """종합 분석 엔진 실행 (Service 위임)"""
    final_ticker = get_final_ticker(ticker)
    logger.info(f"🔍 Analysis request for {final_ticker} (Input: {ticker})")
    
    raw_result = await analysis_service.run_comprehensive_analysis(ticker, final_ticker)
    
    if raw_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=raw_result.get("message"))
    
    return safe_serialize(raw_result)

@router.post("/analyze")
async def analyze_post(req: AnalysisRequest, background_tasks: BackgroundTasks):
    try:
        validate_ticker(req.ticker)
        result = await run_analysis(req.ticker)
        background_tasks.add_task(notify_analysis_result, req.ticker, result)
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Analysis POST error: {e}")
        raise e

@router.get("/analyze/{ticker}")
async def analyze_get(ticker: str, background_tasks: BackgroundTasks):
    try:
        validate_ticker(ticker)
        result = await run_analysis(ticker)
        background_tasks.add_task(notify_analysis_result, ticker, result)
        return JSONResponse(content=result)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise e

@router.get("/api/analyze/technical/{ticker}")
async def get_technical_analysis(ticker: str):
    try:
        validate_ticker(ticker)
        final_ticker = get_final_ticker(ticker)
        
        analysis = await analysis_service.get_technical_analysis(final_ticker)
        if analysis is None:
            raise HTTPException(status_code=404, detail="Data not found")
            
        return JSONResponse(content=safe_serialize(analysis))
    except Exception as e:
        logger.error(f"Technical analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/multi-timeframe/{ticker}")
async def multi_timeframe_analysis(ticker: str):
    try:
        validate_ticker(ticker)
        final_ticker = get_final_ticker(ticker)
        
        result = await analysis_service.get_multi_timeframe_analysis(final_ticker)
        return safe_serialize(result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Multi-timeframe error: {e}")
        raise e
