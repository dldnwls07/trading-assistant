import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
import os
from fredapi import Fred

logger = logging.getLogger(__name__)

class BaseFetcher:
    def fetch(self, start: datetime, end: datetime, lang: str = "ko", tickers: Optional[List[str]] = None) -> List[Dict]:
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

    def fetch(self, start: datetime, end: datetime, lang: str = "ko", tickers: Optional[List[str]] = None) -> List[Dict]:
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
                        "datetime": f"{release_date.strftime('%Y-%m-%d')}T22:30:00",
                        "country": "US",
                        "type": "Indicator",
                        "title": f"{title} (발표)",
                        "description": f"FRED 지표: {title}",
                        "importance": config["imp"],
                        "impact": "해당 지표 발표에 따른 변동성 유의",
                        "category": config["cat"],
                        "actual": "-",
                        "forecast": "-",
                        "previous": "-",
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

    def fetch(self, start: datetime, end: datetime, lang: str = "ko", tickers: Optional[List[str]] = None) -> List[Dict]:
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
                    
                    # Normalize time format
                    time_fmt = time_val if ":" in time_val else "00:00"
                    events.append({
                        "date": date_str,
                        "time": time_val if time_val else "00:00",
                        "datetime": f"{date_str}T{time_fmt}:00",
                        "country": country,
                        "type": "Indicator",
                        "title": event_title,
                        "description": f"TradingEconomics 지표: {event_title}",
                        "importance": importance,
                        "impact": "해당 지표 발표에 따른 변동성 유의",
                        "category": "macro",
                        "actual": actual if actual else "-",
                        "forecast": forecast if forecast else "-",
                        "previous": previous if previous else "-",
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

    def fetch(self, start: datetime, end: datetime, lang: str = "ko", tickers: Optional[List[str]] = None) -> List[Dict]:
        """
        네이버 금융에서 시가총액 상위 종목들을 가져온 뒤 yfinance로 실적 발표일 수집
        """
        import yfinance as yf
        import concurrent.futures
        
        if tickers and len(tickers) > 0:
            # 특정 종목 요청 시 글로벌 시총 상위 40개 조회를 건너뜀 (성능 최적화)
            return []
        
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
            "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0", # KOSPI
            "https://finance.naver.com/sise/sise_market_sum.naver?sosok=1"  # KOSDAQ
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
        """개별 종목의 실적 발표일 수집 (네이버 API 우선 확인 후 yfinance 폴백)"""
        import yfinance as yf
        e_events = []
        try:
            code = ticker_info['code']
            symbol = ticker_info['symbol']
            
            # 1차 시도: 네이버 금융 API (irScheduleInfo) 우선 확인
            integration_url = f"https://m.stock.naver.com/api/stock/{code}/integration"
            ir_target_dt = None
            try:
                res = requests.get(integration_url, headers=self.headers, timeout=3)
                if res.status_code == 200:
                    info = res.json()
                    ir_info = info.get("irScheduleInfo")
                    if ir_info and ir_info.get("date"):
                        # '2026-02-26' 등의 형식을 파싱
                        ir_date_str = ir_info.get("date")
                        ir_target_dt = datetime.strptime(ir_date_str, "%Y-%m-%d")
            except Exception as e:
                logger.debug(f"Naver IR API error for {code}: {e}")
            
            # 2차 시도 (Fallback): yfinance 활용
            if ir_target_dt is None:
                stock = yf.Ticker(symbol)
                cal = stock.calendar
                print(f"YF cal for {symbol}: {cal}")
                if cal is not None and 'Earnings Date' in cal:
                    e_dates = cal['Earnings Date']
                    if not isinstance(e_dates, (list, tuple, pd.Index)):
                        e_dates = [e_dates]
                    
                    for d in e_dates:
                        if pd.notna(d):
                            if hasattr(d, 'date'):
                                ir_target_dt = datetime.combine(d.date(), datetime.min.time())
                            else:
                                ir_target_dt = datetime.combine(d, datetime.min.time())
                            break  # 가장 가까운 하나만 사용

            if ir_target_dt and (start <= ir_target_dt <= end):
                e_events.append({
                    "date": ir_target_dt.strftime("%Y-%m-%d"),
                    "time": "08:00",
                    "datetime": f"{ir_target_dt.strftime('%Y-%m-%d')}T08:00:00",
                    "country": "KR",
                    "type": "Earnings",
                    "ticker": code,
                    "title": f"[{code}] {ticker_info['name']} 실적 발표",
                    "description": f"{ticker_info['name']} 실적 관련 발표",
                    "importance": "high",
                    "impact": "개별 종목 실적에 따른 변동성 확대",
                    "category": "stock",
                    "actual": "-",
                    "forecast": "-",
                    "previous": "-",
                    "source": "Naver/YF"
                })
        except Exception as e:
            logger.error(f"Naver/YF single earnings fetch error for {ticker_info.get('code', 'unknown')}: {e}")
        return e_events

class FinnhubEarningsFetcher(BaseFetcher):
    """Finnhub API 기반 미국 기업 실적 일정 수집 및 yfinance Fallback 지원"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1/calendar/earnings"

    def fetch(self, start: datetime, end: datetime, lang: str = "ko", tickers: Optional[List[str]] = None) -> List[Dict]:
        if tickers and len(tickers) > 0:
            # 특정 종목 요청 시 글로벌 시총 상위 20개 조회를 건너뜀 (성능 최적화)
            return []
            
        if not self.api_key: 
            logger.warning("Finnhub API key missing. Falling back to yfinance for US earnings.")
            return self._fallback_yfinance_fetch(start, end)
            
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
                time_val = "08:00" if item["hour"] == "am" else "16:00"
                events.append({
                    "date": item["date"],
                    "time": time_val,
                    "datetime": f"{item['date']}T{time_val}:00",
                    "country": "US",
                    "type": "Earnings",
                    "ticker": item["symbol"],
                    "title": f"{item['symbol']} 실적 발표",
                    "description": f"{item['symbol']} 분기 실적 및 가이던스 발표",
                    "importance": "high",
                    "impact": "개별 종목 실적에 따른 변동성 확대",
                    "category": "stock",
                    "actual": "-",
                    "forecast": str(item.get("epsEstimate", "-")),
                    "previous": "-",
                    "source": "Finnhub"
                })
        except Exception as e:
            logger.error(f"Finnhub earnings fetch error: {e}")
        return events

    def _fallback_yfinance_fetch(self, start: datetime, end: datetime) -> List[Dict]:
        """Finnhub 키가 없을 때 주요 미국 주식을 yfinance로 백업 수집"""
        import yfinance as yf
        import concurrent.futures
        import pandas as pd
        events = []
        
        # S&P 500 주요 시총 상위 티커 목록
        top_us_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "BRK-B", "LLY", "AVGO", "V", "JPM", "WMT", "UNH", "MA", "PG", "JNJ", "HD", "MRK", "COST"]
        
        def fetch_single(ticker):
            try:
                stock = yf.Ticker(ticker)
                cal = stock.calendar
                if cal is not None and 'Earnings Date' in cal:
                    e_dates = cal['Earnings Date']
                    if not isinstance(e_dates, (list, tuple, pd.Index)):
                        e_dates = [e_dates]
                        
                    for d in e_dates:
                        if pd.notna(d):
                            target_dt = datetime.combine(d.date(), datetime.min.time()) if hasattr(d, 'date') else datetime.combine(d, datetime.min.time())
                            if start <= target_dt <= end:
                                return {
                                    "date": target_dt.strftime("%Y-%m-%d"),
                                    "time": "08:00",
                                    "datetime": f"{target_dt.strftime('%Y-%m-%d')}T08:00:00",
                                    "country": "US",
                                    "type": "Earnings",
                                    "ticker": ticker,
                                    "title": f"[{ticker}] 실적 발표",
                                    "description": f"{ticker} 실적 관련 일정",
                                    "importance": "high",
                                    "impact": "개별 종목 실적에 따른 변동성 확대",
                                    "category": "stock",
                                    "actual": "-",
                                    "forecast": "-",
                                    "previous": "-",
                                    "source": "YF Fallback"
                                }
                            break  # 가장 가까운 일정 1개만 확인
            except: pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ticker = {executor.submit(fetch_single, t): t for t in top_us_tickers}
            for future in concurrent.futures.as_completed(future_to_ticker):
                res = future.result()
                if res: events.append(res)
                
        return events
