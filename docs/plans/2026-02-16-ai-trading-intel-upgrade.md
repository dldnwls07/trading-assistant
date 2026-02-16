# AI Trading Intelligence & Discord Notification Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 경제 캘린더 알림 시스템을 고도화하여 LLM 기반의 시장 분석 리포트와 시각적으로 풍부한 디스코드 알림을 제공합니다.

**Architecture:** 
1. `economic_events` DB 스키마를 확장하여 AI 분석 데이터를 저장합니다.
2. `EventCalendar` 에이전트에 LLM 연동 분석 로직을 추가하여 지표 발표 전/후 전략을 생성합니다.
3. `DiscordNotifier`를 강화하여 임베드(Embed) 형식의 풍부한 알림을 지원합니다.
4. `alert_worker.py`의 스케줄링 로직을 개선하여 정기 브리핑 및 실시간 속보 체계를 구축합니다.

**Tech Stack:** Python, SQLAlchemy, Discord Webhooks, LLM (OpenAI/Gemini), Asyncio

---

### Task 1: 데이터베이스 스키마 확장
**관련 스킬:** `@backend_engineer`, `@supabase-postgres-best-practices` (SQL 구조 참고용)

**Files:**
- Modify: `src/data/storage.py`

**Step 1: EconomicEvent 모델에 AI 분석 컬럼 추가**
- `ai_pre_analysis` (발표 전 시나리오), `ai_post_analysis` (발표 후 해설), `ai_image_url` (차트 이미지) 컬럼을 추가합니다.
- `save_economic_events` 메서드에서 해당 필드들을 업데이트할 수 있도록 수정합니다.

**Step 2: 마이그레이션 확인**
- `cleanup_db.py` 등을 활용하여 스키마가 정상적으로 반영되는지 확인합니다.

---

### Task 2: AI 분석 엔진 구현 (EventCalendar 고도화)
**관련 스킬:** `@python_expert`, `@chief_architect`

**Files:**
- Modify: `src/agents/event_calendar.py`

**Step 1: LLM 연동 분석 메서드 추가**
- `generate_ai_scenarios()`: 주요 지표에 대한 사전 시나리오 생성
- `generate_post_event_report()`: 수치 발표 후 실시간 영향력 분석 리포트 생성
- 기존 `_get_scenario_analysis`를 LLM 기반으로 고도화합니다.

---

### Task 3: 디스코드 임베드 알림 현대화
**관련 스킬:** `@ui-ux-pro-max`, `@frontend_design`

**Files:**
- Modify: `src/utils/notifications.py`
- Modify: `src/api/alert_worker.py`

**Step 1: Rich Embed 지원**
- `DiscordNotifier.send_message`가 더 정교한 임베드 필드와 색상을 지원하도록 확장합니다.
- 중요도(`critical`, `high`)에 따른 색상 테마를 정의합니다.

---

### Task 4: 알림 스케쥴러 및 실시간 감시 통합
**관련 스킬:** `@devops_engineer`, `@backend_engineer`

**Files:**
- Modify: `src/api/alert_worker.py`

**Step 1: 실시간 모니터링 로직 강화**
- 지표 발표 후 10분 이내에 결과를 감지하고 AI 리포트를 생성하여 발송하는 루프를 견고하게 다듬습니다.
- 데일리/위클리/먼슬리 브리핑에 임베드 디자인을 적용합니다.

---

### Task 5: 최종 검증 및 테스트
**관련 스킬:** `@testing_qa`, `@verification-before-completion`

**Step 1: 시뮬레이션 테스트**
- 가상의 이벤트 데이터를 생성하여 디스코드 알림이 설계한 대로(풍부하게) 오는지 확인합니다.
- 매월 1일/매주 월요일 등의 스케줄링 트리거가 정상 작동하는지 로그로 검증합니다.
