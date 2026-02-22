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
