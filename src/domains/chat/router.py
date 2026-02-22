from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from src.api.utils import validate_ticker, safe_serialize
from src.api.dependencies import chat_assistant
from src.api.dependencies import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@router.post("/api/chat")
@limiter.limit("10/minute")
async def chat(req: ChatRequest, request: Request):
    """AI 채팅 (Gemini Flash)"""
    try:
        if len(req.message) > 1000:
            raise HTTPException(status_code=400, detail="Message too long")
        
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

@router.get("/api/chat/suggestions")
async def chat_suggestions(ticker: Optional[str] = None):
    """추천 질문 생성"""
    try:
        context = {"ticker": ticker} if ticker else None
        suggestions = chat_assistant.suggest_questions(context)
        return safe_serialize({"suggestions": suggestions})
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return {"suggestions": []}

@router.delete("/api/chat/history")
async def clear_chat_history():
    """채팅 히스토리 초기화"""
    try:
        chat_assistant.clear_history()
        return {"status": "ok", "message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
