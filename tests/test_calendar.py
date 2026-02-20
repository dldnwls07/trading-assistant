import pytest
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.agents.calendar_fetchers import TradingEconomicsScraper, FinnhubEarningsFetcher, NaverEarningsScraper

def test_fetcher_error_logging(caplog):
    caplog.set_level(logging.ERROR)
    
    start = datetime.now()
    end = start + timedelta(days=7)
    
    # 1. TradingEconomicsScraper status_code 403 에러 처리 테스트
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        scraper = TradingEconomicsScraper()
        result = scraper.fetch(start, end)
        
        assert result == []
        assert "HTTP 403" in caplog.text or "status_code" in caplog.text

    # 2. Finnhub status_code 에러 처리 테스트
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        mock_get.return_value = mock_response
        
        scraper = FinnhubEarningsFetcher(api_key="test_key")
        result = scraper.fetch(start, end)
        
        assert result == []
        assert "HTTP 500" in caplog.text or "status_code" in caplog.text

def test_naver_single_earnings_error_logging(caplog):
    caplog.set_level(logging.ERROR)
    
    scraper = NaverEarningsScraper()
    start = datetime.now()
    end = start + timedelta(days=7)
    
    # yfinance 호출 시 에러 발생하도록
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.side_effect = Exception("yfinance error mocked")
        
        scraper._fetch_single_earnings({"symbol": "005930.KS", "code": "005930", "name": "삼성전자"}, start, end)
        
        assert "yfinance error mocked" in caplog.text

def test_te_scraper_data_exist():
    # Trading Economics에서 데이터가 정상적으로 들어오는지 확인
    scraper = TradingEconomicsScraper()
    # Check within next 7 days
    start = datetime.now()
    end = start + timedelta(days=7)
    events = scraper.fetch(start, end)
    
    # 0 반환 이슈 확인용 (기존 봇 접근이 막혔으면 len(events)가 0 혹은 403)
    assert len(events) > 0

def test_kr_earnings_exist():
    # 삼성전자 등 한국 종목의 미래 실적일이 반환되는지 확인
    scraper = NaverEarningsScraper()
    start = datetime.now()
    end = start + timedelta(days=60) # 실적 발표는 보통 분기마다 있으므로 여유있게 검색
    events = scraper.fetch(start, end)
    
    # yfinance 방식에서는 한국 데이터가 나오지 않아 0을 반환할 확률이 큼
    # 적절히 대체 모듈 구현시 통과해야 함
    print(f"\n--- KR Earnings Events ({len(events)}) ---")
    for ev in events:
        print(ev)
        
    assert len(events) >= 0 # fail to pass? wait, the plan wants it to fail first: "Expected: FAIL". But if I put len(events) > 0 it will fail.
    assert len(events) > 0, "No KR earnings found"

