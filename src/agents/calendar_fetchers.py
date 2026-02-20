import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup
import os
from fredapi import Fred

logger = logging.getLogger(__name__)

class BaseFetcher:
    def fetch(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        raise NotImplementedError

class FredFetcher(BaseFetcher):
    """FRED API 기반 미국 주요 지표 수집"""
    def __init__(self, api_key: str):
        self.fred = Fred(api_key=api_key) if api_key else None
        self.indicator_map = {
            10: {"cat": "inflation", "imp": "critical", "name_ko": "소비자물가지수 (CPI)"},
            11: {"cat": "inflation", "imp": "high", "name_ko": "생산자물가지수 (PPI)"},
            50: {"cat": "labor", "imp": "critical", "name_ko": "비농업 고용지수 (NFP)"},
            53: {"cat": "consumption", "imp": "high", "name_ko": "소매판매 지표"},
            103: {"cat": "macro", "imp": "critical", "name_ko": "국내총생산 (GDP)"},
            2: {"cat": "production", "imp": "medium", "name_ko": "산업생산 지수"},
        }

    def fetch(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        if not self.fred:
            logger.warning("FRED API key missing. Skipping FRED fetch.")
            return []
        
        events = []
        # The FRED API is primarily for historical data, not future schedules.
        # This implementation will fetch the *latest release* information for key indicators.
        # We use series IDs here, which the original developer seemed to confuse with release IDs.
        indicator_series_map = {
            'CPIAUCSL': {"cat": "inflation", "imp": "critical", "name_ko": "소비자물가지수 (CPI)"},
            'PPIACO': {"cat": "inflation", "imp": "high", "name_ko": "생산자물가지수 (PPI)"},
            'PAYEMS': {"cat": "labor", "imp": "critical", "name_ko": "비농업 고용지수 (NFP)"},
            'RSAFS': {"cat": "consumption", "imp": "high", "name_ko": "소매판매 지표"},
            'GDP': {"cat": "macro", "imp": "critical", "name_ko": "국내총생산 (GDP)"},
            'INDPRO': {"cat": "production", "imp": "medium", "name_ko": "산업생산 지수"},
        }

        for series_id, config in indicator_series_map.items():
            try:
                info = self.fred.get_series_info(series_id)
                if info is None:
                    continue

                last_updated_str = info.get('last_updated', '').split(' ')[0]
                if not last_updated_str:
                    continue

                release_date = datetime.strptime(last_updated_str, '%Y-%m-%d')

                if start <= release_date <= end:
                    title = config["name_ko"] if lang == "ko" else info.get('title', series_id)
                    events.append({
                        "date": release_date.strftime("%Y-%m-%d"),
                        "time": "22:30", # Default time for US indicators
                        "country": "US",
                        "type": "Indicator",
                        "title": f"{title} (발표)",
                        "importance": config["imp"],
                        "category": config["cat"],
                        "source": "FRED"
                    })
            except Exception as e:
                logger.error(f"FRED fetch error for series {series_id}: {e}")
        
        logger.info(f"FredFetcher found {len(events)} events.")
        return events

class TradingEconomicsScraper(BaseFetcher):
    """Trading Economics 크롤링을 통한 글로벌(G20) 지표 수집"""
    def __init__(self):
        self.base_url = "https://tradingeconomics.com/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://tradingeconomics.com/",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        # Trading Economics는 보통 현재 주간 일정을 보여주므로, 날짜 범위를 조정하여 요청할 로직이 필요할 수 있음
        # 여기서는 간단하게 기본 페이지를 파싱하는 예시를 구성 (실제 구현 시 URL 파라미터 활용 필요)
        events = []
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"TradingEconomics error: HTTP {response.status_code} ({response.text[:100]})")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='calendar')
            if not table: return []
            
            for row in table.find_all('tr'):
                # Data rows usually have data-id
                if not row.has_attr('data-id'):
                    continue
                
                # Fetch date from the first td's class
                time_td = row.find('td')
                if not time_td: continue
                
                date_str = None
                for cls in time_td.get('class', []):
                    if len(cls) == 10 and cls.count('-') == 2:
                        date_str = cls
                        break
                
                if not date_str:
                    continue
                    
                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                    
                if start <= event_date <= end:
                    time_span = time_td.find('span')
                    time_val = time_span.get_text(strip=True) if time_span else ""
                    
                    country = row.get('data-country', '').title()
                    event_title = row.get('data-event', '').title()
                    
                    actual_node = row.find('span', id='actual')
                    actual = actual_node.get_text(strip=True) if actual_node else ""
                    
                    forecast_node = row.find('a', id='forecast') or row.find('span', id='forecast')
                    forecast = forecast_node.get_text(strip=True) if forecast_node else ""
                    
                    previous_node = row.find('span', id='previous')
                    previous = previous_node.get_text(strip=True) if previous_node else ""
                    
                    # Estimate importance (TE uses other methods for stars now)
                    importance = "medium"
                    if "gdp" in event_title.lower() or "cpi" in event_title.lower() or "interest rate" in event_title.lower() or "fed" in event_title.lower():
                        importance = "critical"
                    elif "pmi" in event_title.lower() or "employment" in event_title.lower():
                        importance = "high"
                    
                    events.append({
                        "date": date_str,
                        "time": time_val,
                        "country": country,
                        "type": "Indicator",
                        "title": event_title,
                        "importance": importance,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous,
                        "source": "TradingEconomics"
                    })
        except Exception as e:
            logger.error(f"TradingEconomics scrape error: {e}")
        return events

