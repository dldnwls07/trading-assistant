# 🛠️ 배포 및 백엔드 오류 수정 계획

현재 보고된 여러 오류(yfinance 세션 오류, 스크리너 메서드 누락, API 비동기 호출 누락 등)를 해결하기 위한 작업 계획입니다.

## 1. 분석된 주요 문제점
- **yfinance 오류:** Yahoo Finance API 정책 변경으로 인해 `requests.Session`을 직접 전달할 때 오류가 발생합니다. (curl_cffi 권장 혹은 세션 미사용 권장)
- **Screener 메서드 누락:** `StockScreener` 클래스에서 `get_market_tickers`, `_apply_style_filter`, `_generate_reason` 메서드가 코드 편집 과정에서 누락되었습니다.
- **API 비동기 호출 누락:** `src/api/server.py`에서 `async`로 정의된 스크리너 메서드들을 `await` 없이 호출하고 있어 런타임 에러가 발생합니다.
- **CORS 설정:** 배포 환경(Render)의 도메인이 CORS 허용 목록에 누락되어 있을 가능성이 있습니다.

## 2. 상세 작업 단계

### 2.1 데이터 수집기(`src/data/collector.py`) 수정
- `yfinance.Ticker` 호출 시 브라우저 차단 회피를 위해 세션 설정을 제거하거나 `yfinance` 기본 핸들러에 맡기도록 수정합니다.

### 2.2 종목 스크리너(`src/agents/screener.py`) 복구
- 누락된 `get_market_tickers` (시장의 주요 티커 반환), `_apply_style_filter` (스타일별 가중치 적용), `_generate_reason` (추천 이유 생성) 메서드를 다시 구현합니다.

### 2.3 API 서버(`src/api/server.py`) 수정
- `/api/screener/recommendations` 및 `/api/screener/top-movers` 엔드포인트에서 스크리너 메서드 호출 시 `await`를 추가합니다.
- Render 배포 도메인을 CORS `origins` 목록에 추가합니다.

### 2.4 오류 검증 및 배포 준비
- 수정된 코드의 구문 오류를 확인하고, 로컬 환경에서 간단한 API 호출 테스트를 수행합니다.

## 3. 예상 결과
- `NVDA` 등 미국 주식의 데이터 수집이 정상화됩니다.
- 자율 트레이딩 루틴에서 발생하는 `'StockScreener' object has no attribute 'get_market_tickers'` 에러가 해결됩니다.
- 프론트엔드에서 스크리너 API 호출 시 발생하는 400 Bad Request 및 데이터 누락 문제가 해결됩니다.

---
**작업을 시작할까요?**
