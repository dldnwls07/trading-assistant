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
