from fastapi import APIRouter
from typing import Optional
from datetime import datetime

from src.api.dependencies import chat_assistant

router = APIRouter()

@router.get("/api/dictionary")
async def get_trading_dictionary(indicator_id: Optional[str] = None, view: str = "beginner"):
    """트레이딩 용어 및 지표 설명 (초보자/전문가 관점 분리)"""
    from src.utils.dictionary import INDICATOR_DESCRIPTIONS, get_explanation
    
    if indicator_id:
        explanation = get_explanation(indicator_id, view)
        return {"id": indicator_id, "explanation": explanation}
    
    return INDICATOR_DESCRIPTIONS

@router.get("/api/health")
async def health_check():
    """API 서버 상태 확인"""
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
