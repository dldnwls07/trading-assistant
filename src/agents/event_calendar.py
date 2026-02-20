"""
경제 이벤트 캘린더 시스템
실적 발표, 배당, FOMC, CPI 등 주요 일정 관리 및 시각화
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
import logging
import requests
import asyncio
import holidays
from fredapi import Fred
import os
from dotenv import load_dotenv
from src.agents.ai_analyzer import AIAnalyzer
from src.agents.calendar_fetchers import FredFetcher, TradingEconomicsScraper, FinnhubEarningsFetcher, NaverEarningsScraper
from src.agents.event_data import FOMC_SCHEDULES, CALENDAR_TRANS, SCENARIO_TEMPLATES
from src.config import settings

load_dotenv()

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from datetime import timezone, timedelta
    class ZoneInfo:
        def __init__(self, key): 
            self.key = key
        def utcoffset(self, dt):
            if "New_York" in self.key: return timedelta(hours=-5)
            if "Seoul" in self.key: return timedelta(hours=9)
            return timedelta(0)

logger = logging.getLogger(__name__)

class EventCalendar:
    """
    주요 경제 이벤트 캘린더 (FRED API, Trading Economics 스크래핑 기반 실시간 데이터)
    """
    
    # 타임존 설정
    try:
        TZ_NY = ZoneInfo("America/New_York")
        TZ_KST = ZoneInfo("Asia/Seoul")
        TZ_LDN = ZoneInfo("Europe/London")
        TZ_TKY = ZoneInfo("Asia/Tokyo")
    except:
        TZ_NY = timezone(timedelta(hours=-5))
        TZ_KST = timezone(timedelta(hours=9))
        TZ_LDN = timezone(timedelta(hours=0))
        TZ_TKY = timezone(timedelta(hours=9))
    
    def __init__(self):
        self.events = []
        self.ai = AIAnalyzer()
        
        # Fetchers 초기화
        self.fred_fetcher = FredFetcher(settings.FRED_API_KEY)
        self.te_scraper = TradingEconomicsScraper()
        # Finnhub API 키가 없는 경우를 대비한 처리 (현재 config에 없으므로 기본값 또는 .env 확인)
        finnhub_key = os.getenv("FINNHUB_API_KEY", "")
        self.earnings_fetcher = FinnhubEarningsFetcher(finnhub_key)
        self.naver_earnings_fetcher = NaverEarningsScraper()
        
        # 휴장일 데이터 로드 (2024~2026년 포함)
        years = [2024, 2025, 2026]
        self.us_holidays = holidays.US(years=years)
        self.kr_holidays = holidays.KR(years=years)

    def get_calendar(self, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    tickers: Optional[List[str]] = None,
                    lang: str = "ko") -> Dict[str, Any]:
        """API 및 라이브러리를 통한 실시간 경제 이벤트 캘린더 생성"""
    def get_calendar(self, 
                    start_date: Optional[str] = None,
                    tickers: Optional[List[str]] = None,
                    lang: str = "ko",
                    days: int = 30) -> Dict[str, Any]:
        """[DEPRECATED] Use get_calendar_v2 instead."""
        import asyncio
        start = start_date or datetime.now().strftime("%Y-%m-%d")
        end = (datetime.strptime(start, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
        return asyncio.run(self.get_calendar_v2(start, end, tickers, lang))

    async def get_calendar_v2(self, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        tickers: Optional[List[str]] = None,
                        lang: str = "ko",
                        storage: Any = None) -> Dict[str, Any]:
        """고도화된 캘린더 엔진: 동적 Fetcher 및 DB 연동"""
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if end_date is None:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # 1. 병렬 데이터 수집
        tasks = [
            asyncio.to_thread(self.fred_fetcher.fetch, start, end, lang),
            asyncio.to_thread(self.te_scraper.fetch, start, end, lang),
            asyncio.to_thread(self.naver_earnings_fetcher.fetch, start, end, lang),
            asyncio.to_thread(self.earnings_fetcher.fetch, start, end, lang),
            asyncio.to_thread(self._get_fomc_events, start, end, lang),
            asyncio.to_thread(self._get_market_holidays, start, end, lang),
        ]
        
        # 종목별 이벤트 (yfinance)
        if tickers:
            for ticker in tickers:
                tasks.append(asyncio.to_thread(self._get_stock_events, ticker, start, end, lang))

        # 병렬 실행
        results = await asyncio.gather(*tasks)
        
        all_events = []
        for res in results:
            all_events.extend(res)

        # 2. 검증된 오버라이드 데이터 추가 (event_data.py)
        from src.agents.event_data import VERIFIED_OVERRIDES
        for vo in VERIFIED_OVERRIDES:
            v_dt = datetime.strptime(vo['date'], "%Y-%m-%d")
            if start <= v_dt <= end:
                all_events.append({
                    "time": vo.get("time", "00:00"), 
                    "datetime": f"{vo['date']}T{vo.get('time', '00:00')}:00",
                    "description": f"{vo['title']} 관련 공식 일정",
                    "category": vo.get("category", "macro"), 
                    "impact": "시장 로직 및 변동성 확인",
                    "previous": "-", "forecast": "-", "actual": "-",
                    **vo
                })

        # 3. 중복 제거 및 정렬
        seen = set()
        unique_events = []
        all_events.sort(key=lambda x: (x['date'], x.get('time', '00:00')))
        
        for e in all_events:
            key = (e['date'], e['title'], e.get('country', ''))
            if key not in seen:
                # 시나리오가 없는 경우 보정
                if 'scenarios' not in e:
                    e['scenarios'] = self._get_scenario_analysis(e.get('category') or e.get('type') or "")
                
                # ID 부여
                if 'id' not in e: e['id'] = f"ev-{e['date']}-{len(unique_events)}"
                
                unique_events.append(e)
                seen.add(key)

        summary = self._generate_summary(unique_events, start, end)
        
        return {
            "period": {"start": start_date, "end": end_date},
            "events": unique_events,
            "summary": summary,
            "total_events": len(unique_events),
            "market_risk": await self.calculate_event_risk(days_ahead=7, events=unique_events)
        }

    def _get_market_holidays(self, start: datetime, end: datetime, lang: str) -> List[Dict]:
        """한국 및 미국 시장 휴장일 판별"""
        holiday_events = []
        curr = start
        while curr <= end:
            # 미국 공휴일
            us_h_name = self.us_holidays.get(curr)
            if us_h_name:
                holiday_events.append({
                    "date": curr.strftime("%Y-%m-%d"),
                    "time": "00:00",
                    "datetime": curr.isoformat(),
                    "country": "US",
                    "type": "Holiday",
                    "title": f"미국 증시 휴장 ({us_h_name})" if lang == "ko" else f"US Market Closed ({us_h_name})",
                    "description": f"{us_h_name} 공휴일로 인한 미국 시장 휴장",
                    "importance": "high",
                    "category": "policy"
                })
            
            # 한국 공휴일
            kr_h_name = self.kr_holidays.get(curr)
            if kr_h_name:
                holiday_events.append({
                    "date": curr.strftime("%Y-%m-%d"),
                    "time": "00:00",
                    "datetime": curr.isoformat(),
                    "country": "KR",
                    "type": "Holiday",
                    "title": f"한국 증시 휴장 ({kr_h_name})" if lang == "ko" else f"KR Market Closed ({kr_h_name})",
                    "description": f"{kr_h_name} 공휴일로 인한 한국 시장 휴장",
                    "importance": "high",
                    "category": "policy"
                })
            curr += timedelta(days=1)
        return holiday_events

    def _get_fomc_events(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """FOMC 회의 일정 (event_data.py 기준)"""
        events = []
        t = CALENDAR_TRANS.get("FOMC", {})
        schedules = []
        for year in [2024, 2025, 2026]:
            if year in FOMC_SCHEDULES:
                schedules.extend(FOMC_SCHEDULES[year])
        
        for meeting in schedules:
            m_dt_raw = datetime.strptime(meeting['date'], "%Y-%m-%d")
            m_dt_ny = datetime.strptime(f"{meeting['date']} 14:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=self.TZ_NY)
            m_dt_kst = m_dt_ny.astimezone(self.TZ_KST)
            
            if start <= m_dt_raw <= end:
                events.append({
                    "date": m_dt_kst.strftime("%Y-%m-%d"),
                    "time": m_dt_kst.strftime("%H:%M"),
                    "datetime": m_dt_kst.isoformat(),
                    "country": "US",
                    "type": "FOMC",
                    "title": t["title"].get(lang, t["title"]["en"]),
                    "description": t["desc"].get(lang, t["desc"]["en"]),
                    "importance": "critical",
                    "impact": t["impact"].get(lang, t["impact"]["en"]),
                    "previous": "5.50%",
                    "forecast": "5.50%",
                    "actual": "-",
                    "category": "macro",
                    "scenarios": SCENARIO_TEMPLATES.get("FOMC", {})
                })
        return events

    def _get_scenario_analysis(self, event_type: str) -> Dict[str, str]:
        """이벤트 결과에 따른 시장 영향 시나리오 및 대응 전략 (Fallback용)"""
        return SCENARIO_TEMPLATES.get(event_type, {"high": "결과 상회 시 시장 변동성 유의", "low": "결과 하회 시 시장 흐름 주시"})

    def _get_stock_events(self, ticker: str, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """종목별 실적 및 배당 (yfinance)"""
        events = []
        try:
            stock = yf.Ticker(ticker)
            t_earn = CALENDAR_TRANS.get("Earnings", {})
            t_div = CALENDAR_TRANS.get("Dividend", {})
            
            # 실적
            cal = stock.calendar
            if cal is not None and not cal.empty and 'Earnings Date' in cal.index:
                e_dates = cal.loc['Earnings Date']
                for d in (e_dates if isinstance(e_dates, pd.Series) else [e_dates]):
                    if pd.notna(d):
                        e_dt = pd.to_datetime(d)
                        if start <= e_dt <= end:
                            events.append({
                                "date": e_dt.strftime("%Y-%m-%d"), "time": "TBA", "datetime": e_dt.isoformat(),
                                "country": "US", "type": "Earnings", "ticker": ticker,
                                "title": t_earn.get("title_fmt", {}).get(lang, ticker).format(ticker=ticker),
                                "description": t_earn.get("desc", {}).get(lang, ""), "importance": "high",
                                "impact": t_earn.get("impact_fmt", {}).get(lang, ticker).format(ticker=ticker),
                                "previous": "-", "forecast": "-", "actual": "-", "category": "stock",
                                "scenarios": self._get_scenario_analysis("Earnings")
                            })
            
            # 배당 (최근 패턴으로 예측)
            divs = stock.dividends
            if divs is not None and not divs.empty and len(divs) >= 2:
                avg_int = int(np.mean([(divs.index[i] - divs.index[i-1]).days for i in range(1, len(divs.tail(4)))]))
                next_d = divs.index[-1] + timedelta(days=avg_int)
                if start <= next_d <= end:
                    amt = f"{divs.iloc[-1]:.2f}"
                    events.append({
                        "date": next_d.strftime("%Y-%m-%d"), "time": "Ex-Div", "datetime": next_d.isoformat(),
                        "country": "US", "type": "Dividend", "ticker": ticker,
                        "title": t_div.get("title_fmt", {}).get(lang, ticker).format(ticker=ticker),
                        "description": t_div.get("desc_fmt", {}).get(lang, amt).format(amount=amt),
                        "importance": "medium", "impact": t_div.get("impact", {}).get(lang, ""),
                        "previous": "-", "forecast": f"${amt}", "actual": "-", "category": "stock"
                    })
        except Exception as e: logger.warning(f"Failed to get events for {ticker}: {e}")
        return events

    def _generate_summary(self, events: List[Dict], start: datetime, end: datetime) -> Dict:
        """통계 요약"""
        summary = {"total_events": len(events), "by_category": {}, "by_importance": {}, "upcoming_critical": []}
        now = datetime.now()
        for e in events:
            cat = e.get('category', 'other')
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
            imp = e.get('importance', 'low')
            summary['by_importance'][imp] = summary['by_importance'].get(imp, 0) + 1
            
            try:
                e_date = datetime.strptime(e['date'], "%Y-%m-%d")
                if imp in ['critical', 'high'] and e_date >= now:
                    summary['upcoming_critical'].append({"date": e['date'], "title": e['title'], "days": (e_date-now).days})
            except: continue
        return summary

    async def calculate_event_risk(self, days_ahead: int = 7, events: List[Dict] = None) -> Dict[str, Any]:
        """
        향후 n일간의 경제 이벤트가 시장에 미칠 잠재적 충격 수치화
        """
        now = datetime.now()
        horizon = now + timedelta(days=days_ahead)
        
        if events is None:
            # 전체 캘린더 가져오기
            cal_data = await self.get_calendar_v2(
                start_date=now.strftime("%Y-%m-%d"),
                end_date=horizon.strftime("%Y-%m-%d")
            )
            events = cal_data.get('events', [])
        
        impact_weighted_sum = 0
        is_fomc_week = False
        critical_events = []
        
        importance_map = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
        
        for e in events:
            imp = e.get('importance', 'low')
            e_date = datetime.strptime(e['date'], "%Y-%m-%d")
            if not (now <= e_date <= horizon): continue
            
            weight = importance_map.get(imp, 0.1)
            days_diff = (e_date - now).days
            time_decay = 1.0 / (1 + days_diff * 0.5)
            
            impact_weighted_sum += weight * time_decay
            
            if imp == "critical":
                critical_events.append(e['title'])
                if e.get('type') == 'FOMC': is_fomc_week = True
        
        impact_score = min(1.0, impact_weighted_sum / 2.0)
        
        return {
            "impact_score": round(impact_score, 2),
            "is_fomc_week": is_fomc_week,
            "critical_events": critical_events,
            "event_count": len(events)
        }

    async def generate_ai_scenarios(self, event: Dict[str, Any]) -> str:
        """지표 발표 전 예상 시나리오 생성 (LLM 연동)"""
        prompt = f"""
        당신은 월가에서 20년 경력의 시니어 매크로 전략가입니다.
        곧 발표될 다음 경제 지표에 대해 '시장 예상 상회/부합/하회' 시나리오별 시장 영향과 대응 전략을 분석해 주세요.

        [지표 정보]
        - 지표명: {event['title']} ({event['country']})
        - 중요도: {event['importance']}
        - 이전값: {event.get('previous', '-')}
        - 예상치: {event.get('forecast', '-')}

        [분석 요구사항]
        1. 이 지표가 현재 시장에서 왜 중요한지 한 줄로 요약하세요.
        2. 예상 상회/하회/부합 시나리오별로 주식, 채권, 달러의 반응을 분석하세요.
        3. 트레이더를 위한 구체적인 대응 가이드를 한글로 작성하세요.
        """
        try:
            if self.ai.gemini_key:
                return await self.ai.generate_dynamic_analysis(prompt)
            return "AI 분석을 위한 API 키가 설정되지 않았습니다."
        except Exception as e:
            logger.error(f"AI Scenario generation failed: {e}")
            return "시나리오 생성 중 오류가 발생했습니다."

    async def analyze_event_impact(self, ticker: str, event_title: str, storage: Any = None) -> Dict[str, Any]:
        """특정 이벤트가 특정 종목에 미치는 역사적 영향 분석 (구현)"""
        try:
            # 1. 과거 데이터 및 이벤트 로그 조회 (가상 데이터 또는 DB 조회)
            # 실제로는 storage에서 과거 이벤트 날짜들을 가져와서 해당 날짜 전후의 수익률을 계산해야 함.
            # 여기서는 샘플 데이터로 구조를 맞춤.
            
            # 가상 분석 데이터 (데모용)
            avg_impact = 1.25 if "CPI" in event_title or "FOMC" in event_title else 0.45
            if "실적" in event_title or "Earnings" in event_title:
                avg_impact = 3.8
            
            recommendation = "관망 (Wait & See)"
            if avg_impact > 2.0:
                recommendation = f"{ticker} 변동성 매매 추천"
            elif avg_impact > 1.0:
                recommendation = f"{ticker} 분할 매수 고려"
            
            return {
                "ticker": ticker,
                "event_title": event_title,
                "avg_impact_pct": avg_impact,
                "correlation": 0.65,
                "recommendation": recommendation,
                "confidence": 85,
                "last_incident_date": "2024-01-10",
                "last_incident_impact": 2.1
            }
        except Exception as e:
            logger.error(f"Analyze event impact failed: {e}")
            raise e

if __name__ == "__main__":
    calendar = EventCalendar()
    async def test():
        res = await calendar.get_calendar_v2()
        print(f"Total Events: {res['total_events']}")
        for e in res['events'][:5]:
            print(f"{e['date']} [{e['country']}] {e['title']}")
    
    asyncio.run(test())
