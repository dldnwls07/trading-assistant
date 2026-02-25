from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging
from typing import List, Dict, Any

from src.api.utils import validate_ticker, safe_serialize
from src.api.dependencies import portfolio_analyzer, storage, collector, limiter
from src.domains.market_data.router import get_exchange_rate
from src.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)

router = APIRouter()
portfolio_service = PortfolioService(storage, collector, portfolio_analyzer)

class PortfolioRequest(BaseModel):
    holdings: List[Dict[str, Any]]

@router.post("/api/portfolio/analyze")
@limiter.limit("20/minute")
async def analyze_portfolio(req: PortfolioRequest, request: Request):
    """포트폴리오 AI 분석"""
    try:
        for holding in req.holdings:
            validate_ticker(holding.get("ticker", "AA"))
        result = portfolio_service.analyze_portfolio(req.holdings)
        return safe_serialize(result)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        raise e

@router.get("/api/virtual/account")
async def get_virtual_account(agent_id: int = None):
    """가상 계좌 잔고 및 정보 조회"""
    try:
        account_info = await portfolio_service.get_virtual_account_info(agent_id)
        return account_info
    except Exception as e:
        logger.error(f"Virtual account error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/virtual/positions")
async def get_virtual_positions(agent_id: int = None):
    """가상 계좌 보유 종목 조회"""
    try:
        rate_res = await get_exchange_rate()
        usd_krw = rate_res.get("rate", 1350.0)
        
        positions = await portfolio_service.get_virtual_positions_with_current_prices(usd_krw, agent_id)
        return safe_serialize(positions)
    except Exception as e:
        logger.error(f"Virtual positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
