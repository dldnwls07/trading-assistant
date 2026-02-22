# 추가 DDD (Feature-Sliced Design) 리팩토링 검토 보고서

현재까지 `analysis`, `calendar`, `chat`, `portfolio`, `screener` 도메인의 초기 분리가 완료되었습니다. 전체 코드베이스(`frontend/src`, `src` 백엔드)를 점검한 결과, 다음과 같은 추가적인 DDD 구조화 대상이 존재합니다.

## 1. 프론트엔드 (Frontend) 추가 개선 사항

### 1-1. `Wallet` 도메인 분리
현재 `src/pages/WalletPage.jsx`가 존재하지만 `features/wallet`으로 분리되지 않았습니다.
- **작업 내용:** 
  - `features/wallet/api/walletApi.ts` 생성
  - `features/wallet/hooks/useWallet.ts` 생성
  - `WalletPage.jsx`의 비즈니스 로직(지갑 잔고, 연동 로직 등)을 이관

### 1-2. 차트(Chart) 관련 공통 피처화 (Shared Feature)
`src/components/StockChart.tsx`와 `src/hooks/useChart...` 파일들이 루트 가까이에 파편화되어 있습니다. 이는 `analysis` 뿐만 아니라 향후 다른 곳에서도 쓰일 수 있으므로 공통 피처 또는 UI 모듈로 격리가 필요합니다.
- **작업 내용:**
  - `features/chart` 또는 `shared/chart` 형태의 폴더 생성
  - `useChartDrawing.js`, `useChartIndicators.ts`, `useChartResize.js` 훅들을 해당 폴더로 이관
  - `StockChart.tsx` 컴포넌트 이관

### 1-3. 전역/공통 컴포넌트의 `shared` 계층 정립
현재 `src/components`에 `HelpTooltip`, `Navigation`, `SettingsModal` 등이 모여 있습니다. FSD(Feature-Sliced Design) 패턴에 맞게 전역 UI와 위젯들을 분류할 필요가 있습니다.
- **작업 내용:**
  - `shared/ui` (단순 컴포넌트: HelpTooltip 등)
  - `widgets` (복합 컴포넌트: Navigation, SettingsModal 등) 로 재구성

---

## 2. 백엔드 (Backend) 추가 개선 사항

백엔드의 `src/` 폴더는 최근 `domains/` 라우터 분리 작업을 통해 1차적인 도메인 분리가 이루어졌습니다. 하지만 세부 내부 점검 결과 추가 개선점이 보입니다.

### 2-1. `agents/` 디렉터리의 기능별 응집화
현재 AI 에이전트 클래스들이 `src/agents/` 하나에 몰려 있을 가능성이 높습니다. 에이전트들도 각 도메인(분석, 채팅, 포트폴리오 등)에 기여하므로 구조화가 필요합니다.
- **검토 내용:** `agents/` 폴더도 `domains/`에 맞추어 그룹화할 수 있는지 점검.

### 2-2. `components/` 및 `services/`의 분리 명확화
백엔드 로직이 `api/`(라우터 중심)와 `domains/`로 나뉘어 있는데, `services/` 폴더와의 책임을 명확히 가를 필요가 있습니다. 순수 비즈니스 서비스 로직이 라우터 파일(`domains/*.py`) 내부에 강하게 결합되어 있는지 확인 후 Layered Architecture 관점의 쪼개기가 필요합니다.

---

## 🚀 다음 스텝 제안

추가 리팩토링의 **우선순위**는 다음과 같습니다. 

1. **(Frontend) `Wallet` 도메인 완료 및 `Chart` 공통 모듈화:** 가장 빠르고 확실하게 기존 페이지 해체 작업을 마무리 지을 수 있습니다.
2. **(Frontend) `shared/`, `widgets/` 계층 도입:** 프론트엔드의 FSD 패턴을 완벽히 완성합니다.
3. **(Backend) `domains/` 내부의 서비스 레이어 분리:** 현재 라우터 파일에 몰려있는 비즈니스 로직을 `service` 구역으로 추출합니다.

어느 부분부터 작업을 이어나갈까요?
