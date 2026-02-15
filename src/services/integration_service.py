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
        
        try:
            # 1. 데이터 수집 (병렬)
            daily_data_task = self.collector.get_ohlcv(ticker, period="2y", interval="1d")
            
            # 2. 추가 데이터 확보 (재무, 이벤트)
            financials = await self.storage.get_financials(ticker)
            if not financials:
                await self.parser.fetch_and_save_financials(ticker)
                financials = await self.storage.get_financials(ticker)
            
            events_task = asyncio.to_thread(get_stock_events, ticker)
            
            # 일봉 데이터 확보
            daily_df = await daily_data_task
            if daily_df is None or daily_df.empty:
                raise ValueError(f"No daily data found for {ticker}")
            
            # 3. 분석 태스크들 병렬 실행
            ml_task = asyncio.to_thread(self.ml_predictor.predict_next, daily_df)
            multi_res_task = self.multi_analyzer.analyze_all_timeframes(ticker)
            events = await events_task
            
            ml_res, multi_res = await asyncio.gather(ml_task, multi_res_task)
            
            # 4. 결과 통합 및 가공
            final_result = {
                **multi_res, # Multi-timeframe results (Score, Signal, Patterns, etc)
                "ml_prediction": ml_res,
                "events": events,
                "fundamental_summary": multi_res.get("medium_term", {}).get("full_analysis", {}).get("fundamental", {}),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            # 5. 최종 종합 AI 리포트 생성 (모든 데이터 통합)
            # multi_analyzer 내에서 이미 ai_report를 생성했을 수 있지만, 통합 단계에서 재정의 가능
            final_result["full_report"] = self.ai_analyzer.generate_report(final_result)
            
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
