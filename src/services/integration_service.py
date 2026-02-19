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
from src.agents.strategy_ensemble import StrategyEnsemble
from src.utils.backtester import Backtester

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
            results = await asyncio.gather(
                self.collector.get_ohlcv(ticker, period="2y", interval="1d"),
                ensure_financials(),
                return_exceptions=False
            )
            
            daily_df = results[0]
            
            if daily_df is None or daily_df.empty:
                raise ValueError(f"No daily data found for {ticker}")
            
            # 2. 분석 태스크 병렬 실행
            ml_task = asyncio.to_thread(self.ml_predictor.predict_next, daily_df)
            events_task = asyncio.to_thread(get_stock_events, ticker)
            multi_res_task = self.multi_analyzer.analyze_all_timeframes(ticker)
            
            ml_res, events, multi_res = await asyncio.gather(
                ml_task, events_task, multi_res_task
            )
            
            # 3. 결과 통합 및 가공
            final_result = {
                **multi_res,
                "ml_prediction": ml_res,
                "events": events or {},
                "fundamental_summary": multi_res.get("medium_term", {}).get("full_analysis", {}).get("fundamental", {}),
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            # 4. ML Forecast를 medium_term.full_analysis.ml_forecast에도 매핑
            #    (프론트엔드 TradingSetup 컴포넌트가 이 경로를 참조)
            medium_term = final_result.get("medium_term", {})
            if medium_term and ml_res:
                full_analysis = medium_term.get("full_analysis", {})
                if isinstance(full_analysis, dict):
                    full_analysis["ml_forecast"] = ml_res
                    medium_term["full_analysis"] = full_analysis
                    final_result["medium_term"] = medium_term
            
            # 5. 백테스트 실행 및 medium_term.full_analysis.backtest에 매핑
            try:
                backtest_res = await self._run_backtest(daily_df)
                if medium_term and isinstance(medium_term.get("full_analysis"), dict):
                    medium_term["full_analysis"]["backtest"] = backtest_res
            except Exception as e:
                logger.warning(f"백테스트 실행 실패: {e}")
            
            # 6. Strategy Ensemble (consensus.global_ensemble) 생성
            try:
                ensemble_result = self._build_consensus(final_result, ml_res)
                final_result["consensus"] = {"global_ensemble": ensemble_result}
            except Exception as e:
                logger.warning(f"앙상블 계산 실패: {e}")
            
            # 7. Entry Points (진입가/손절가/익절가) 계산
            try:
                entry_points = self._calculate_entry_points(final_result)
                final_result["entry_points"] = entry_points
            except Exception as e:
                logger.warning(f"진입가 계산 실패: {e}")
            
            # 8. Market Regime (시장 국면) 판정
            try:
                market_regime = self._determine_market_regime(final_result)
                final_result["market_regime"] = market_regime
            except Exception as e:
                logger.warning(f"마켓 레짐 판정 실패: {e}")
            
            # 9. Strategy Checklist 생성
            try:
                checklist = self._build_strategy_checklist(final_result)
                final_result["strategy_checklist"] = checklist
            except Exception as e:
                logger.warning(f"체크리스트 생성 실패: {e}")
            
            return final_result

        except Exception as e:
            logger.error(f"❌ Integration error for {ticker}: {e}")
            return {"status": "error", "message": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _run_backtest(self, daily_df) -> Dict[str, Any]:
        """RSI 기반 간단한 전략으로 백테스트 수행"""
        import pandas as pd
        from src.utils.advanced_indicators import AdvancedIndicators
        
        df = AdvancedIndicators.calculate_all(daily_df.copy())
        
        # RSI 기반 매매 신호 생성: RSI < 30 매수, RSI > 70 매도
        signals = pd.Series(0, index=df.index)
        if "rsi" in df.columns:
            signals[df["rsi"] < 30] = 1   # 매수
            signals[df["rsi"] > 70] = -1  # 매도
        
        return Backtester.backtest_vectorized(df, signals)
    
    def _build_consensus(self, final_result: dict, ml_res: dict) -> Dict[str, Any]:
        """StrategyEnsemble을 활용하여 종합 등급/신뢰도 산출"""
        med_analysis = final_result.get("medium_term", {}).get("full_analysis", {})
        tech_results = med_analysis.get("daily_analysis", {})
        
        # 기술적 점수 — raw_indicators의 RSI를 기반으로 간이 산출
        raw = tech_results.get("raw_indicators", {})
        rsi = raw.get("rsi", 50)
        tech_score = max(0, min(100, rsi))
        
        tech_input = {"score": tech_score, "patterns": [], "divergences": []}
        event_input = {"impact_score": 0.3, "is_fomc_week": False}
        fund_input = {"score": 50}
        
        return StrategyEnsemble.calculate_ensemble(
            tech_results=tech_input,
            event_results=event_input,
            fund_results=fund_input,
            sentiment_score=50.0,
            ml_forecast=ml_res
        )
    
    def _calculate_entry_points(self, final_result: dict) -> Dict[str, float]:
        """현재가와 ATR을 기반으로 진입가/손절가/익절가 계산"""
        med = final_result.get("medium_term", {})
        raw = med.get("full_analysis", {}).get("daily_analysis", {}).get("raw_indicators", {})
        
        close = raw.get("Close", 0)
        atr = raw.get("atr", 0)
        
        if not close or not atr:
            # ATR이 없으면 현재가 기준 2% 범위 사용
            close = med.get("current_price", 0)
            atr = close * 0.02 if close else 0
        
        return {
            "entry_price": round(close - atr * 0.5, 2),    # ATR 0.5배 아래 진입
            "stop_loss": round(close - atr * 2.0, 2),      # ATR 2배 아래 손절
            "take_profit": round(close + atr * 3.0, 2),    # ATR 3배 위 익절 (R:R = 1:1.5)
        }
    
    def _determine_market_regime(self, final_result: dict) -> Dict[str, str]:
        """ADX, SMA 위치, 변동성을 기반으로 시장 국면 판정"""
        med = final_result.get("medium_term", {})
        raw = med.get("full_analysis", {}).get("daily_analysis", {}).get("raw_indicators", {})
        
        adx = raw.get("adx", 0)
        close = raw.get("Close", 0)
        sma_50 = raw.get("sma_50", 0)
        sma_200 = raw.get("sma_200", 0)
        
        above_sma50 = close > sma_50 if (close and sma_50) else False
        above_sma200 = close > sma_200 if (close and sma_200) else False
        
        if above_sma50 and above_sma200 and adx > 25:
            return {
                "regime": "Bull",
                "label": "BULL TREND",
                "color": "#22c55e",
                "desc": "가격이 주요 이동평균선 위에서 강한 추세를 형성하고 있습니다. 상승 모멘텀 지속 중."
            }
        elif not above_sma50 and not above_sma200 and adx > 25:
            return {
                "regime": "Bear",
                "label": "BEAR TREND",
                "color": "#ef4444",
                "desc": "가격이 주요 이동평균선 아래에서 하락 추세를 보이고 있습니다. 리스크 관리 필수."
            }
        elif adx < 20:
            return {
                "regime": "VCP",
                "label": "CONSOLIDATION",
                "color": "#f59e0b",
                "desc": "변동성이 수축되며 횡보 국면에 있습니다. 방향성 돌파를 기다리는 구간."
            }
        else:
            return {
                "regime": "Transition",
                "label": "TRANSITION",
                "color": "#6366f1",
                "desc": "추세 전환 조짐이 감지됩니다. 확인 신호가 나올 때까지 보수적 접근 권장."
            }
    
    def _build_strategy_checklist(self, final_result: dict) -> list:
        """규칙 기반 전략 체크리스트 — O'Neil/Minervini 스타일"""
        med = final_result.get("medium_term", {})
        raw = med.get("full_analysis", {}).get("daily_analysis", {}).get("raw_indicators", {})
        
        close = raw.get("Close", 0)
        sma_50 = raw.get("sma_50", 0)
        sma_200 = raw.get("sma_200", 0)
        rsi = raw.get("rsi", 50)
        adx = raw.get("adx", 0)
        volume = raw.get("Volume", 0)
        macd_hist = raw.get("Hist") or raw.get("macd_hist", 0)
        
        return [
            {
                "id": "sma50",
                "text": f"가격이 50일 이동평균선 위에서 거래 중 ({close:.2f} vs {sma_50:.2f})" if close and sma_50 else "50일 이동평균선 데이터 없음",
                "status": bool(close and sma_50 and close > sma_50),
                "importance": "HIGH"
            },
            {
                "id": "sma200",
                "text": f"가격이 200일 이동평균선 위에서 거래 중" if close and sma_200 else "200일 이동평균선 데이터 없음",
                "status": bool(close and sma_200 and close > sma_200),
                "importance": "HIGH"
            },
            {
                "id": "golden_cross",
                "text": "골든크로스 형성 (SMA50 > SMA200)",
                "status": bool(sma_50 and sma_200 and sma_50 > sma_200),
                "importance": "MEDIUM"
            },
            {
                "id": "rsi_healthy",
                "text": f"RSI 건강 구간 (30~70): 현재 {rsi:.1f}" if rsi else "RSI 데이터 없음",
                "status": bool(rsi and 30 <= rsi <= 70),
                "importance": "MEDIUM"
            },
            {
                "id": "trend_strength",
                "text": f"ADX 추세 강도: {adx:.1f} (25 이상 = 유효 추세)" if adx else "ADX 데이터 없음",
                "status": bool(adx and adx > 25),
                "importance": "MEDIUM"
            },
            {
                "id": "macd_bullish",
                "text": "MACD 히스토그램 양수 (상승 모멘텀)",
                "status": bool(macd_hist and macd_hist > 0),
                "importance": "LOW"
            },
        ]

# 싱글톤 인스턴스 팩토리
_integration_service = None

def get_integration_service() -> IntegrationService:
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService()
    return _integration_service
