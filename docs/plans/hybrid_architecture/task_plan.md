# Task Plan: Hybrid AI Architecture Integration
<!-- 
  WHAT: This is your roadmap for the entire task. Think of it as your "working memory on disk."
-->

## Goal
To implement a production-ready, multi-agent hybrid architecture integrating an RL Agent (Adilbai/stock-trading-rl-agent) for technical signals, a local LLM (WON-Reasoning) for Korean fundamental analysis, a FinGPT-inspired RAG pipeline, and Gemini for US analysis and final synthesis.

## Current Phase
Phase 1: Architecture & Infrastructure Setup

## Phases

### Phase 1: Architecture & Infrastructure Setup
- [ ] Set up local serving infrastructure (Ollama/vLLM) for `KRX-Data/WON-Reasoning`
- [ ] Set up Python environment and dependencies for `Adilbai/stock-trading-rl-agent` (PyTorch, RL libraries)
- [ ] Define precise input/output schemas for each agent
- **Status:** in_progress

### Phase 2: Data Pipeline & FinGPT RAG Implementation
- [ ] Implement robust DART/KRX scrapers (Korean Data)
- [ ] Implement US market news/options scrapers
- [ ] Build FinGPT-style RAG vector store or retrieval logic for context injection
- **Status:** pending

### Phase 3: Agent Routing & Integration
- [ ] Implement n8n or Python routing logic: KR data -> WON-Reasoning
- [ ] Implement n8n or Python routing logic: US data -> Gemini
- [ ] Create chron-job or trigger to run RL agent daily for S&P500/KOSPI technical signals
- **Status:** pending

### Phase 4: Synthesis & Final Output
- [ ] Create the Master Prompt for Gemini to aggregate WON-Reasoning's output, US sentiment, and RL signals
- [ ] Format output for Discord Morning Briefing
- [ ] Expose aggregated JSON via backend API for frontend consumption
- **Status:** pending

### Phase 5: Frontend Integration & Verification
- [ ] Update `AnalysisPage.tsx` to display the dual-market insights and RL technical gauge
- [ ] Verify accuracy and latency of the entire pipeline
- **Status:** pending

## Key Questions
1. Do we have enough local VRAM to run WON-Reasoning (7B) concurrently with the RL agent?
2. Will the FinGPT RAG pipeline be built directly inside `server_mcp.py` or as a separate microservice?
3. How will historical financial data be fed into the RL agent daily?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Multi-Agent Routing | Maximizes the strengths of each model (Local specialized vs. API generalized vs. Quantitative RL). |
| FinGPT RAG concept | Ensures models ground their reasoning in actual real-time news to prevent hallucinations. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
- Update phase status as you progress: pending → in_progress → complete
- Re-read this plan before major decisions (attention manipulation)
- Log ALL errors - they help avoid repetition
