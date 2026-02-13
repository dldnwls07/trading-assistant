# 📋 RSI 0.0 오류 해결 및 분석 품질 최적화 계획

## 1. 문제 분석
* **RSI 계산 로직의 한계:** 현재 `rolling().mean()` (SMA 방식)을 사용하여 RSI를 계산하고 있음. 데이터가 적거나 변동이 없을 때 `0.0` 또는 `NaN`이 발생하기 쉬운 구조임.
* **데이터 수집의 부정확성:** `MultiTimeframeAnalyzer`가 한국 주식에 부적합한 `yfinance`를 직접 사용하고 있어, 장외 시간이나 거래량이 적은 종목에서 주가가 동일하게 유지되어 RSI가 오류를 일으킴.
* **유효성 검사 부재:** RSI가 `NaN`일 경우 AI 리포트 생성 시 기본값 `0`으로 처리되어 오해를 불러일으킴.

## 2. 작업 상세
### 2.1 TechnicalAnalyzer 개선 (`src/agents/analyst.py`)
* [ ] RSI 계산 방식을 표준인 **Wilder's Smoothing (EMA)** 방식으로 변경.
* [ ] 주가 변동이 전혀 없을 경우 RSI를 `50.0` (중립)으로 반환하도록 예외 처리 추가.
* [ ] 0 나누기 방지 로직 강화.

### 2.2 Advanced Technical Indicators 개선 (`src/utils/advanced_indicators.py`)
* [ ] `AdvancedIndicators._rsi` 메서드에 동일한 개선 로직 적용.

### 2.3 데이터 수집 최적화 (`src/agents/multi_timeframe.py`)
* [ ] `yfinance` 직접 호출을 `MarketDataCollector` 사용으로 변경.
* [ ] 한국 주식(`*.KS`, `*.KQ`)의 경우 `FinanceDataReader`를 통한 정확한 데이터 수집 보장.

### 2.4 AI 분석기 보정 (`src/agents/ai_analyzer.py`)
* [ ] RSI 데이터가 유효하지 않을 때 AI가 임의로 `0.0`을 출력하지 않도록 방어 코드 추가.

## 3. 예상 결과
* 종목에 관계없이 실제 시장 상황을 반영하는 정확한 RSI 값 출력.
* 한국 주식 분석 시 데이터 단절 및 0.0 출력 현상 해결.
* 분석 신뢰도 향상.
