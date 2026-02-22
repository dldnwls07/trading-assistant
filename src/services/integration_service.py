import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from src.config import settings
from src.data.collector import MarketDataCollector
from src.agents.core.analyst import StockAnalyst
from src.agents.analysis.multi_timeframe import MultiTimeframeAnalyzer
from src.agents.analysis.ml_predictor import MLPricePredictor
from src.agents.analysis.ai_analyzer import AIAnalyzer
from src.agents.analysis.strategy_ensemble import StrategyEnsemble
from src.utils.backtester import Backtester

logger = logging.getLogger(__name__)

from src.data.storage import get_storage
from src.data.parser import FinancialParser
from src.agents.analysis.ai_analyzer import get_stock_events

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
            
            # 2. 나스닥 인덱스 데이터 수집 (상관관계 분석용)
            index_task = self.collector.get_ohlcv("^IXIC", period="6mo", interval="1d")
            
            # 3. 분석 태스크 병렬 실행
            # ticker를 함께 전달해야 레버리지 ETF 감지 로직이 작동함
            ml_task = asyncio.to_thread(self.ml_predictor.predict_next, daily_df, ticker)
            events_task = asyncio.to_thread(get_stock_events, ticker)
            multi_res_task = self.multi_analyzer.analyze_all_timeframes(ticker)
            
            ml_res, events, multi_res, index_df = await asyncio.gather(
                ml_task, events_task, multi_res_task, index_task
            )
            
            # VIX 값은 multi_res에서 가져옴 (multi_timeframe에서 이미 수집)
            vix_value = multi_res.get("vix", 18.0)
            
            # 상관계수 계산 (종목 vs 나스닥)
            correlation = self._calculate_correlation(daily_df, index_df)
            
            # 4. 결과 통합 및 가공
            final_result = {
                **multi_res,
                "ml_prediction": ml_res,
                "events": events or {},
                "fundamental_summary": multi_res.get("medium_term", {}).get("full_analysis", {}).get("fundamental", {}),
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "vix": vix_value,
                "correlation": correlation,
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
                backtest_res = await self._run_backtest(daily_df, vix=vix_value)
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
    
    async def _run_backtest(self, daily_df, vix: float = 18.0) -> Dict[str, Any]:
        """VIX 적응형 RSI 백테스트 — VIX가 높으면 매수/매도 임계값 조정"""
        import pandas as pd
        from src.utils.advanced_indicators import AdvancedIndicators
        
        df = AdvancedIndicators.calculate_all(daily_df.copy())
        
        # VIX 적응형 RSI 임계값
        if vix > 30:
            buy_threshold, sell_threshold = 25, 80
        elif vix > 22:
            buy_threshold, sell_threshold = 30, 75
        else:
            buy_threshold, sell_threshold = 35, 70
        
        # VIX 적응형 RSI 매매 신호 생성
        signals = pd.Series(0, index=df.index)
        if "rsi" in df.columns:
            signals[df["rsi"] < buy_threshold] = 1    # 매수
            signals[df["rsi"] > sell_threshold] = -1   # 매도
        
        result = Backtester.backtest_vectorized(df, signals)
        result["vix_adjusted"] = True
        result["rsi_thresholds"] = {"buy": buy_threshold, "sell": sell_threshold}
        return result
    
    def _calculate_correlation(self, stock_df, index_df) -> Dict[str, Any]:
        """종목과 인덱스의 상관계수를 계산하여 동반하락 vs 개별조정 구분"""
        try:
            if index_df is None or index_df.empty or stock_df is None or stock_df.empty:
                return {"value": None, "regime": "unknown", "desc": "인덱스 데이터 불가"}
            
            # 수익률 기반 상관계수 (60일)
            stock_returns = stock_df['Close'].pct_change().dropna().tail(60)
            index_returns = index_df['Close'].pct_change().dropna().tail(60)
            
            # 날짜 인덱스가 다를 수 있으므로 inner join
            import pandas as pd
            combined = pd.DataFrame({
                "stock": stock_returns,
                "index": index_returns
            }).dropna()
            
            if len(combined) < 20:
                return {"value": None, "regime": "insufficient_data", "desc": "상관관계 계산에 충분한 데이터 없음"}
            
            corr = float(combined["stock"].corr(combined["index"]))
            
            if corr > 0.85:
                regime = "high_correlation"
                desc = f"나스닥과 상관계수 {corr:.2f} — 동반 하락/상승 가능성 높음. 시장 전체 방향에 민감."
            elif corr > 0.5:
                regime = "moderate_correlation"
                desc = f"나스닥과 상관계수 {corr:.2f} — 시장과 일정 수준 연동되나 독립적 움직임 가능."
            else:
                regime = "low_correlation"
                desc = f"나스닥과 상관계수 {corr:.2f} — 시장 독립형 종목. 개별 조정/상승 국면."
            
            return {"value": round(corr, 3), "regime": regime, "desc": desc}
            
        except Exception as e:
            logger.warning(f"상관관계 계산 실패: {e}")
            return {"value": None, "regime": "error", "desc": str(e)}
    
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
        """ADX, SMA, VIX, 상관관계를 종합하여 시장 국면 판정"""
        med = final_result.get("medium_term", {})
        raw = med.get("full_analysis", {}).get("daily_analysis", {}).get("raw_indicators", {})
        
        adx = raw.get("adx", 0)
        close = raw.get("Close", 0)
        sma_50 = raw.get("sma_50", 0)
        sma_200 = raw.get("sma_200", 0)
        vix = final_result.get("vix", 18.0)
        corr_data = final_result.get("correlation", {})
        corr_value = corr_data.get("value")
        
        above_sma50 = close > sma_50 if (close and sma_50) else False
        above_sma200 = close > sma_200 if (close and sma_200) else False
        
        # 상관관계 정보 접미사 생성
        corr_suffix = ""
        if corr_value is not None:
            if corr_value > 0.85:
                corr_suffix = f" 나스닥 상관계수 {corr_value:.2f} (높음 — 시장 동반 움직임)."
            elif corr_value > 0.5:
                corr_suffix = f" 나스닥 상관계수 {corr_value:.2f} (보통 — 독립적 움직임 가능)."
            else:
                corr_suffix = f" 나스닥 상관계수 {corr_value:.2f} (낮음 — 개별 요인에 의한 움직임)."
        
        # VIX 경고 접미사
        vix_suffix = ""
        if vix > 30:
            vix_suffix = f" ⚠️ VIX {vix:.1f} 극단적 공포 — 시장 급변 가능성."
        elif vix > 22:
            vix_suffix = f" ⚠️ VIX {vix:.1f} 경계 구간 — 변동성 확대."
        
        if above_sma50 and above_sma200 and adx > 25:
            return {
                "regime": "Bull",
                "label": "BULL TREND",
                "color": "#22c55e",
                "desc": f"가격이 주요 이동평균선 위에서 강한 추세를 형성하고 있습니다. 상승 모멘텀 지속 중.{corr_suffix}{vix_suffix}"
            }
        elif not above_sma50 and not above_sma200 and adx > 25:
            # 상관관계가 높으면 '시장 동반 하락', 낮으면 '개별 약세'
            if corr_value and corr_value > 0.85:
                bear_detail = "시장 전체 하락에 동반된 '동반 하락' 국면입니다."
            else:
                bear_detail = "종목 고유의 약세 요인에 의한 '개별 조정' 국면입니다."
            return {
                "regime": "Bear",
                "label": "BEAR TREND",
                "color": "#ef4444",
                "desc": f"가격이 주요 이동평균선 아래에서 하락 추세. {bear_detail}{corr_suffix}{vix_suffix}"
            }
        elif adx < 20:
            return {
                "regime": "VCP",
                "label": "CONSOLIDATION",
                "color": "#f59e0b",
                "desc": f"변동성이 수축되며 횡보 국면에 있습니다. 방향성 돌파를 기다리는 구간.{corr_suffix}{vix_suffix}"
            }
        else:
            return {
                "regime": "Transition",
                "label": "TRANSITION",
                "color": "#6366f1",
                "desc": f"추세 전환 조짐이 감지됩니다. 확인 신호가 나올 때까지 보수적 접근 권장.{corr_suffix}{vix_suffix}"
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
        vix = final_result.get("vix", 18.0)
        
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
            {
                "id": "vix_safe",
                "text": f"VIX 안정 구간 (<22): 현재 {vix:.1f}" if vix else "VIX 데이터 없음",
                "status": bool(vix and vix < 22),
                "importance": "HIGH"
            },
        ]

# 싱글톤 인스턴스 팩토리
_integration_service = None

def get_integration_service() -> IntegrationService:
    global _integration_service
    if _integration_service is None:
        _integration_service = IntegrationService()
    return _integration_service
