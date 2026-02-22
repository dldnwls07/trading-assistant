# 🚀 백엔드 및 프론트엔드 DDD 구조(도메인 주도 설계) 개편 계획서

**목표**: 기술 중심적(계층형)으로 분리된 폴더 구조를 "비즈니스 핵심 목적(Domain/Feature)" 단위로 재편하여 코드 일관성과 확장성을 높입니다.

## 🛠️ 1. 백엔드(Backend) 구조 개편
현재 1100줄이 넘는 `src/api/server.py`를 도메인 단위로 해체하여 `router`로 분리합니다. 향후 각 도메인 폴더 안에는 `service(비즈니스 로직)`과 `repository(DB 연동)` 파일이 추가될 수 있도록 기반을 마련합니다.

### 📁 개편 후 백엔드 폴더 구조 (예정)
```text
src/
 ├─ domains/               ← (신규) 비즈니스 도메인 폴더
 │   ├─ analysis/          # 분석 도메인 (기술적 분석, 종합 분석, 다중 타임프레임)
 │   │   └─ router.py
 │   ├─ market_data/       # 시장 데이터 (히스토리 시세, 종목 검색, 환율)
 │   │   └─ router.py
 │   ├─ chat/              # AI 채팅 (채팅 주고받기, 추천 질문, 채팅 내역 초기화)
 │   │   └─ router.py
 │   ├─ portfolio/         # 포트폴리오 (보유 종목, 가상 계좌, 자산 분석)
 │   │   └─ router.py
 │   ├─ calendar/          # 일정 도메인 (경제 캘린더, 실적 발표, 이벤트 분석)
 │   │   └─ router.py
 │   ├─ screener/          # 스크리너 도메인 (AI 추천, 급등/급락 종목)
 │   │   └─ router.py
 │   ├─ backtest/          # 백테스팅 (전략 테스트, 최적화)
 │   │   └─ router.py
 │   └─ tools/             # 사전, 유틸성 기능 도메인
 │       └─ router.py
 │
 ├─ api/
 │   └─ server.py          ← 각 domain의 router들을 `app.include_router()`로 조립하는 가벼운 진입점으로 변경
```

### 📋 백엔드 작업 순서
1. `src/domains/` 하위 폴더 및 `router.py` 일괄 생성.
2. `server.py`에 산재한 API 엔드포인트들을 도메인별 `router.py`로 이동. (FastAPI의 `APIRouter` 사용)
3. `server.py`에서 의존성 꼬임 방지를 위해 필요한 패키지(`Request`, `BackgroundTasks` 등) import 수정.
4. `server.py` 가벼운 조립 라인(app.include_router)으로 축소.
5. 로컬 서버 테스트 구동을 통한 오류 점검.

---

## 🎨 2. 프론트엔드(Frontend) 구조 개편
Feature 단위로 화면(Page)과 해당 도메인의 로직(Component, Hooks)을 한곳에 응집시키는 Feature-Sliced Design 철학을 일부 도입합니다.

### 📁 개편 후 프론트엔드 폴더 구조 (예정)
```text
frontend/src/
 ├─ features/                ← (신규) 비즈니스 피처 폴더
 │   ├─ analysis/            # 분석 화면 관련 (AnalysisPage, StockChart, 관련 훅)
 │   ├─ calendar/            # 캘린더 관련 (CalendarPage, EarningsPage, 관련 모달)
 │   ├─ chat/                # 챗 관련 (ChatPage, 입력 폼 등)
 │   ├─ portfolio/           # 포트폴리오 (PortfolioPage, WalletPage)
 │   └─ screener/            # 스크리너 (ScreenerPage)
 │
 ├─ components/
 │   └─ common/              # 전역 재사용 컴포넌트 (버튼, 네비게이션, 툴팁 등)
 │
 ├─ pages/                   # 앱의 라우팅 트리(react-router 진입점) 역할만 담당 (엄청 얇아짐)
 ├─ hooks/                   # 도메인에 종속되지 않는 전역 훅
 └─ utils/                   # 포매터 등 공통 유틸
```

### 📋 프론트엔드 작업 순서
1. `frontend/src/features/` 디렉터리 생성 및 도메인 하위 디렉터리 구축.
2. 기존 `components/` 및 `pages/`에 있는 거대한 파일들을 비즈니스 맥락에 맞게 분산 배치.
3. 코드 이동에 따른 `import 경로` 역추적 후 모두 수정 (매우 중요).
4. `App.jsx` 등의 라우팅 연결부 경로 수정.
5. `npm run dev` (또는 로컬 Vite 빌드) 테스트를 통해 import 에러가 없는지 무결성 검증.

---

*본 계획은 한 번에 코드를 크게 뜯어고치는 "파괴적 리팩토링"입니다. 작업 중 예기치 못한 버그를 막기 위해 백엔드 구조부터 분할 검증을 완료하고 프론트엔드를 진행하도록 하겠습니다.*
