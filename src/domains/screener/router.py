from fastapi import APIRouter, HTTPException
import logging
from typing import Optional

from src.api.utils import safe_serialize
from src.api.dependencies import screener

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/screener/recommendations")
async def get_recommendations(
    style: Optional[str] = "balanced",
    market: Optional[str] = "US",
    limit: int = 10
):
    """AI 추천 종목 스크리닝"""
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

@router.get("/api/screener/top-movers")
async def get_top_movers(market: str = "US"):
    """급등/급락 종목"""
    try:
        movers = await screener.get_top_movers(market=market)
        return safe_serialize(movers)
    except Exception as e:
        logger.error(f"Top movers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
