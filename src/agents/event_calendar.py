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

logger = logging.getLogger(__name__)

class EventCalendar:
    """
    주요 경제 이벤트 캘린더
    - 기업 실적 발표일
    - 배당락일 / 배당 지급일
    - FOMC 회의 일정
    - 주요 경제 지표 발표 (CPI, 고용지표 등)
    """
    
    # 2024년 FOMC 회의 일정 (고정)
    FOMC_SCHEDULE_2024 = [
        {"date": "2024-01-31", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-03-20", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-05-01", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-06-12", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-07-31", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-09-18", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-11-07", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2024-12-18", "type": "FOMC Meeting", "importance": "high"}
    ]
    
    # 2026년 FOMC 회의 일정 (예상)
    FOMC_SCHEDULE_2026 = [
        {"date": "2026-01-28", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-03-18", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-04-29", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-06-17", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-07-29", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-09-16", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-11-04", "type": "FOMC Meeting", "importance": "high"},
        {"date": "2026-12-16", "type": "FOMC Meeting", "importance": "high"}
    ]
    
    def __init__(self):
        self.events = []
    
    def get_calendar(self, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    tickers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        지정된 기간의 이벤트 캘린더 생성
        
        Args:
            start_date: 시작일 (YYYY-MM-DD), 기본값: 오늘
            end_date: 종료일 (YYYY-MM-DD), 기본값: 3개월 후
            tickers: 추적할 종목 리스트
            
        Returns:
            {
                "period": {"start": "...", "end": "..."},
                "events": [...],
                "summary": {...}
            }
        """
        # 기본 날짜 설정
        if start_date is None:
            start = datetime.now()
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None:
            end = start + timedelta(days=90)  # 3개월
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info(f"캘린더 생성: {start.date()} ~ {end.date()}")
        
        all_events = []
        
        # 1. FOMC 일정 추가
        all_events.extend(self._get_fomc_events(start, end))
        
        # 2. 경제 지표 발표 일정 추가
        all_events.extend(self._get_economic_indicators(start, end))
        
        # 3. 종목별 이벤트 추가
        if tickers:
            for ticker in tickers:
                all_events.extend(self._get_stock_events(ticker, start, end))
        
        # 날짜순 정렬
        all_events.sort(key=lambda x: x['date'])
        
        # 요약 통계
        summary = self._generate_summary(all_events, start, end)
        
        return {
            "period": {
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d")
            },
            "events": all_events,
            "summary": summary,
            "total_events": len(all_events)
        }
    
    def _get_fomc_events(self, start: datetime, end: datetime) -> List[Dict]:
        """FOMC 회의 일정"""
        events = []
        
        # 연도에 맞는 스케줄 선택
        schedules = []
        if start.year <= 2024 <= end.year:
            schedules.extend(self.FOMC_SCHEDULE_2024)
        if start.year <= 2026 <= end.year:
            schedules.extend(self.FOMC_SCHEDULE_2026)
        
        for meeting in schedules:
            meeting_date = datetime.strptime(meeting['date'], "%Y-%m-%d")
            if start <= meeting_date <= end:
                events.append({
                    "date": meeting['date'],
                    "type": "FOMC",
                    "title": "연준 FOMC 회의",
                    "description": "금리 결정 및 통화정책 발표",
                    "importance": "critical",
                    "impact": "전체 시장에 큰 영향",
                    "category": "macro"
                })
        
        return events
    
    def _get_economic_indicators(self, start: datetime, end: datetime) -> List[Dict]:
        """주요 경제 지표 발표 일정"""
        events = []
        
        # CPI (소비자물가지수) - 매월 중순
        current = start.replace(day=15)
        while current <= end:
            if current >= start:
                events.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "type": "CPI",
                    "title": "소비자물가지수 (CPI) 발표",
                    "description": "인플레이션 지표, 금리 정책에 영향",
                    "importance": "high",
                    "impact": "채권, 주식 시장 변동성 증가",
                    "category": "macro"
                })
            current = (current + timedelta(days=32)).replace(day=15)
        
        # 고용지표 (Non-Farm Payrolls) - 매월 첫째 주 금요일
        current = start.replace(day=1)
        while current <= end:
            # 첫째 주 금요일 찾기
            first_friday = current
            while first_friday.weekday() != 4:  # 4 = 금요일
                first_friday += timedelta(days=1)
            
            if start <= first_friday <= end:
                events.append({
                    "date": first_friday.strftime("%Y-%m-%d"),
                    "type": "NFP",
                    "title": "미국 고용지표 (NFP) 발표",
                    "description": "비농업 고용 변화, 실업률",
                    "importance": "high",
                    "impact": "달러 및 주식 시장 영향",
                    "category": "macro"
                })
            
            current = (current + timedelta(days=32)).replace(day=1)
        
        # GDP 발표 - 분기별 (1, 4, 7, 10월 말)
        gdp_months = [1, 4, 7, 10]
        for month in gdp_months:
            for year in range(start.year, end.year + 1):
                gdp_date = datetime(year, month, 28)
                if start <= gdp_date <= end:
                    events.append({
                        "date": gdp_date.strftime("%Y-%m-%d"),
                        "type": "GDP",
                        "title": "GDP 성장률 발표",
                        "description": "분기별 경제 성장률",
                        "importance": "medium",
                        "impact": "경제 전반 건강도 평가",
                        "category": "macro"
                    })
        
        return events
    
    def _get_stock_events(self, ticker: str, start: datetime, end: datetime) -> List[Dict]:
        """종목별 이벤트 (실적, 배당)"""
        events = []
        
        try:
            stock = yf.Ticker(ticker)
            
            # 1. 실적 발표일
            calendar = stock.calendar
            if calendar is not None and not calendar.empty:
                if 'Earnings Date' in calendar.index:
                    earnings_dates = calendar.loc['Earnings Date']
                    if isinstance(earnings_dates, pd.Series):
                        for date in earnings_dates:
                            if pd.notna(date):
                                earnings_date = pd.to_datetime(date)
                                if start <= earnings_date <= end:
                                    events.append({
                                        "date": earnings_date.strftime("%Y-%m-%d"),
                                        "type": "Earnings",
                                        "ticker": ticker,
                                        "title": f"{ticker} 실적 발표",
                                        "description": "분기 실적 및 가이던스 발표",
                                        "importance": "high",
                                        "impact": f"{ticker} 주가 변동성 증가",
                                        "category": "stock"
                                    })
            
            # 2. 배당 정보
            dividends = stock.dividends
            if dividends is not None and not dividends.empty:
                # 최근 배당 패턴 분석하여 향후 배당일 예측
                recent_divs = dividends.tail(4)  # 최근 4회
                if len(recent_divs) >= 2:
                    # 평균 배당 주기 계산
                    intervals = []
                    for i in range(1, len(recent_divs)):
                        interval = (recent_divs.index[i] - recent_divs.index[i-1]).days
                        intervals.append(interval)
                    
                    avg_interval = int(np.mean(intervals))
                    last_div_date = recent_divs.index[-1]
                    
                    # 다음 배당일 예측
                    next_div_date = last_div_date + timedelta(days=avg_interval)
                    
                    if start <= next_div_date <= end:
                        events.append({
                            "date": next_div_date.strftime("%Y-%m-%d"),
                            "type": "Dividend",
                            "ticker": ticker,
                            "title": f"{ticker} 배당락일 (예상)",
                            "description": f"예상 배당금: ${recent_divs.iloc[-1]:.2f}",
                            "importance": "medium",
                            "impact": "배당 투자자 주목",
                            "category": "stock"
                        })
            
        except Exception as e:
            logger.warning(f"{ticker} 이벤트 수집 실패: {e}")
        
        return events
    
    def _generate_summary(self, events: List[Dict], start: datetime, end: datetime) -> Dict:
        """이벤트 요약 통계"""
        summary = {
            "total_events": len(events),
            "by_category": {},
            "by_importance": {},
            "upcoming_critical": [],
            "this_week": []
        }
        
        # 카테고리별 집계
        for event in events:
            category = event.get('category', 'other')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            importance = event.get('importance', 'low')
            summary['by_importance'][importance] = summary['by_importance'].get(importance, 0) + 1
        
        # 중요 이벤트 (critical, high)
        now = datetime.now()
        for event in events:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            
            if event.get('importance') in ['critical', 'high'] and event_date >= now:
                summary['upcoming_critical'].append({
                    "date": event['date'],
                    "title": event['title'],
                    "days_until": (event_date - now).days
                })
        
        # 이번 주 이벤트
        week_end = now + timedelta(days=7)
        for event in events:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            if now <= event_date <= week_end:
                summary['this_week'].append({
                    "date": event['date'],
                    "title": event['title'],
                    "importance": event.get('importance', 'low')
                })
        
        return summary
    
    def get_next_important_event(self, ticker: Optional[str] = None) -> Optional[Dict]:
        """다음 중요 이벤트 조회"""
        calendar = self.get_calendar(tickers=[ticker] if ticker else None)
        
        now = datetime.now()
        for event in calendar['events']:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            if event_date >= now and event.get('importance') in ['critical', 'high']:
                return event
        
        return None
    
    def format_for_ui(self, calendar_data: Dict) -> str:
        """UI 표시용 포맷팅"""
        lines = []
        lines.append(f"📅 이벤트 캘린더 ({calendar_data['period']['start']} ~ {calendar_data['period']['end']})")
        lines.append(f"총 {calendar_data['total_events']}개 이벤트\n")
        
        # 이번 주 이벤트
        if calendar_data['summary']['this_week']:
            lines.append("🔔 이번 주 주요 일정:")
            for event in calendar_data['summary']['this_week']:
                lines.append(f"  • {event['date']}: {event['title']}")
            lines.append("")
        
        # 다가오는 중요 이벤트
        if calendar_data['summary']['upcoming_critical']:
            lines.append("⚠️ 다가오는 중요 이벤트:")
            for event in calendar_data['summary']['upcoming_critical'][:5]:
                lines.append(f"  • {event['date']} (D-{event['days_until']}): {event['title']}")
            lines.append("")
        
        # 카테고리별 통계
        lines.append("📊 카테고리별 이벤트:")
        for cat, count in calendar_data['summary']['by_category'].items():
            lines.append(f"  • {cat}: {count}개")
        
        return "\n".join(lines)


# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    calendar = EventCalendar()
    
    # 향후 3개월 캘린더 (AAPL 포함)
    result = calendar.get_calendar(tickers=["AAPL", "MSFT"])
    
    print(calendar.format_for_ui(result))
    
    print("\n\n=== 전체 이벤트 목록 ===")
    for event in result['events'][:10]:  # 처음 10개만
        print(f"\n{event['date']} - {event['title']}")
        print(f"  중요도: {event['importance']}")
        print(f"  {event['description']}")
