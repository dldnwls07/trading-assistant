# 📚 AI 트레이딩 어시스턴트 사용자 가이드

## 목차
1. [시작하기](#시작하기)
2. [주요 기능](#주요-기능)
3. [사용 예시](#사용-예시)
4. [API 키 설정](#api-키-설정)
5. [문제 해결](#문제-해결)

---

## 시작하기

### 필수 요구사항
- Python 3.8 이상
- 인터넷 연결 (데이터 수집용)

### 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일을 편집하여 API 키를 설정하세요:

```env
# Hugging Face API (AI 분석 및 채팅)
HF_TOKEN="your_huggingface_token_here"

# FRED API (거시 경제 지표) - 선택사항
FRED_API_KEY="your_fred_api_key_here"
```

**API 키 발급:**
- **Hugging Face**: https://huggingface.co/settings/tokens (무료)
- **FRED**: https://fred.stlouisfed.org/docs/api/api_key.html (무료)

---

## 주요 기능

### 1. 📊 고급 차트 패턴 감지

**30개 이상의 차트 패턴 자동 감지** + Bulkowski 통계 기반 신뢰도 평가

```python
from src.agents.pattern_detector import AdvancedPatternDetector
import yfinance as yf

detector = AdvancedPatternDetector()
data = yf.Ticker("AAPL").history(period="6mo")
patterns = detector.detect_all_patterns(data)

for pattern in patterns[:5]:
    print(f"{pattern['name']}: 신뢰도 {pattern['reliability']}/5.0")
```

**지원 패턴:**
- **반전 패턴**: Head & Shoulders, Double/Triple Top/Bottom, Rounding Bottom 등
- **지속 패턴**: Triangle, Wedge, Flag, Pennant, Rectangle
- **캔들 패턴**: Hammer, Engulfing, Morning/Evening Star 등

---

### 2. ⏱️ 다중 시간 프레임 분석

**단기/중기/장기 각각의 독립적 신호 및 매수/매도 타점 제공**

```python
from src.agents.multi_timeframe import MultiTimeframeAnalyzer

analyzer = MultiTimeframeAnalyzer()
result = analyzer.analyze_all_timeframes("AAPL")

# 단기 (데이 트레이딩)
print(f"단기 점수: {result['short_term']['score']}")
print(f"단기 매수 타점: {result['short_term']['entry_points']['buy_zone']}")

# 중기 (스윙 트레이딩)
print(f"중기 피보나치 레벨: {result['medium_term']['entry_points']['fibonacci_levels']}")

# 장기 (포지션 트레이딩)
print(f"장기 목표가: {result['long_term']['entry_points']['take_profit']}")

# 종합 컨센서스
print(f"컨센서스: {result['consensus']['consensus']}")
```

**시간 프레임별 특징:**
- **단기 (1~5일)**: 1시간봉, ATR 기반 손절/익절, 리스크/보상 1.33
- **중기 (1~3개월)**: 일봉, 피보나치 되돌림, 리스크/보상 2.0
- **장기 (6개월~1년)**: 주봉, 200일선 기준, 리스크/보상 3.0

---

### 3. 🎯 AI 추천 종목 시스템

**투자 스타일별 맞춤 종목 추천**

```python
from src.agents.screener import StockScreener

screener = StockScreener()

# S&P 500 종목 스크리닝
sp500_tickers = screener.get_sp500_tickers()

# 공격적 성장형 투자자를 위한 추천
recommendations = screener.screen_stocks(
    tickers=sp500_tickers[:50],  # 상위 50개만
    investor_style="aggressive_growth",
    top_n=10
)

for rec in recommendations:
    print(f"{rec['ticker']}: 점수 {rec['score']}, {rec['reason']}")
```

**지원 투자 스타일:**
- `aggressive_growth`: 공격적 성장형
- `dividend`: 안정적 배당형
- `value`: 가치 투자형
- `momentum`: 모멘텀 트레이딩형
- `balanced`: 균형 포트폴리오형

---

### 4. 👤 투자 스타일 프로파일링

**설문 기반 자동 스타일 분류**

```python
from src.agents.profiler import InvestorProfiler

profiler = InvestorProfiler()

# 설문 응답
survey = {
    "risk_tolerance": 4,        # 1~5 (1=보수적, 5=공격적)
    "time_horizon": "short",    # short/medium/long
    "loss_tolerance": 4,        # 1~5
    "investment_goal": "growth", # growth/income/preservation/balanced
    "trading_frequency": "weekly" # daily/weekly/monthly/rarely
}

style = profiler.create_profile_from_survey(survey)
print(f"당신의 투자 스타일: {profiler.STYLES[style]['name']}")
```

---

### 5. 💼 포트폴리오 AI 평가

**보유 종목 분석 및 리밸런싱 제안**

```python
from src.agents.portfolio_analyzer import PortfolioAnalyzer

analyzer = PortfolioAnalyzer()

# 보유 종목 입력
holdings = [
    {"ticker": "AAPL", "shares": 10, "avg_price": 150},
    {"ticker": "MSFT", "shares": 5, "avg_price": 300},
    {"ticker": "GOOGL", "shares": 3, "avg_price": 2500}
]

result = analyzer.analyze_portfolio(holdings)

print(f"포트폴리오 점수: {result['portfolio_score']}/100")
print(f"분산도: {result['diversification']['grade']}")
print(f"리스크 밸런스: {result['risk_balance']['message']}")

# 리밸런싱 제안
for suggestion in result['rebalancing']['sell']:
    print(f"매도 추천: {suggestion['ticker']} - {suggestion['reason']}")
```

**평가 항목:**
- 종합 점수 (가중 평균)
- 분산도 (HHI 지수)
- 리스크 밸런스
- 투자 스타일 일치도

---

### 6. 📅 경제 이벤트 캘린더

**FOMC, CPI, 실적 발표 등 주요 일정 추적**

```python
from src.agents.event_calendar import EventCalendar

calendar = EventCalendar()

# 향후 3개월 캘린더 (AAPL 포함)
result = calendar.get_calendar(tickers=["AAPL", "MSFT"])

print(calendar.format_for_ui(result))

# 다음 중요 이벤트
next_event = calendar.get_next_important_event("AAPL")
if next_event:
    print(f"다음 중요 일정: {next_event['date']} - {next_event['title']}")
```

**포함 이벤트:**
- FOMC 회의 (연 8회)
- CPI 발표 (매월)
- 고용지표 NFP (매월)
- GDP 발표 (분기별)
- 기업 실적 발표
- 배당락일

---

### 7. 💬 AI 채팅 어시스턴트

**대화형 투자 상담**

```python
from src.agents.chat_assistant import ChatAssistant

assistant = ChatAssistant()

# 컨텍스트 제공
context = {
    "ticker": "AAPL",
    "current_price": 175.50,
    "analysis": {"final_score": 72, "signal": "매수 권고"},
    "patterns": [{"name": "Double Bottom", "reliability": 4.2}]
}

# 대화
response = assistant.chat("AAPL 지금 사도 될까요?", context)
print(response)

# 추천 질문
suggestions = assistant.suggest_questions(context)
for q in suggestions:
    print(f"- {q}")
```

**주요 기능:**
- Hugging Face LLM 기반 응답
- 대화 히스토리 유지
- 컨텍스트 기반 맞춤 답변
- 폴백 모드 (LLM 없이도 동작)

---

### 8. 📈 FRED API 거시 경제 분석

**무료 거시 경제 지표 수집 및 분석**

```python
from src.data.fred_provider import FREDDataProvider

fred = FREDDataProvider()

# 거시 경제 스냅샷
snapshot = fred.get_macro_snapshot()
print(f"연준 기준금리: {snapshot.get('fed_funds_rate')}%")
print(f"인플레이션: {snapshot.get('cpi_yoy')}%")
print(f"실업률: {snapshot.get('unemployment_rate')}%")

# 종합 분석
analysis = fred.analyze_macro_conditions()
print(f"거시 점수: {analysis['score']}/100 ({analysis['grade']})")
print(f"추천: {analysis['recommendation']}")
```

**제공 지표:**
- 연준 기준금리
- CPI (인플레이션)
- 실업률
- GDP 성장률
- 10년물/2년물 국채 수익률
- VIX (변동성 지수)

---

## 사용 예시

### 종합 분석 워크플로우

```python
from src.agents.multi_timeframe import MultiTimeframeAnalyzer
from src.agents.chat_assistant import ChatAssistant
from src.data.fred_provider import FREDDataProvider

# 1. 거시 환경 확인
fred = FREDDataProvider()
macro = fred.analyze_macro_conditions()
print(f"거시 환경: {macro['grade']} ({macro['score']}점)")

# 2. 종목 다중 시간 프레임 분석
analyzer = MultiTimeframeAnalyzer()
result = analyzer.analyze_all_timeframes("AAPL")

print(f"\n=== AAPL 분석 ===")
print(f"단기: {result['short_term']['signal']}")
print(f"중기: {result['medium_term']['signal']}")
print(f"장기: {result['long_term']['signal']}")
print(f"컨센서스: {result['consensus']['consensus']}")

# 3. 감지된 패턴 확인
print(f"\n감지된 패턴: {len(result['all_patterns'])}개")
for p in result['all_patterns'][:3]:
    print(f"- {p['name']} (신뢰도: {p['reliability']}/5.0)")

# 4. AI 상담
assistant = ChatAssistant()
context = {
    "ticker": "AAPL",
    "analysis": result['medium_term']['full_analysis'],
    "patterns": result['all_patterns']
}

response = assistant.chat("종합적으로 판단했을 때 어떤가요?", context)
print(f"\nAI 조언: {response}")
```

---

## API 키 설정

### Hugging Face Token

1. https://huggingface.co/settings/tokens 접속
2. "New token" 클릭
3. Read 권한 선택
4. `.env` 파일의 `HF_TOKEN`에 입력

### FRED API Key

1. https://fred.stlouisfed.org/ 회원가입
2. https://fred.stlouisfed.org/docs/api/api_key.html 에서 API 키 발급
3. `.env` 파일의 `FRED_API_KEY`에 입력

---

## 문제 해결

### Q: "HF_TOKEN이 설정되지 않았습니다" 경고가 뜹니다.
**A:** `.env` 파일에 Hugging Face API 토큰을 설정하세요. 토큰 없이도 기본 기능은 작동하지만, AI 리포트 생성 및 채팅 기능이 제한됩니다.

### Q: "FRED_API_KEY가 필요합니다" 오류가 발생합니다.
**A:** FRED API는 선택사항입니다. API 키 없이도 기본 거시 분석은 가능하지만, 실시간 경제 지표는 제공되지 않습니다.

### Q: 패턴 감지가 너무 느립니다.
**A:** 데이터 기간을 줄이거나 (`period="3mo"`) 분석할 종목 수를 제한하세요.

### Q: 포트폴리오 분석 시 일부 종목이 실패합니다.
**A:** yfinance API의 일시적 오류일 수 있습니다. 잠시 후 다시 시도하거나, 해당 종목을 제외하고 분석하세요.

### Q: 다중 시간 프레임 분석에서 데이터가 부족하다고 나옵니다.
**A:** 신규 상장 종목이거나 거래량이 적은 종목일 수 있습니다. 최소 6개월 이상의 거래 이력이 있는 종목을 선택하세요.

---

## 라이선스

이 프로젝트는 개인 투자 분석 목적으로 제작되었습니다. 투자 권유가 아닌 정보 제공 목적이며, 모든 투자 결정은 사용자 본인의 책임입니다.

---

## 기여

버그 리포트 및 기능 제안은 GitHub Issues를 통해 제출해 주세요.

**Happy Trading! 📈**
