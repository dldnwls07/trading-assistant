# 🗺️ QuantCore to FINT: Strategic Roadmap

## 🌟 Vision: "Democratizing Algo-Trading"
QuantCore 기술력을 바탕으로, FINT와 같이 **"초보자도 쉽고 투명하게 사용할 수 있는 자동 투자 플랫폼"**을 구축합니다.

---

## 🏗️ Phase 1: Core Engine & Data (Completed ✅)
> **Goal:** 안정적인 데이터 파이프라인과 기본 매매 엔진 구축
- [x] **Data Pipeline**: KRX/Fred API 연동 및 DB 구축
- [x] **Trade Engine**: 기본 매수/매도 로직 및 스케줄러 구현 (`AutoTrader`)
- [x] **Notification**: 디스코드 알림 시스템 (`Notifier`)

## 🎨 Phase 2: Intelligence & Visualization (Current 🔄)
> **Goal:** 투자의 근거를 시각적으로 설명하는 "설명 가능한 AI(XAI)" 터미널
- [ ] **Smart Charting (Auto-Drawing)**
    - *FINT Connection:* FINT의 "투명한 포트폴리오" 철학을 차트 시각화로 구현. AI가 왜 여기서 매수/매도 신호를 보냈는지 차트 위에 선(Line)과 영역(Zone)으로 직접 보여줌.
    - *Action:* 지지/저항선, 추세선 자동 드로잉 구현 (진행 중)
- [ ] **Insight Dashboard (Report)**
    - *FINT Connection:* FINT의 "Educational Dashboard"와 유사. 복잡한 지표 대신 "매수 강도", "위험도", "보유 기간" 등 직관적인 자연어 리포트 제공.
    - *Action:* `AnalysisInsights` 컴포넌트 고도화 (진행 중)
- [ ] **UI/UX Polishing**
    - *FINT Connection:* "User-Friendly Experience". 전문가용 기능을 유지하되, 디자인은 모던하고 깔끔하게(Glassmorphism) 다듬어 진입 장벽을 낮춤.

## 🤖 Phase 3: Automation & Personalization (Next)
> **Goal:** 개인 성향에 맞춘 자동 투자 및 자산 배분 (FINT의 핵심)
- [ ] **Thematic Investing ("Tilts")**
    - 사용자가 "AI 섹터", "반도체", "고배당" 등 테마를 고르면 AutoTrader가 관련 종목을 자동으로 큐레이션하고 비중 조절.
- [ ] **Risk Profiling & Dynamic Rebalancing**
    - 사용자 공격성(보수/중립/공격)에 따라 현금 비중과 로스컷 라인을 동적으로 조절하는 로직 추가.
- [ ] **Mobile-Native UI**
    - 데스크톱 터미널을 넘어, 모바일에서도 쉽게 확인 가능한 반응형 웹앱 완성.

---

## 🚀 Immediate Next Step: Phase 2 Execution
**"AI가 그린 차트, 투자의 네비게이션이 되다."**
우선적으로 사용자가 가장 먼저 접하는 시각 정보인 **차트의 신뢰도와 설명력**을 높이는 작업(Phase 2)에 집중합니다. 이는 FINT가 지향하는 "쉬운 투자"의 기술적 기반이 됩니다.
