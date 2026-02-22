# 🎯 하이브리드 AI 최종 통합 및 UI 강화 계획 (plan.md)

## 0. 목표
로컬 LLM(원-리즈닝)의 펀더멘털 분석과 RL 에이전트의 기술적 신호를 결합하는 **하이브리드 분석 레이어**를 구축하고, 이를 프론트엔드 UI에 시각화하여 최종 통합을 완료합니다.

## 1. 백엔드: 하이브리드 분석 레이어 구현
- **서비스 수정:** `src/domains/analysis_kr/services/kr_market_service.py` 확장
  - 기존 로컬 LLM 분석 결과에 RL 에이전트 신호를 결합하는 `get_hybrid_analysis` 메서드 추가.
  - Gemini를 사용하여 두 신호를 정합성 있게 요약.
- **라우터 업데이트:** 
  - `/api/analysis/kr/hybrid` 엔드포인트 신설. 

## 2. 프론트엔드: 분석 페이지(AnalysisPage) UI 강화
- **RL 게이지(Gauge) 추가:**
  - `AnalysisPage.tsx` 내 `ML_PRED` 섹션을 실제 RL 에이전트 데이터로 연동.
- **심층 추론 UI 연동:**
  - 로컬 LLM의 `<think>` 과정을 UI에 표시할 수 있도록 상태 관리 추가.

## 3. 마무리 및 검증
- **통합 테스트:** 삼성전자(KR) 케이스 최종 확인.
- **Git 커밋:** conventional commit 스타일로 커밋.

## 작업 순서 (turbo-all)
1. 백엔드 하이브리드 분석 로직 구현
2. 프론트엔드 UI 데이터 바인딩
3. 최종 검증 및 커밋
