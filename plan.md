# 🚀 에이전트 엔진 v5.0 업그레이드 계획

## 🎯 3가지 핵심 개선

### 1. VIX 가중치 산식 (변동성 적응형 지표)
- **대상 파일**: `integration_service.py`, `multi_timeframe.py`
- **목표**: VIX(^VIX)를 실시간으로 수집하여, VIX > 22일 때 RSI 매수 임계값을 30으로 낮추고 매도 임계값을 80으로 높임
- **적용 위치**:
  - `integration_service._run_backtest()` — VIX 적응형 RSI 신호
  - `integration_service._build_strategy_checklist()` — VIX 경고 항목 추가
  - `integration_service._build_consensus()` — VIX 리스크 반영
  - `multi_timeframe._generate_timeframe_strategy()` — VIX 적응형 RSI 임계값

### 2. 상관관계 모듈 (Correlation)
- **대상 파일**: `integration_service.py`
- **목표**: 분석 종목과 나스닥(^IXIC)의 상관계수를 계산하여 '동반 하락' vs '개별 조정' 국면 구분
- **적용 위치**:
  - `integration_service._determine_market_regime()` — 상관계수 기반 레짐 세분화
  - `integration_service._build_consensus()` — 상관 리스크 반영

### 3. 거래량 컨퍼메이션 (Volume Confirmation)
- **대상 파일**: `pattern_detector.py`
- **목표**: 패턴 완성 시 거래량이 전일 대비 150% 이상이 아닌 경우 confidence를 50% 감점
- **적용 위치**:
  - `detect_all_patterns()` — 볼륨 검증 후처리 로직 추가

## 📋 작업 순서
1. `multi_timeframe.py` — VIX 데이터 수집 + 전략 생성 반영
2. `integration_service.py` — VIX + 상관관계 통합
3. `pattern_detector.py` — 거래량 컨퍼메이션
