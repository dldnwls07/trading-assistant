# QuantCore Pro: Elite AI Terminal & Intelligent Charting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**목표:** AI 패턴 탐지(B), 사용자 드로잉(A), 그리고 데이터 밀집형 터미널 레이아웃(C)을 결합하여 전문가급 트레이딩 환경을 구축합니다.

---

### Task 1: AI 패턴 탐지 및 자동 드로잉 (Priority B)
- **Files:** `src/agents/analyst.py`, `frontend/src/components/StockChart.jsx`
- **Action:**
    - 백엔드 `StockAnalyst`가 기술적 패턴(Double Bottom, Triangles 등)의 구체적인 가격 좌표(Price Points)를 반환하도록 강화합니다.
    - 프론트엔드 `StockChart`에서 AI가 찾은 패턴을 차트 위에 도형(Polygons/Trendlines)으로 자동 렌더링합니다.
    - AI가 분석한 주요 지지/저항선을 Price Line으로 시각화합니다.

### Task 2: 인터랙티브 드로잉 툴바 구현 (Priority A)
- **Files:** `frontend/src/components/StockChart.jsx`, `frontend/src/components/chart/DrawingToolbar.jsx` (신규)
- **Action:**
    - 차트 좌측에 추세선, 수평선, 텍스트 도구를 포함한 드로잉 툴바를 추가합니다.
    - `lightweight-charts`의 `subscribeClick` 및 `subscribeCrosshairMove`를 활용하여 사용자가 차트 위에 직접 선을 긋고 저장할 수 있는 로직을 구현합니다.
    - 드로잉 데이터를 로컬 스토리지에 저장하여 페이지 새로고침 시에도 유지되도록 합니다.

### Task 3: 전문가용 터미널 레이아웃 및 거시 타임라인 (Priority C)
- **Files:** `frontend/src/pages/AnalysisPage.jsx`, `frontend/src/components/StockChart.jsx`
- **Action:**
    - 차트 우측에 **Volume Profile (매물대)** 히스토그램을 추가하여 가격대별 거래량을 시각화합니다.
    - 차트 하단 시간축에 경제 지표 발표 일정을 아이콘으로 표시하는 **Macro Timeline Marks**를 추가합니다.
    - 전체 레이아웃을 더 좁은 여백과 높은 데이터 밀도를 가진 '터미널 스타일'로 리팩토링합니다.

### Task 4: UI/UX 폴리싱 및 테마 고도화
- **Files:** `frontend/src/index.css`, `frontend/src/pages/AnalysisPage.jsx`
- **Action:**
    - Neon Blue / Cyberpunk 다크 테마를 강화합니다.
    - 유리 질감(Glassmorphism) 효과를 모든 대시보드 카드에 적용합니다.
    - 사이드바 툴바의 애니메이션 및 마이크로 인터랙션을 추가합니다.

---

### Task 5: 통합 검증 및 테스트
- **Action:**
    - AI가 패턴을 정확히 그려주는지 확인합니다.
    - 사용자가 그은 선이 시간축 이동 시에도 정확한 가격대에 고정되는지 확인합니다.
    - 모바일/데스크톱 반응형 레이아웃을 검증합니다.
