from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import logging

from src.domains.analysis_kr.services.kr_market_service import KRMarketAnalysisService
from src.domains.analysis_kr.infrastructure.won_reasoning_adapter import WONReasoningAdapter
from src.domains.trading_signals.router import SIGNAL_SERVICE, RL_ADAPTER

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis/kr", tags=["Analysis KR"])

# Lazy-loaded adapter
WON_ADAPTER = WONReasoningAdapter()
KR_SERVICE = KRMarketAnalysisService(WON_ADAPTER, SIGNAL_SERVICE)

class KRAnalysisRequest(BaseModel):
    ticker: str
    news: List[str]

class KRAnalysisResponse(BaseModel):
    ticker: str
    thought: str
    solution: str
    report: str

class HybridAnalysisResponse(BaseModel):
    ticker: str
    thought: str
    solution: str
    rl_action: str
    rl_confidence: float
    hybrid_comment: str

@router.post("/news", response_model=KRAnalysisResponse)
async def analyze_with_news(req: KRAnalysisRequest):
    """
    한국 시장 뉴스를 기반으로 WON-Reasoning 모델을 사용한 심층 분석 수행
    """
    try:
        if WON_ADAPTER.model is None:
            logger.info("📡 Loading WON-Reasoning Model into VRAM...")
            WON_ADAPTER.load_model()
            
        result = await KR_SERVICE.analyze_company_with_news(req.ticker, req.news)
        
        return KRAnalysisResponse(
            ticker=result.ticker,
            thought=result.thought,
            solution=result.solution,
            report=result.full_report
        )
    except Exception as e:
        logger.error(f"KR Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hybrid", response_model=HybridAnalysisResponse)
async def analyze_hybrid(req: KRAnalysisRequest):
    """
    [Hybrid] 로컬 LLM(기본적) + RL 에이전트(기술적) + Gemini(최종 합성)
    """
    try:
        # 1. LLM 모델 로드 확인
        if WON_ADAPTER.model is None:
            WON_ADAPTER.load_model()
        
        # 2. RL 모델 로드 확인
        if RL_ADAPTER.model is None:
            RL_ADAPTER.load_bundle()

        # 3. 하이브리드 분석 수행
        result = await KR_SERVICE.get_hybrid_analysis(req.ticker, req.news)
        
        return HybridAnalysisResponse(
            ticker=result["ticker"],
            thought=result["won_analysis"].thought,
            solution=result["won_analysis"].solution,
            rl_action=result["rl_signal"].action if result["rl_signal"] else "N/A",
            rl_confidence=result["rl_signal"].position_size if result["rl_signal"] else 0.0,
            hybrid_comment=result["hybrid_comment"]
        )
    except Exception as e:
        logger.error(f"Hybrid Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
