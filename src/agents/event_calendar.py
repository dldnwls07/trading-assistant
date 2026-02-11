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
    주요 경제 이벤트 캘린더 (SaveTicker 수준의 고밀도 글로벌 데이터 제공)
    """
    
    # FOMC 회의 일정
    FOMC_SCHEDULE_2024 = [
        {"date": "2024-01-31", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-03-20", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-05-01", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-06-12", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-07-31", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-09-18", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-11-07", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2024-12-18", "type": "FOMC Meeting", "importance": "critical"}
    ]
    
    FOMC_SCHEDULE_2025 = [
        {"date": "2025-01-29", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-03-19", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-05-07", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-06-18", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-07-30", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-09-17", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-11-05", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2025-12-17", "type": "FOMC Meeting", "importance": "critical"}
    ]

    FOMC_SCHEDULE_2026 = [
        {"date": "2026-01-28", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-03-18", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-04-29", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-06-17", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-07-29", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-09-16", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-11-04", "type": "FOMC Meeting", "importance": "critical"},
        {"date": "2026-12-16", "type": "FOMC Meeting", "importance": "critical"}
    ]
    
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
    
    # 다국어 지원 및 이벤트 메타데이터
    TRANS = {
        "FOMC": {
            "title": {"ko": "연준 FOMC 금리 결정", "en": "Fed Interest Rate Decision", "zh": "美联储利率决议", "ja": "FOMC金利発表"},
            "desc": {"ko": "미 연방준비제도 이사회 기준 금리 및 정책 성명서", "en": "Interest rate decision & policy statement", "zh": "利率决议及货币政策声明", "ja": "政策金利発表および声明"},
            "impact": {"ko": "전 세계 금융 시장의 핵심 변수", "en": "Critical driver for global markets", "zh": "全球市场关键驱动力", "ja": "世界市場의 主要指標"}
        },
        "CPI": {
            "title": {"ko": "소비자물가지수 (CPI)", "en": "CPI (MoM/YoY)", "zh": "消费者物价指数", "ja": "消費者物価指数"},
            "desc": {"ko": "인플레이션 핵심 지표, 금리 정책 결정의 근거", "en": "Primary inflation gauge, affects policy", "zh": "通胀衡量指标", "ja": "主要インフレ指標"},
            "impact": {"ko": "인플레 압력 판단, 채권/주식 변동성", "en": "Bond/stock volatility driver", "zh": "市场波动主要因素", "ja": "債券・株式의 変動要因"}
        },
        "PPI": {
            "title": {"ko": "생산자물가지수 (PPI)", "en": "PPI (MoM/YoY)", "zh": "生产者物价指数", "ja": "生産者物価指数"},
            "desc": {"ko": "도매 물가 상승률, CPI의 선행 지표", "en": "Leading indicator for consumer inflation", "zh": "CPI的领先指标", "ja": "CPI의 先行指標"},
            "impact": {"ko": "제조 비용 압력 분석", "en": "Analyzes manufacturing cost pressure", "zh": "分析生产成本压力", "ja": "製造コスト圧力의 分析"}
        },
        "NFP": {
            "title": {"ko": "비농업 고용지수 (NFP)", "en": "Non-Farm Payrolls", "zh": "非农就业人数", "ja": "非農業部門雇用者数"},
            "desc": {"ko": "가장 중요한 월간 고용 보고서", "en": "Most important monthly jobs report", "zh": "最重要的月度就业报告", "ja": "最重要의 雇用統計"},
            "impact": {"ko": "경제 성장의 건전성 증거", "en": "Proof of economic health", "zh": "经济健康状况的证据", "ja": "経済健全性의 証明"}
        },
        "GDP": {
            "title": {"ko": "GDP 성장률 (분기별)", "en": "GDP (QoQ/YoY)", "zh": "GDP增长率", "ja": "GDP成長率"},
            "desc": {"ko": "한 국가의 경제 성장 속도 측정", "en": "Measures economic expansion rate", "zh": "衡量经济增长速度", "ja": "経済成長率의 測定"},
            "impact": {"ko": "경기 순환 주기 판단", "en": "Determines economic cycle phase", "zh": "判断经济周期", "ja": "景気サイクルの判断"}
        },
        "Retail Sales": {
            "title": {"ko": "소매판매 (Retail Sales)", "en": "Retail Sales (MoM)", "zh": "零售销售", "ja": "小売売上高"},
            "desc": {"ko": "소비자 지출의 강도 측정", "en": "Measures strength of consumer spending", "zh": "衡量消费者支出力度", "ja": "個人消費의 強さ를 測定"},
            "impact": {"ko": "경제 성장의 70% 차지하는 소비 체크", "en": "Checks core segment of US GDP", "zh": "检查美国GDP的核心部分", "ja": "個人消費の確認"}
        },
        "PMI": {
            "title": {"ko": "ISM 제조업 PMI", "en": "ISM Manufacturing PMI", "zh": "ISM 制造业 PMI", "ja": "ISM 製造業 PMI"},
            "desc": {"ko": "제조업 활동 및 실물 경기 판단", "en": "Gauge of manufacturing activity", "zh": "制造业活动指标", "ja": "製造業活動の指標"},
            "impact": {"ko": "경기 확산/수축 판단 기준 (50 기준)", "en": "Expansion/contraction baseline", "zh": "扩张/收缩基准", "ja": "拡大・縮小의 基準"}
        },
        "Sentiment": {
            "title": {"ko": "소비자심리지수", "en": "Consumer Sentiment", "zh": "消费者信心指数", "ja": "消費者態度指数"},
            "desc": {"ko": "미래 소비 지출에 대한 가계의 낙관론", "en": "Household optimism about spending", "zh": "家庭支出乐观度", "ja": "個人消費の見通し"},
            "impact": {"ko": "향후 소매 판매의 선행 지표", "en": "Proxy for future retail sales", "zh": "零售销售的前瞻指标", "ja": "小売売上高의 先行指標"}
        },
        "BOK": {
            "title": {"ko": "한은 금리 결정", "en": "BOK Rate Decision", "zh": "韩国央行利率决议", "ja": "韓国中銀金利発表"},
            "desc": {"ko": "대한민국 기준 금리 결정", "en": "South Korea base rate change", "zh": "韩国基准利率决议", "ja": "韓国政策金利の決定"},
            "impact": {"ko": "환율 및 국채 시장 직격탄", "en": "Direct impact on FX & bonds", "zh": "对外汇和债券市场的直接影响", "ja": "為替・債券市場への影響"}
        },
        "Claims": {
            "title": {"ko": "신규 실업수당 청구", "en": "Initial Jobless Claims", "zh": "初请失业金人数", "ja": "新規실업보험신청"},
            "desc": {"ko": "주간 단위 고용 시장 악화 감지", "en": "Weekly labor market check", "zh": "每周劳动力市场检查", "ja": "週間労働市場チェック"},
            "impact": {"ko": "고용 부진 여부 즉시 파악", "en": "Immediate view of labor stress", "zh": "立即查看劳动力压力", "ja": "雇用不安의 即時把握"}
        },
        "ECB": {
            "title": {"ko": "유럽중앙은행(ECB) 금리 결정", "en": "ECB Rate Decision", "zh": "欧洲央行利率决议", "ja": "欧州中銀金利発表"},
            "desc": {"ko": "유로존 기준 금리 및 통화 정책 발표", "en": "Eurozone base rate & policy", "zh": "欧元区基准利率及货币政策", "ja": "ユー로圏政策金利発表"},
            "impact": {"ko": "유로화(EUR) 및 유럽 증시 영향", "en": "Impact on EUR & EU stocks", "zh": "对欧元和欧洲股市的影响", "ja": "ユーロおよび欧州市場への影響"}
        },
        "BOJ": {
            "title": {"ko": "일본은행(BOJ) 금리 결정", "en": "BOJ Rate Decision", "zh": "日本央行利率决议", "ja": "日銀政策金利発表"},
            "desc": {"ko": "일본 기준 금리 및 YCC 정책 발표", "en": "Japan rate & YCC statement", "zh": "日本基准利率及YCC政策", "ja": "日本の政策金利発表"},
            "impact": {"ko": "엔화(JPY) 및 캐리 트레이드 영향", "en": "Impact on JPY & carry trade", "zh": "对日元和套利交易的影响", "ja": "円およびキャリートレードへの影響"}
        },
        "Speech": {
            "title_fmt": {"ko": "{name} 연준 위원 연설", "en": "Fed Speech: {name}", "zh": "美联储官员演讲: {name}", "ja": "FRB高官演説: {name}"},
            "desc": {"ko": "통화 정책 방향에 대한 힌트 제공", "en": "Provides hints on policy direction", "zh": "提供货币政策方向的线索", "ja": "金融政策의 方向性に関する示唆"},
            "impact": {"ko": "발언 수준에 따른 시장 변동성", "en": "Volatility based on tone", "zh": "基于调性的波动", "ja": "発言内容に伴う変動性"}
        },
        "Auction": {
            "title_fmt": {"ko": "미 {term} 국채 입찰", "en": "US {term} Auction", "zh": "美国 {term} 国债拍卖", "ja": "米 {term} 国債入札"},
            "desc": {"ko": "미 재무부 국채 발행 및 수요 확인", "en": "US Treasury debt issuance", "zh": "美财政部债务发行", "ja": "米財務省国債発行"},
            "impact": {"ko": "채권 금리 및 달러 인덱스 영향", "en": "Impact on yields & Dollar", "zh": "对收益率和美元的影响", "ja": "利回りおよびドルへの影響"}
        },
        "Earnings": {
            "title_fmt": {"ko": "{ticker} 실적 발표", "en": "{ticker} Earnings", "zh": "{ticker} 财报", "ja": "{ticker} 決算"},
            "desc": {"ko": "분기 영업이익 및 향후 가이던스", "en": "Net income & outlook", "zh": "净利润及展望", "ja": "純利益および見通し"},
            "impact_fmt": {"ko": "{ticker} 주가 변동성 확대", "en": "High volatility for {ticker}", "zh": "{ticker} 股价大波动", "ja": "{ticker} 株価의 変動性拡大"}
        },
        "Dividend": {
            "title_fmt": {"ko": "{ticker} 배당락일", "en": "{ticker} Ex-Div Date", "zh": "{ticker} 除息日", "ja": "{ticker} 配当落ち日"},
            "desc_fmt": {"ko": "배당금: ${amount}", "en": "Div: ${amount}", "zh": "股息: ${amount}", "ja": "配当: ${amount}"},
            "impact": {"ko": "권리 확보를 위한 매수 기한", "en": "Buy deadline for dividend rights", "zh": "派息权利购买截止日", "ja": "配当権利獲得の買付期限"}
        }
    }

    def __init__(self):
        self.events = []
    
    def get_calendar(self, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    tickers: Optional[List[str]] = None,
                    lang: str = "ko") -> Dict[str, Any]:
        """지정된 기간의 고밀도 이벤트 캘린더 생성"""
        if start_date is None:
            start = datetime.now()
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date is None:
            end = start + timedelta(days=90)
        else:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        logger.info(f"Generating calendar: {start.date()} ~ {end.date()} (Lang: {lang})")
        
        all_events = []
        all_events.extend(self._get_fomc_events(start, end, lang))
        all_events.extend(self._get_economic_indicators(start, end, lang))
        all_events.extend(self._get_professional_events(start, end, lang))
        
        if tickers:
            for ticker in tickers:
                all_events.extend(self._get_stock_events(ticker, start, end, lang))
        
        all_events.sort(key=lambda x: (x['date'], x['time']))
        
        summary = self._generate_summary(all_events, start, end)
        
        return {
            "period": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")},
            "events": all_events,
            "summary": summary,
            "total_events": len(all_events)
        }
    
    def _get_fomc_events(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """FOMC 회의 일정"""
        events = []
        t = self.TRANS["FOMC"]
        schedules = []
        if start.year <= 2024 <= end.year: schedules.extend(self.FOMC_SCHEDULE_2024)
        if start.year <= 2025 <= end.year: schedules.extend(self.FOMC_SCHEDULE_2025)
        if start.year <= 2026 <= end.year: schedules.extend(self.FOMC_SCHEDULE_2026)
        
        for meeting in schedules:
            m_dt_ny = datetime.strptime(f"{meeting['date']} 14:00:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=self.TZ_NY)
            m_dt_kst = m_dt_ny.astimezone(self.TZ_KST)
            if start <= m_dt_kst.replace(tzinfo=None) <= end:
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
                    "scenarios": self._get_scenario_analysis("FOMC")
                })
        return events
    
    def _get_economic_indicators(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """주요 경제 지표 발표 일정 (US, KR, EU, JP, CN)"""
        events = []
        
        def add_item(dt_raw, tz, country, type_key, importance, category, scenarios_key):
            dt_with_tz = dt_raw.replace(tzinfo=tz)
            dt_kst = dt_with_tz.astimezone(self.TZ_KST)
            check_date = dt_kst.replace(tzinfo=None)
            
            if start <= check_date <= end:
                t_info = self.TRANS.get(type_key, {})
                events.append({
                    "date": dt_kst.strftime("%Y-%m-%d"),
                    "time": dt_kst.strftime("%H:%M"),
                    "datetime": dt_kst.isoformat(),
                    "country": country,
                    "type": type_key,
                    "title": t_info.get("title", {}).get(lang, type_key),
                    "description": t_info.get("desc", {}).get(lang, ""),
                    "importance": importance,
                    "impact": t_info.get("impact", {}).get(lang, ""),
                    "previous": "이전값 확인",
                    "forecast": "예상치 확인",
                    "actual": "-",
                    "category": category,
                    "scenarios": self._get_scenario_analysis(scenarios_key)
                })

        # 월간 반복 지표
        curr = start.replace(day=1)
        while curr <= end:
            # US Indicators
            add_item(curr.replace(day=1, hour=10, minute=0), self.TZ_NY, "US", "PMI", "high", "macro", "GDP")
            add_item(curr.replace(day=12, hour=8, minute=30), self.TZ_NY, "US", "CPI", "critical", "inflation", "CPI")
            add_item(curr.replace(day=14, hour=8, minute=30), self.TZ_NY, "US", "PPI", "high", "inflation", "PPI")
            add_item(curr.replace(day=15, hour=10, minute=0), self.TZ_NY, "US", "Sentiment", "medium", "consumption", "GDP")
            add_item(curr.replace(day=16, hour=8, minute=30), self.TZ_NY, "US", "Retail Sales", "high", "consumption", "Retail")
            
            # Global Indicators
            add_item(curr.replace(day=2, hour=13, minute=45), self.TZ_LDN, "EU", "ECB", "critical", "policy", "CPI")
            add_item(curr.replace(day=20, hour=11, minute=00), self.TZ_TKY, "JP", "BOJ", "critical", "policy", "CPI")
            add_item(curr.replace(day=25, hour=10, minute=0), self.TZ_KST, "KR", "BOK", "high", "policy", "CPI")
            
            # Month Increment
            if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
            else: curr = curr.replace(month=curr.month+1)

        # 주간 및 특정 주기 지표 (Thursday, Friday)
        curr_d = start
        while curr_d <= end:
            if curr_d.weekday() == 3: # Thursday
                add_item(curr_d.replace(hour=8, minute=30), self.TZ_NY, "US", "Claims", "medium", "labor", "NFP")
            curr_d += timedelta(days=1)

        # NFP (First Friday)
        curr_f = start.replace(day=1)
        while curr_f <= end:
            first_friday = curr_f
            while first_friday.weekday() != 4: first_friday += timedelta(days=1)
            add_item(first_friday.replace(hour=8, minute=30), self.TZ_NY, "US", "NFP", "critical", "labor", "NFP")
            if curr_f.month == 12: curr_f = curr_f.replace(year=curr_f.year+1, month=1)
            else: curr_f = curr_f.replace(month=curr_f.month+1)

        return events

    def _get_professional_events(self, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """연준 위원 연설 및 국채 입찰 (Professional Data)"""
        events = []
        t_sp = self.TRANS["Speech"]
        t_au = self.TRANS["Auction"]
        
        # 1. 미 재무부 국채 입찰 (Treasury Auctions) - 매월 정기적
        # 2년물(매월 말), 5년물(매월 말), 10년물(매월 중순)
        curr = start.replace(day=1)
        while curr <= end:
            # 10 Year Note (Approx 12th)
            d10 = curr.replace(day=12, hour=13, minute=0)
            if start <= d10 <= end:
                events.append(self._create_auction_event(d10, "10Y", lang))
            
            # 2 Year Note (Approx 26th)
            d2 = curr.replace(day=26, hour=13, minute=0)
            if start <= d2 <= end:
                events.append(self._create_auction_event(d2, "2Y", lang))
            
            if curr.month == 12: curr = curr.replace(year=curr.year+1, month=1)
            else: curr = curr.replace(month=curr.month+1)

        # 2. 연준 위원 연설 (Fed Speeches) - 블랙아웃 기간 외 빈번함
        # 동적 수집이 이상적이나, 여기서는 주요 위원 위주로 시뮬레이션
        speakers = ["Powell", "Williams", "Cook", "Waller"]
        curr_s = start
        while curr_s <= end:
            # 화/수/목 위주로 연설 배치
            if curr_s.weekday() in [1, 2, 3] and curr_s.day % 4 == 0:
                name = speakers[curr_s.day % len(speakers)]
                dt_ny = curr_s.replace(hour=10, minute=0, tzinfo=self.TZ_NY)
                dt_kst = dt_ny.astimezone(self.TZ_KST)
                events.append({
                    "date": dt_kst.strftime("%Y-%m-%d"),
                    "time": dt_kst.strftime("%H:%M"),
                    "datetime": dt_kst.isoformat(),
                    "country": "US",
                    "type": "Speech",
                    "title": t_sp["title_fmt"].get(lang, t_sp["title_fmt"]["en"]).format(name=name),
                    "description": t_sp["desc"].get(lang, t_sp["desc"]["en"]),
                    "importance": "high",
                    "impact": t_sp["impact"].get(lang, t_sp["impact"]["en"]),
                    "previous": "-", "forecast": "-", "actual": "-",
                    "category": "policy",
                    "scenarios": self._get_scenario_analysis("FOMC")
                })
            curr_s += timedelta(days=1)
            
        return events

    def _create_auction_event(self, dt_ny_raw, term, lang):
        t = self.TRANS["Auction"]
        dt_ny = dt_ny_raw.replace(tzinfo=self.TZ_NY)
        dt_kst = dt_ny.astimezone(self.TZ_KST)
        return {
            "date": dt_kst.strftime("%Y-%m-%d"),
            "time": dt_kst.strftime("%H:%M"),
            "datetime": dt_kst.isoformat(),
            "country": "US",
            "type": "Auction",
            "title": t["title_fmt"].get(lang, t["title_fmt"]["en"]).format(term=term),
            "description": t["desc"].get(lang, t["desc"]["en"]),
            "importance": "medium",
            "impact": t["impact"].get(lang, t["impact"]["en"]),
            "previous": "4.25%", "forecast": "-", "actual": "-",
            "category": "debt",
            "scenarios": {"high": "응찰률 저조 → 금리 상승 압력", "low": "응찰률 호조 → 금리 안정"}
        }

    def _get_scenario_analysis(self, event_type: str) -> Dict[str, str]:
        """이벤트 결과에 따른 시장 영향 시나리오"""
        scenarios = {
            "CPI": {
                "high": "🔴 예상 상회: 인플레 우려 → 금리 인하 지연 → 주식/채권 약세, 달러 강세",
                "low": "🟢 예상 하회: 인플레 둔화 → 금리 인하 기대 → 성장주/기술주 강세, 달러 약세"
            },
            "PPI": {
                "high": "🔴 예상 상회: 기업 비용 증가 → 향후 소비자물가 전가 우려 → 시장 경계감",
                "low": "🟢 예상 하회: 원가 부담 완화 → 마진 개선 기대 → 긍정적"
            },
            "NFP": {
                "high": "🟡 예상 상회: 고용 과열 → 긴축 우려 → 주식 단기 약세 (경기 침체 우려는 완화)",
                "low": "🔴 예상 하회: 고용 둔화 → 경기 침체 공포 → 안전자산 선호, 주식 약세"
            },
            "GDP": {
                "high": "🟢 예상 상회: 견조한 경제 성장 → 경기 민감주/가치주 강세",
                "low": "🔴 예상 하회: 경기 둔화 우려 → 방어주 선호, 금리 인하 압력 증가"
            },
            "FOMC": {
                "hawkish": "🦅 매파적(Hawkish): 금리 인상 시사 → 성장주 타격, 금융주 일부 수혜",
                "dovish": "🕊️ 비둘기파적(Dovish): 금리 인하 시사 → 전반적 자산 시장 랠리"
            },
            "Earnings": {
                "beat": "🚀 어닝 서프라이즈: 실적/가이던스 호조 → 주가 급등 가능성",
                "miss": "📉 어닝 쇼크: 실적 부진 → 주가 급급 및 밸류에이션 재평가"
            },
            "Retail": {
                "high": "🟢 예상 상회: 강력한 소비 → 경기 침체 우려 해소 → 전체 시장 긍정적",
                "low": "🔴 예상 하회: 소비 위축 → 경기 하강 신호 → 필수소비재/유틸리티 방어주 선호"
            }
        }
        return scenarios.get(event_type, {"high": "상회 시 변동성 확대", "low": "하회 시 시장 주시"})

    def _get_stock_events(self, ticker: str, start: datetime, end: datetime, lang: str = "ko") -> List[Dict]:
        """종목별 실적 및 배당 (yfinance)"""
        events = []
        try:
            stock = yf.Ticker(ticker)
            t_earn = self.TRANS["Earnings"]
            t_div = self.TRANS["Dividend"]
            
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
                                "title": t_earn["title_fmt"].get(lang, ticker).format(ticker=ticker),
                                "description": t_earn["desc"].get(lang, ""), "importance": "high",
                                "impact": t_earn["impact_fmt"].get(lang, ticker).format(ticker=ticker),
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
                        "title": t_div["title_fmt"].get(lang, ticker).format(ticker=ticker),
                        "description": t_div["desc_fmt"].get(lang, amt).format(amount=amt),
                        "importance": "medium", "impact": t_div["impact"].get(lang, ""),
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
            
            e_date = datetime.strptime(e['date'], "%Y-%m-%d")
            if imp in ['critical', 'high'] and e_date >= now:
                summary['upcoming_critical'].append({"date": e['date'], "title": e['title'], "days": (e_date-now).days})
        return summary

    def format_for_ui(self, data: Dict) -> str:
        """UI 표시용 요약 텍스트"""
        lines = [f"📅 경제 캘린더 ({data['period']['start']} ~ {data['period']['end']})", f"총 {data['total_events']}개의 일정이 발견되었습니다.\n"]
        if data['summary']['upcoming_critical']:
            lines.append("⚠️ 주요 고위험 일정:")
            for e in data['summary']['upcoming_critical'][:5]:
                lines.append(f"  • {e['date']} (D-{e['days']}): {e['title']}")
        return "\n".join(lines)

if __name__ == "__main__":
    calendar = EventCalendar()
    res = calendar.get_calendar()
    print(calendar.format_for_ui(res))
