# Task Plan: Hybrid AI Architecture Integration
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
-->

## Goal
To implement a production-ready, multi-agent hybrid architecture integrating an RL Agent (Adilbai/stock-trading-rl-agent) for technical signals, a local LLM (WON-Reasoning) for Korean fundamental analysis, a FinGPT-inspired RAG pipeline, and Gemini for US analysis and final synthesis.

## Current Phase
Completed

## Phases

### Phase 1: 로컬 LLM 및 인프라 검증 (🇰🇷 WON-Reasoning)
- [x] `Transformers` + `BitsAndBytes` (4-bit 양자화) 기반 로컬 구동 코드 구현
- [x] RTX 4070 Ti Super (16GB) 최적화 및 CUDA 가속 연동 확인
- [x] FastAPI 백엔드(`analysis_kr` 도메인) 통합 및 API 테스트 완료
- [x] 프론트/백엔드 연동 및 UI 동작 확인
- **Status:** completed

### Phase 2: 기술적 보조 지표 (🤖 RL Agent) 연동
- [x] RL 에이전트 의존성 세팅 및 모델 로딩 로직 구현
- [x] MarketDataCollector 연동을 통한 60일 데이터 파이프라인 구축
- [x] RL 에이전트 (PPO) 기술적 신호 생성 검증 완료 (3008-dim)
- **Status:** completed

### Phase 3: Agent Routing & Integration
- [x] Python 기반 하이브리드 라우팅 로직 구현: KR -> WON-Reasoning + RL
- [x] Gemini를 활용한 기본적/기술적 분석 합성 레이어 구축
- **Status:** completed

### Phase 4: Synthesis & Final Output
- [x] 하이브리드 리포트(Thought + Signal + Synthesis) 통합 API 신설
- [x] 프론트엔드 소비를 위한 JSON 규격 확정
- **Status:** completed

### Phase 5: Frontend Integration & Verification
- [x] `AnalysisPage.tsx` 하이브리드 분석 버튼 및 결과 섹터 추가
- [x] RL Signal Gauge 위젯 UI 구현 및 연동
- [x] 전체 파이프라인 지연 시간 및 정확도 검증 완료
- **Status:** completed

## Key Questions
1. Do we have enough local VRAM? Yes, 4-bit quantization + CPU unloading for RL ensures stability.
2. Routing logic? Implemented in `KRMarketAnalysisService`.

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Hybrid Synthesis | Combines human-like reasoning (LLM) with quantitative precision (RL). |
| Lazy Loading | Conserves GPU memory by loading big models only when needed. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| 3.13 Compatibility | 1 | Switched to MarketDataCollector to avoid yfinance raw errors. |
| Model 404 | 1 | Corrected filename from `ppo_stock_trading.zip` to `final_model.zip`. |
| Quota Exceeded | 1 | Implemented Groq (Llama-3) fallback for hybrid synthesis. |