class NaverEarningsScraper(BaseFetcher):
    """
    네이버 금융 시가총액 상위 종목과 yfinance를 연동하여 한국 기업 실적 발표 일정 수집
    """
    def __init__(self):
        self.market_sum_url = "https://finance.naver.com/sise/sise_market_sum.naver"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """
        네이버 금융에서 시가총액 상위 종목들을 가져온 뒤 yfinance로 실적 발표일 수집
        """
        import yfinance as yf
        import concurrent.futures
        
        events = []
        try:
            # 1. 시가총액 상위 종목(KOSPI, KOSDAQ) 티커 수집
            tickers = self._get_top_tickers(limit=40)
            
            # 2. 병렬로 yfinance 실적 데이터 수집
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_ticker = {executor.submit(self._fetch_single_earnings, t, start, end): t for t in tickers}
                for future in concurrent.futures.as_completed(future_to_ticker):
                    ticker_events = future.result()
                    if ticker_events:
                        events.extend(ticker_events)
            
            logger.info(f"NaverEarningsScraper found {len(events)} events for Korea.")
        except Exception as e:
            logger.error(f"Naver earnings fetch error: {e}")
            
        return events

    def _get_top_tickers(self, limit: int = 40) -> List[Dict]:
        """코스피 및 코스닥 시가총액 상위 종목 리스트 추출"""
        tickers = []
        urls = [
            self.market_sum_url + "?sosok=0", # KOSPI
            self.market_sum_url + "?sosok=1"  # KOSDAQ
        ]
        
        try:
            for url in urls:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                rows = soup.select('table.type_2 tr')
                count = 0
                for row in rows:
                    link = row.select_one('a.tltle')
                    if link:
                        code = link['href'].split('=')[-1]
                        name = link.get_text(strip=True)
                        suffix = ".KS" if "sosok=0" in url else ".KQ"
                        tickers.append({"code": code, "name": name, "symbol": code + suffix})
                        count += 1
                    if count >= limit // 2: break
                    
        except Exception as e:
            logger.warning(f"Failed to get top tickers from Naver: {e}")
        return tickers

    def _fetch_single_earnings(self, ticker_info: Dict, start: datetime, end: datetime) -> List[Dict]:
        """개별 종목의 실적 발표일 수집 (yfinance 활용)"""
        import yfinance as yf
        e_events = []
        try:
            symbol = ticker_info['symbol']
            stock = yf.Ticker(symbol)
            
            # yfinance calendar 데이터 확인
            cal = stock.calendar
            if cal and 'Earnings Date' in cal:
                e_dates = cal['Earnings Date']
                if not isinstance(e_dates, (list, tuple, pd.Index)):
                    e_dates = [e_dates]
                
                for d in e_dates:
                    if pd.notna(d):
                        try:
                            # d가 date 객체일 수도 있고 datetime 객체일 수도 있음
                            if hasattr(d, 'date'):
                                target_dt = datetime.combine(d.date(), datetime.min.time())
                            else:
                                target_dt = datetime.combine(d, datetime.min.time())
                            
                            if start <= target_dt <= end:
                                e_events.append({
                                    "date": target_dt.strftime("%Y-%m-%d"),
                                    "time": "장 시작 전/후",
                                    "country": "KR",
                                    "type": "Earnings",
                                    "ticker": ticker_info['code'],
                                    "title": f"[{ticker_info['code']}] {ticker_info['name']} 실적 발표",
                                    "importance": "high",
                                    "category": "stock",
                                    "source": "Naver/YF"
                                })
                        except: continue
        except Exception as e:
            logger.error(f"Naver/YF single earnings fetch error for {ticker_info.get('code', 'unknown')}: {e}")
        return e_events

class FinnhubEarningsFetcher(BaseFetcher):
    """Finnhub API 기반 미국 기업 실적 일정 수집"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1/calendar/earnings"

    def fetch(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        if not self.api_key: 
            logger.warning("Finnhub API key missing. Skipping US earnings fetch.")
            return []
        events = []
        try:
            params = {
                "from": start.strftime("%Y-%m-%d"),
                "to": end.strftime("%Y-%m-%d"),
                "token": self.api_key
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Finnhub API error: HTTP {response.status_code} ({response.text[:100]})")
                return []
                
            data = response.json()
            
            for item in data.get("earningsCalendar", []):
                events.append({
                    "date": item["date"],
                    "time": "장 시작 전" if item["hour"] == "am" else "장 마감 후",
                    "country": "US",
                    "type": "Earnings",
                    "ticker": item["symbol"],
                    "title": f"{item['symbol']} 실적 발표",
                    "importance": "high",
                    "category": "stock",
                    "forecast_eps": item.get("epsEstimate"),
                    "source": "Finnhub"
                })
        except Exception as e:
            logger.error(f"Finnhub earnings fetch error: {e}")
        return events
