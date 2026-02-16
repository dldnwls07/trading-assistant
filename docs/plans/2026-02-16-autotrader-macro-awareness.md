# AutoTrader: Macro-Aware 리스크 관리 고도화 실행 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**목표:** `AutoTrader`가 `EventCalendar`의 거시 경제 이벤트 데이터를 연동하여, 주요 지표 발표 전후로 매매 비중을 조절하고 리스크를 선제적으로 관리하는 '거시 인지형' 트레이딩 시스템을 구축합니다.

---

### Task 1: AutoTrader와 EventCalendar 연동 기초 설정
- **Files:** `src/agents/auto_trader.py`
- **Action:**
    - `AutoTrader.__init__`에서 `EventCalendar` 인스턴스를 초기화합니다.
    - 현재 시장의 리스크 상태를 간단히 가져올 수 있는 `_get_macro_risk()` 유틸리티 메서드를 추가합니다.

### Task 2: 매수 로직 고도화 (Macro-Aware Buy)
- **Files:** `src/agents/auto_trader.py`
- **Action:**
    - `_check_and_buy` 내부에서 매매 결정 전 매크로 리스크 점수를 확인합니다.
    - **중요도 Critical** 이벤트가 12시간 이내에 있을 경우:
        - 신규 매수 전면 중단 (관망 모드).
    - **중요도 High** 이벤트가 24시간 이내에 있을 경우:
        - `OrderExecutor.calculate_position_size`의 결과값을 50%로 줄여서 보수적으로 진입합니다.

### Task 3: 매도 로직 고도화 (Macro-Aware Sell/Hold)
- **Files:** `src/agents/auto_trader.py`
- **Action:**
    - `_check_and_sell` 내부에서 리스크가 높을 경우, 평소보다 낮은 익절 점수(SELL_SCORE)에서도 빠르게 수익을 실현하도록 로직을 조정합니다.
    - 리스크 점수가 극도로 높으면(Impact Score > 0.8), 보유 비중 축소 권고 알림을 발송합니다.

### Task 4: Gemini AI 판단 프롬프트 확장
- **Files:** `src/agents/auto_trader.py`
- **Action:**
    - `_get_ai_decision` 메서드의 `context`에 `upcoming_events` 정보를 포함합니다.
    - 프롬프트에 "곧 발표될 경제 지표를 고려하여 보수적으로 판단하라"는 지침을 강화합니다.

### Task 5: 최종 검증 및 알림 확인
- **Files:** `test_auto_trader_macro.py` (신규)
- **Action:**
    - 가상의 `Critical` 이벤트가 있는 상황을 시뮬레이션하여 `AutoTrader`가 매수를 멈추거나 비중을 줄이는지 확인합니다.
    - 디스코드 알림에 "매크로 리스크 감지로 인한 비중 조절" 메시지가 정상적으로 포함되는지 검증합니다.
