# Calendar API Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 경제 캘린더 및 기업 실적 캘린더가 제대로 작동하지 않고 데모 데이터를 표시하는 근본 원인을 분석하고, 이를 온전히 해결하기 위한 구현 계획을 수립합니다.

**Architecture:** 
현재 캘린더가 작동하지 않는 주된 이유는 백엔드(FastAPI)의 `calendar_fetchers.py`에서 외부 데이터를 가져올 때 발생하는 오류들이 조용히 무시(`try-except`에서 빈 리스트 `[]` 반환)되고 있기 때문입니다. 이로 인해 프론트엔드는 "데이터 없음"으로 인식하고 하드코딩된 데모 시나리오를 렌더링하고 있습니다. 주요 원인은 다음과 같습니다:
1. **Trading Economics 스크래핑 차단:** 단순 봇 헤더(`requests.get`) 사용으로 인해 Cloudflare 등 보안에 막혀 403 에러가 발생하거나 HTML 파싱 구조가 변경되어 거시 경제 데이터 수집에 실패합니다.
2. **yfinance 한국 실적 발표일 누락:** 네이버 시총 상위 종목을 가져온 뒤 `yfinance` 캘린더 API를 호출하지만, 한국 주식은 `yfinance`에 미래 실적 발표일(Earnings Date)이 제대로 등록되어 있지 않습니다.
3. **Finnhub / FRED 데이터 한계:** FRED API는 미래 일정이 아닌 과거 최근 업데이트 일자만 가져오며, `.env` 내의 `FINNHUB_API_KEY` 환경 변수 문자열 파싱 문제(공백 등)나 API 호출 한도로 인해 미국 실적 데이터도 누락될 수 있습니다.

이러한 문제를 우회 스크래퍼 도입, 에러 로깅 강화, 그리고 한국 주식용 별도 공시(DART/Naver) 스크래퍼 연결을 통해 해결합니다.

**Tech Stack:** Python, FastAPI, BeautifulSoup, yfinance, requests

---

### Task 1: Fetcher 모듈 에러 로깅 강화 및 예외 처리 수정

**Files:**
- Modify: `src/agents/calendar_fetchers.py`

**Step 1: Write the failing test**

```python
def test_fetcher_error_logging():
    # 예외 발생 시 빈 리스트가 아닌 예외 내역이 로그로 남는지 확인하는 테스트
    pass
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_calendar.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/agents/calendar_fetchers.py
# BaseFetcher 및 각 Fetcher 클래스의 except 블록에 `logger.error(...)` 구체화
# status_code가 200이 아닐 경우의 처리 로직 명시적 추가
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_calendar.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/agents/calendar_fetchers.py
git commit -m "fix: 캘린더 수집기 에러 로깅 강화 및 조용한 실패 방지"
```

### Task 2: Trading Economics 크롤링 안정화

**Files:**
- Modify: `src/agents/calendar_fetchers.py`

**Step 1: Write the failing test**

```python
def test_te_scraper_data_exist():
    # Trading Economics에서 데이터가 정상적으로 들어오는지 확인
    # assert len(events) > 0
    pass
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_calendar.py -v`
Expected: FAIL (현재 0 반환)

**Step 3: Write minimal implementation**

```python
# src/agents/calendar_fetchers.py의 TradingEconomicsScraper
# User-Agent, Accept, Referer 헤더 추가 및, 필요시 cloudscraper 패키지로 우회
# 테이블 HTML 파싱 구조(id='calendar' 또는 class 변경) 대응
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_calendar.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/agents/calendar_fetchers.py
git commit -m "fix: Trading Economics 스크래퍼 헤더 및 파싱 로직 업데이트"
```

### Task 3: 한국 기업 실적(Earnings) 수집 로직 개선

**Files:**
- Modify: `src/agents/calendar_fetchers.py`

**Step 1: Write the failing test**

```python
def test_kr_earnings_exist():
    # 삼성전자 등 한국 종목의 미래 실적일이 반환되는지 확인
    pass
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_calendar.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/agents/calendar_fetchers.py의 NaverEarningsScraper 의 _fetch_single_earnings
# yfinance 의존성을 낮추고, 네이버 금융이나 인베스팅닷컴 등의 실적 발표 일정 캘린더 API/HTML을 소스로 사용하도록 전면 개편
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_calendar.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/agents/calendar_fetchers.py
git commit -m "feat: 한국 주식 실적 수집 방식을 yfinance에서 대안 모듈로 교체"
```

### Task 4: Finnhub API Key 로드 점검 및 폴백 마련

**Files:**
- Modify: `src/agents/event_calendar.py`

**Step 1: Write the failing test**

```python
def test_finnhub_key_loads():
    # 환경변수에서 읽어온 키가 공백 없이 세팅되었는지 확인
    pass
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_calendar.py -v`

**Step 3: Write minimal implementation**

```python
# src/agents/event_calendar.py
finnhub_key = os.getenv("FINNHUB_API_KEY", "").strip()
# 만약 키가 없을 경우를 대비해 yfinance로 미국 주식 실적을 대체 검색하는 Fallback 로직 추가
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_calendar.py -v` 
Expected: PASS

**Step 5: Commit**

```bash
git add src/agents/event_calendar.py
git commit -m "fix: Finnhub API키 로드 시 공백 제거 및 미국 실적 yfinance 폴백 연동"
```

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-20-calendar-fixes.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
