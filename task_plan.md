# Task Plan: Hybrid AI Architecture Integration (한·미 통합 분석 시스템)
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
-->

## Goal
한국 시장 분석에 특화된 로컬 모델(`WON-Reasoning`)과 미국 시장 및 종합 브리핑 융합에 능한 클라우드 모델(`Gemini`), 그리고 기술적 타이밍 보조지표로 작용하는 트레이딩 봇(`stock-trading-rl-agent`)을 `Trading Assistant Pro`의 파이프라인에 통합한다.

## Current Phase
Phase 1

## Phases

### Phase 1: 로컬 LLM 및 인프라 검증 (🇰🇷 WON-Reasoning)
- [ ] `Ollama` 또는 `vLLM`을 활용하여 `KRX-Data/WON-Reasoning` 7B 모델 구동 스크립트 작성 (예: `start_won_model.sh`)
- [ ] 파이썬 또는 `curl`로 로컬 서버 API에 한국어 기업 공시 테스트 프롬프트를 전송하고 `<think>` 추론 파싱 로직 구현
- [ ] n8n 워크플로우(`discord_morning_briefing.json`) 내에서 이 로컬 API를 호출하는 브랜치 임시 구성
- **Status:** pending

### Phase 2: 기술적 보조 지표 (🤖 RL Agent) 연동
- [ ] `Adilbai/stock-trading-rl-agent` 구동을 위한 파이썬 가상환경(venv) 및 의존성(`stable-baselines3`, `gym` 등) 세팅 스크립트 작성
- [ ] 특정 종목(S&P 500 또는 KOSPI 시총 상위)의 60일치 과거 데이터를 `yfinance` 등으로 받아 이 에이전트에 통과시키는 래퍼(Wrapper) 스크립트 개발 (`agents/rl_technical_analyzer.py`)
- [ ] 해당 스크립트 구동 시 [Buy/Sell/Hold, 비중] 수치가 정상 출력되는지 검증
- **Status:** pending

### Phase 3: RAG 파이프라인 (FinGPT 컨셉) 및 백엔드 통합
- [ ] 매일 아침의 최신 뉴스(텍스트)와 가격 데이터(숫자)를 DB 혹은 벡터 스토어에 적재하는 로직 구성 (기존의 `event_calendar.py` 등 확장)
- [ ] FastAPI 백엔드(`src/api/server.py` 또는 `src/server_mcp.py`)에 `/api/analyze/fundamental/kr` (WON 모델용) 및 `/api/analyze/technical/rl` (RL 모델용) 엔드포인트 신설
- **Status:** pending

### Phase 4: Gemini 융합 및 프론트엔드 표출
- [ ] WON-Reasoning의 <solution> 분석 결과, RL 에이전트의 Action 수치, 그리고 미국 영문 뉴스 리포팅을 종합하여 Gemini 1.5 Pro에 던지는 **"최종 마스터 프롬프트"** 작성
- [ ] `discord_morning_briefing.json`의 최종 노드로 위 프로세스를 완성 후 디스코드 알림 발송 테스트
- [ ] 프론트엔드(`frontend/src/features/analysis/`)에서 이 하이브리드 데이터를 받아와 차트 옆에 표출하는 UI 컴포넌트 추가
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Hybrid Multi-Agent 아키텍처 도입 | 언어/국가별 도메인 지식 격차(한국은 로컬 특화, 미국은 글로벌)를 줄이고, 동시에 Fundamental과 Technical 영역을 완전히 분리하여 정확도를 높이기 위함. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       |         |            |
