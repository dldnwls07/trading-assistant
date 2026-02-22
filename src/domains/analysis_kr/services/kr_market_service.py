from src.domains.analysis_kr.interfaces.abstract_analyst import LocalAnalyst
from src.domains.analysis_kr.entities.analysis import WONAnalysisResult
from src.domains.trading_signals.services.signal_service import SignalService
from src.agents.analysis.ai_analyzer import AIAnalyzer
import logging

logger = logging.getLogger(__name__)

class KRMarketAnalysisService:
    def __init__(self, analyst: LocalAnalyst, signal_service: SignalService = None):
        self.analyst = analyst
        self.signal_service = signal_service
        self.ai_synthesizer = AIAnalyzer() # Gemini 기반 합성기

    async def analyze_company_with_news(self, ticker: str, news_list: list[str]) -> WONAnalysisResult:
        """
        뉴스 목록을 받아 기업의 현재 상황을 한국 특화 모델로 추론 분석
        """
        context = "\n".join([f"- {news}" for news in news_list])
        result = await self.analyst.analyze(ticker, context)
        return result

    async def get_hybrid_analysis(self, ticker: str, news_list: list[str]) -> dict:
        """
        [Hybrid Engine] 
        1. WON-Reasoning (Fundamental Thought)
        2. RL Agent (Technical Signal)
        3. Gemini (Final Synthesis)
        """
        # 1. 로컬 LLM 심층 분석 (기본적 분석)
        won_result = await self.analyze_company_with_news(ticker, news_list)
        
        # 2. RL 에이전트 신호 (기술적 분석)
        rl_signal = None
        if self.signal_service:
            try:
                rl_signal = await self.signal_service.generate_rl_signal(ticker)
            except Exception as e:
                logger.warning(f"RL Signal failed for {ticker}: {e}")

        # 3. Gemini를 활용한 최종 통합 리포트 생성
        final_summary = "분석 중 오류가 발생했습니다."
        if self.ai_synthesizer:
            rl_info = f"Action: {rl_signal.action}, Confidence: {rl_signal.position_size*100:.1f}%" if rl_signal else "데이터 없음"
            
            prompt = f"""
            당신은 매크로와 매매 기술을 모두 섭렵한 하이브리드 트레이더입니다. 
            아래의 두 가지 상반되거나 상호 보완적인 분석 데이터를 통합하여 실전 매매 전략을 한글로 요약하세요.

            [1. 기본적 분석 (로컬 LLM 추론)]
            {won_result.solution}

            [2. 기술적 분석 (강화학습 에이전트 신호)]
            {rl_info}

            분석 요구사항:
            1. **반드시 100% 한글(현대 한국어)**로만 작성하세요. (한자를 섞어 쓰면 절대 안 됩니다. 예: 分析 -> 분석, 慎重 -> 신중, 內外 -> 내외)
            2. 두 분석의 결이 같다면 확신을 가지고 추천하고, 다르다면 리스크 요인을 짚어주세요.
            3. 투자자에게 줄 수 있는 최종 결론(매수/매도/관망)과 비중 조절 제안을 포함하세요.
            4. 3-4문장 내외로 간결하고 전문적으로 작성하세요.
            """
            final_summary = await self.ai_synthesizer.generate_dynamic_analysis(prompt)

        return {
            "ticker": ticker,
            "won_analysis": won_result,
            "rl_signal": rl_signal,
            "hybrid_comment": final_summary
        }

    async def analyze_earnings_announcement(self, ticker: str, earnings_data: dict) -> WONAnalysisResult:
        context = f"실적 공시 요약: {earnings_data}"
        result = await self.analyst.analyze(ticker, context)
        return result
