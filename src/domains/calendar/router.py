from fastapi import APIRouter, HTTPException
import logging
import asyncio
from typing import Optional
from datetime import datetime
import traceback

from src.api.utils import validate_ticker, safe_serialize
from src.api.dependencies import event_calendar, storage

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/calendar")
async def get_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tickers: Optional[str] = None,
    lang: str = "ko"
):
    """경제 이벤트 캘린더 (v2: DB 연동 및 리스크 분석 포함)"""
    try:
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

@router.get("/api/calendar/earnings")
async def get_earnings_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    country: str = "US",
    lang: str = "ko"
):
    """기업 실적 발표 전용 캘린더"""
    try:
        from datetime import timedelta
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if country.upper() == "KR":
            events = await asyncio.to_thread(event_calendar.naver_earnings_fetcher.fetch, start, end, lang)
        else:
            events = await asyncio.to_thread(event_calendar.earnings_fetcher.fetch, start, end, lang)
        
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

@router.get("/api/calendar/analyze")
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
