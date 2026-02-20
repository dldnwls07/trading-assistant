# FOMC 회의 일정 (현지시간 기준)
FOMC_SCHEDULES = {
    2024: [
        {"date": "2024-01-31", "desc": "FOMC Meeting"},
        {"date": "2024-03-20", "desc": "FOMC Meeting"},
        {"date": "2024-05-01", "desc": "FOMC Meeting"},
        {"date": "2024-06-12", "desc": "FOMC Meeting"},
        {"date": "2024-07-31", "desc": "FOMC Meeting"},
        {"date": "2024-09-18", "desc": "FOMC Meeting"},
        {"date": "2024-11-07", "desc": "FOMC Meeting"},
        {"date": "2024-12-18", "desc": "FOMC Meeting"}
    ],
    2025: [
        {"date": "2025-01-29", "desc": "FOMC Meeting"},
        {"date": "2025-03-19", "desc": "FOMC Meeting"},
        {"date": "2025-05-07", "desc": "FOMC Meeting"},
        {"date": "2025-06-18", "desc": "FOMC Meeting"},
        {"date": "2025-07-30", "desc": "FOMC Meeting"},
        {"date": "2025-09-17", "desc": "FOMC Meeting"},
        {"date": "2025-10-29", "desc": "FOMC Meeting"},
        {"date": "2025-12-10", "desc": "FOMC Meeting"}
    ],
    2026: [
        {"date": "2026-01-28", "desc": "FOMC Meeting"},
        {"date": "2026-03-18", "desc": "FOMC Meeting"},
        {"date": "2026-05-06", "desc": "FOMC Meeting"},
        {"date": "2026-06-17", "desc": "FOMC Meeting"},
        {"date": "2026-07-29", "desc": "FOMC Meeting"},
        {"date": "2026-09-16", "desc": "FOMC Meeting"},
        {"date": "2026-10-28", "desc": "FOMC Meeting"},
        {"date": "2026-12-09", "desc": "FOMC Meeting"}
    ]
}

# 캘린더 번역 및 메타데이터
CALENDAR_TRANS = {
    "FOMC": {
        "title": {"ko": "미 연준(Fed) 금리 결정 (FOMC)", "en": "Fed Interest Rate Decision (FOMC)"},
        "desc": {"ko": "미국 중앙은행의 기준금리 결정 및 정책 성명서 발표", "en": "Federal Reserve interest rate decision and policy statement"},
        "impact": {"ko": "글로벌 시장의 유동성과 금리 방향성을 결정하는 가장 중요한 이벤트", "en": "Most critical event for global liquidity and rate direction"}
    },
    "CPI": {
        "title": {"ko": "미국 소비자물가지수 (CPI)", "en": "US Consumer Price Index (CPI)"},
        "desc": {"ko": "인플레이션 수준을 측정하는 핵심 지표", "en": "Core indicator for measuring inflation levels"},
        "impact": {"ko": "금리 인상/인하 경로를 결정짓는 핵심 데이터", "en": "Key data for interest rate path decisions"}
    },
    "NFP": {
        "title": {"ko": "미국 비농업 고용지수 (NFP)", "en": "US Non-Farm Payrolls (NFP)"},
        "desc": {"ko": "미국 노동 시장의 건강 상태를 나타내는 지표", "en": "Indicator of US labor market health"},
        "impact": {"ko": "경기 활성화 및 소비 여력을 확인하는 주요 지표", "en": "Main indicator for economic activity and consumption power"}
    }
}

# AI 시나리오 템플릿
SCENARIO_TEMPLATES = {
    "FOMC": {
        "high": {"desc": "금리 동결 또는 인상 (매파적)", "impact": "negative", "reason": "고금리 유지로 인한 유동성 축소 우려"},
        "low": {"desc": "금리 인하 (비둘기파적)", "impact": "positive", "reason": "유동성 공급 및 차입 비용 감소 기대"},
        "con": {"desc": "시장 예상 부합", "impact": "neutral", "reason": "이미 반영된 재료로 변동성 제한적"}
    }
}

# 검증된 수동 오버라이드 (데이터가 누락되거나 틀린 경우)
VERIFIED_OVERRIDES = [
    {"date": "2026-02-12", "time": "22:30", "title": "미국 소비자물가지수 (CPI)", "country": "US", "importance": "critical", "category": "inflation", "forecast": "3.1%", "previous": "3.2%"},
    {"date": "2026-02-13", "time": "22:30", "title": "미국 생산자물가지수 (PPI)", "country": "US", "importance": "high", "category": "inflation", "forecast": "2.4%", "previous": "2.5%"},
    {"date": "2026-02-24", "time": "22:30", "title": "미국 소비자신뢰지수", "country": "US", "importance": "medium", "category": "consumption", "forecast": "108.5", "previous": "107.2"},
    {"date": "2026-03-06", "time": "22:30", "title": "미국 비농업 고용지수 (NFP)", "country": "US", "importance": "critical", "category": "labor", "forecast": "185K", "previous": "210K"},
    {"date": "2026-03-12", "time": "22:30", "title": "미국 소비자물가지수 (CPI)", "country": "US", "importance": "critical", "category": "inflation", "forecast": "3.0%", "previous": "3.1%"},
    {"date": "2026-03-18", "time": "03:00", "title": "FOMC 금리 결정", "country": "US", "importance": "critical", "category": "policy", "forecast": "5.25%", "previous": "5.50%"},
]
