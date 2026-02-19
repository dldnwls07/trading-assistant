import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.config import settings
from src.data.collector import MarketDataCollector
from src.agents.analyst import StockAnalyst
from src.agents.multi_timeframe import MultiTimeframeAnalyzer
from src.agents.ml_predictor import MLPricePredictor
from src.agents.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

from src.data.storage import get_storage
from src.data.parser import FinancialParser
from src.agents.ai_analyzer import get_stock_events

class IntegrationService:
    """
    통합 비즈니스 로직 서비스 (Facade Pattern)
    - 데이터 수집, ML 예측, 에이전트 분석을 조율
    """
    def __init__(
        self,
        collector: MarketDataCollector = None,
        multi_analyzer: MultiTimeframeAnalyzer = None,
        ml_predictor: MLPricePredictor = None,
        ai_analyzer: AIAnalyzer = None,
        storage = None,
        parser = None
    ):
        self.collector = collector or MarketDataCollector()
        self.multi_analyzer = multi_analyzer or MultiTimeframeAnalyzer()
        self.ml_predictor = ml_predictor or MLPricePredictor()
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.storage = storage or get_storage()
        self.parser = parser or FinancialParser()
        
    async def run_comprehensive_analysis(self, ticker: str) -> Dict[str, Any]:
        """한 종목에 대한 모든 관점의 종합 분석 실행"""
        logger.info(f"🔮 Orchestrating analysis for {ticker}...")
        
        async def ensure_financials():
            """재무 데이터 확보 보장"""
            f = await self.storage.get_financials(ticker)
            if not f:
                await self.parser.fetch_and_save_financials(ticker)
                
        try:
            # 1. 핵심 데이터 수집 (병렬 처리)
            # 일봉 데이터와 재무 데이터는 서로 독립적이므로 동시에 가져옵니다.
            # 하나라도 실패하면 즉시 에러를 반환하여 불필요한 연산을 방지합니다.
            results = await asyncio.gather(
                self.collector.get_ohlcv(ticker, period="2y", interval="1d"),
                ensure_financials(),
                return_exceptions=False
            )
            
            daily_df = results[0]
            
            # 일봉 데이터 검증
            if daily_df is None or daily_df.empty:
                raise ValueError(f"No daily data found for {ticker}")
            
            # 2. 분석 태스크 병렬 실행 (데이터 확보 후 실행)
            # - ML 예측 (CPU Bound -> to_thread)
            # - 이벤트 수집 (IO/CPU Bound -> to_thread)
            # - 멀티 타임프레임 분석 (Async IO Cloud)
            ml_task = asyncio.to_thread(self.ml_predictor.predict_next, daily_df)
            events_task = asyncio.to_thread(get_stock_events, ticker)
            multi_res_task = self.multi_analyzer.analyze_all_timeframes(ticker)
            
            ml_res, events, multi_res = await asyncio.gather(
                ml_task, 
                events_task, 
                multi_res_task
            )
            
            # 3. 결과 통합 및 가공
            final_result = {
                **multi_res, # Multi-timeframe results (Score, Signal, Patterns, etc)
                "ml_prediction": ml_res,
                "events": events or {}, # None 방지
                "fundamental_summary": multi_res.get("medium_term", {}).get("full_analysis", {}).get("fundamental", {}),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            # multi_timeframe.analyze_all_timeframes()에서 이미 AI 리포트 생성 완료
            # (final_score, signal, full_report 포함)
            # 여기서 generate_report를 다시 호출하면 이중 호출 + 데이터 구조 불일치로 실패함
            
            return final_result

        except Exception as e:
            logger.error(f"❌ Integration error for {ticker}: {e}")
            return {"status": "error", "message": str(e), "timestamp": datetime.now().isoformat()}

# 싱글톤 인스턴스 팩토리
_integration_service = None

def get_integration_service() -> IntegrationService:
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService()
    return _integration_service
