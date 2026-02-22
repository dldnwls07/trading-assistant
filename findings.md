# Findings & Decisions
<!-- 
  WHAT: Your knowledge base for the task. Stores everything you discover and decide.
-->

## Requirements
<!-- Captured from user request -->
- Integrate `Adilbai/stock-trading-rl-agent` for automated technical trading signals.
- Integrate `KRX-Data/WON-Reasoning` locally for Korean stock market/news analysis.
- Adopt `AI4Finance-Foundation/FinGPT` concepts for pipeline architecture and RAG.
- Use `Google Gemini` as the ultimate synthesizer and US market analyzer.
- Create a realistic plan that fits within the current `Trading Assistant Pro` features (already containing React frontend and FastAPI backend).

## Research Findings
<!-- Key discoveries during exploration -->
- The workspace already had a `task_plan.md` focusing on Frontend Feature-Sliced Refactoring. The frontend is organized under `src/features/`.
- `WON-Reasoning` output includes `<think>` tags which must be parsed and logically passed to Gemini to preserve the reasoning steps.
- `Adilbai/stock-trading-rl-agent` requires numerical indicator inputs (SMA, MACD, RSI, Bollinger Bands, Volume, Price).
- FinGPT RAG focuses on fetching real-time news/tweets, retrieving top K relevant chunks using a lightweight embedding model, and passing them to the LLM to prevent hallucinations.
<!--### Key Discoveries
- **Hardware Optimization (RTX 4070 Ti Super 16GB):**
  - 16-bit 로딩 시 VRAM 부족으로 RAM(32GB) 점유율이 98%까지 치솟으며 시스템이 정지됨.
  - `BitsAndBytes` 4-bit 양자화 적용 시 VRAM 점유율 약 6GB 수준으로 안정화.
  - CUDA 전용 PyTorch(cu124) 설치로 GPU 사용률 100% 확보, 추론 속도 10배 이상 향상.
- **Hybrid AI Pipeline:**
  - 한국 시장 분석에는 `WON-Reasoning`이 `<think>` 태그를 통한 심층 추론에 매우 탁월함 확인.
  - 전용 도메인(`analysis_kr`)을 통해 백엔드 라우터-서비스-인프라 계층 분리 완료.
- **Frontend Integration:**
  - Vite + React 기반의 프리미엄 UI가 정상 작동 중이며, 삼성전자 등 한국 종목 차트 로딩 및 분석 준비 완료.

---
*Note: 작업을 진행하면서 파악되는 파일별 문제점이나 해결책을 이곳에 누적 기록합니다.*

## Technical Decisions
<!-- Decisions made with rationale -->
| Decision | Rationale |
|----------|-----------|
| Hybrid Multi-Agent | KRX data is best handled by WON-Reasoning; general text parsing and final formatting by Gemini; pure numerical technical analysis by PPO RL Agent. |
| Reuse Project Root | Overwrote the old frontend refactoring `task_plan.md` in the root directory to maintain the single source of truth for the *current* major epic (Hybrid AI). |

## Issues Encountered
<!-- Errors and how they were resolved -->
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
<!-- URLs, file paths, API references -->
- WON-Reasoning: https://huggingface.co/KRX-Data/WON-Reasoning
- RL Agent: https://huggingface.co/Adilbai/stock-trading-rl-agent
- FinGPT: https://github.com/AI4Finance-Foundation/FinGPT

---
*Update this file after every 2 view/browser/search operations*
*This prevents visual information from being lost*
