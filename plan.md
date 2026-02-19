# 📋 분석 데이터 복원 계획

## 🎯 목표
프론트엔드가 기대하는 분석 데이터를 백엔드에서 올바르게 생성하여 전달되도록 복원

## 📊 현재 상태: 프론트엔드가 참조하지만 백엔드가 제공하지 않는 데이터

### 1. `AnalysisInsights` 컴포넌트 (시간 프레임별 전략)
- `{timeframe}_term.recommendation` — 단/중/장기별 추천 전략
- `{timeframe}_term.focus_areas` — 기술적 주요 관찰점
- `{timeframe}_term.holding_period` — 추천 보유 기간

### 2. `TradingSetup` 컴포넌트 (전략 앙상블)
- `consensus.global_ensemble` — 앙상블 점수/등급/추천 (StrategyEnsemble 사용)
- `medium_term.full_analysis.ml_forecast` — ML 5D 예측 (현재 `ml_prediction`에만 있음)
- `medium_term.full_analysis.backtest` — 백테스트 결과

### 3. `StrategicSignals` 컴포넌트
- `entry_points` — 진입가/손절가/익절가

### 4. `StrategyCard` 컴포넌트
- `market_regime` — 현재 마켓 레짐
- `strategy_checklist` — 전략 체크리스트

---

## 🔧 수정 파일 및 작업 순서

### Step 1: `multi_timeframe.py` — 시간 프레임별 전략 필드 추가
- `_analyze_timeframe()` 반환값에 `recommendation`, `focus_areas`, `holding_period` 추가
- raw_indicators에서 RSI, MACD, SMA 등을 읽어 규칙 기반으로 생성
- 이 필드들은 LLM 호출 없이 계산 가능 (빠르고 안정적)

### Step 2: `integration_service.py` — ML/앙상블/진입가 통합
- `ml_prediction` 결과를 `medium_term.full_analysis.ml_forecast`에도 매핑
- `StrategyEnsemble.calculate_ensemble()` 호출하여 `consensus.global_ensemble` 생성
- `entry_points` 계산 (현재가 기반 ATR 활용)
- `market_regime` 계산 (ADX, 변동성 기반)
- `strategy_checklist` 생성

---

## ⚠️ 주의사항
- LLM 호출은 추가하지 않음 (할당량 절약)
- 모든 새 필드는 규칙 기반 또는 기존 엔진 활용
- 프론트엔드 수정 불필요 (이미 UI가 준비되어 있음)
