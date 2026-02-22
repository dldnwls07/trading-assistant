import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf
import asyncio
import json

from src.config import settings
from src.agents.core.analyst import StockAnalyst
from src.agents.analysis.pattern_detector import AdvancedPatternDetector
from src.agents.analysis.ai_analyzer import AIAnalyzer
from src.data.collector import MarketDataCollector
from src.utils.chart_generator import generate_chart_image

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    """
    다중 시간 프레임 종합 분석 시스템
    - v2: LLM 중심 아키텍처. 모든 분석 및 점수 계산을 AI에 위임.
    """
    
    @property
    def timeframe_config(self):
        return {
            "short": { "name": "단기 (1개월)", "data_period": "1mo", "data_interval": "1h" },
            "medium": { "name": "중기 (6개월)", "data_period": "1y", "data_interval": "1d" },
            "long": { "name": "장기 (1년+)", "data_period": "2y", "data_interval": "1wk" },
        }

    def __init__(
        self,
        analyst: StockAnalyst = None,
        pattern_detector: AdvancedPatternDetector = None,
        ai_analyzer: AIAnalyzer = None,
        collector: MarketDataCollector = None
    ):
        self.analyst = analyst or StockAnalyst()
        self.pattern_detector = pattern_detector or AdvancedPatternDetector()
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.collector = collector or MarketDataCollector()
    
    async def _fetch_vix(self) -> float:
        """VIX(^VIX) 현재값을 수집합니다. 실패 시 기본값 18 반환."""
        try:
            vix_data = await self.collector.get_ohlcv("^VIX", period="5d", interval="1d")
            if vix_data is not None and not vix_data.empty:
                vix_value = float(vix_data['Close'].iloc[-1])
                logger.info(f"📊 VIX 현재값: {vix_value:.2f}")
                return vix_value
        except Exception as e:
            logger.warning(f"VIX 데이터 수집 실패 (기본값 18 사용): {e}")
        return 18.0
    
    async def _fetch_index_data(self, index_ticker: str = "^IXIC") -> Optional[pd.DataFrame]:
        """나스닥 등 인덱스 데이터를 수집합니다 (상관관계 분석용)."""
        try:
            index_data = await self.collector.get_ohlcv(index_ticker, period="6mo", interval="1d")
            if index_data is not None and not index_data.empty:
                return index_data
        except Exception as e:
            logger.warning(f"인덱스({index_ticker}) 데이터 수집 실패: {e}")
        return None

    async def analyze_all_timeframes(self, ticker: str, index_ticker: str = "^GSPC", skip_report: bool = False) -> Dict[str, Any]:
        """모든 시간 프레임의 원본 지표를 수집하고, LLM에 분석을 요청합니다."""
        logger.info(f"🚀 {ticker} LLM-centric multi-timeframe analysis started...")
        
        # VIX + 인덱스 + 타임프레임 분석을 모두 병렬로 실행
        tasks = [
            self._analyze_timeframe(ticker, tf_key, index_ticker) 
            for tf_key in ["short", "medium", "long"]
        ]
        vix_task = self._fetch_vix()
        index_task = self._fetch_index_data("^IXIC")
        
        results = await asyncio.gather(*tasks, vix_task, index_task)
        tf_results = list(results[:3])
        vix_value = results[3]
        index_df = results[4]
        
        # Aggregate patterns and create the payload for the LLM
        all_patterns = []
        for i, res in enumerate(tf_results):
            if res and res.get('patterns'):
                for p in res['patterns']:
                    p['timeframe'] = ["short", "medium", "long"][i]
                    all_patterns.append(p)
                    
        # Extract chart image from medium timeframe result
        chart_image_bytes = tf_results[1].get("chart_image") if tf_results[1] else None

        def _extract_raw(tf_result) -> dict:
            """타임프레임 결과에서 raw_indicators를 안전하게 추출"""
            if not tf_result:
                return {}
            full = tf_result.get("full_analysis", {})
            raw = full.get("daily_analysis", {}).get("raw_indicators")
            if raw:
                return raw
            return full.get("raw_indicators") or {}

        llm_payload = {
            "ticker": ticker,
            "short_term_indicators": _extract_raw(tf_results[0]),
            "medium_term_indicators": _extract_raw(tf_results[1]),
            "long_term_indicators": _extract_raw(tf_results[2]),
            "all_patterns": all_patterns,
            "vix": vix_value,
        }
        
        final_score = 50
        final_signal = "HOLD"
        ai_report = "AI 분석 모델을 호출하는 데 실패했습니다. API 키 또는 할당량을 확인해주세요."
        
        if not skip_report:
            try:
                response_dict = self.ai_analyzer.generate_report(llm_payload, image_bytes=chart_image_bytes)
                
                final_score = int(response_dict.get("score", 50))
                final_signal = response_dict.get("signal", "HOLD")
                ai_report = response_dict.get("report", "AI가 리포트를 생성하는 데 실패했습니다.")

            except Exception as e:
                logger.error(f"Failed to process AI report: {e}", exc_info=True)
                ai_report = "AI 분석 중 오류가 발생했습니다."

        # chart_image는 내부 처리용이므로 API 응답에서 제거 (JSON serialization 에러 방지)
        for tf_result in tf_results:
            if tf_result and 'chart_image' in tf_result:
                del tf_result['chart_image']

        if isinstance(ai_report, dict):
            ai_report = ai_report.get("report", "AI 분석 리포트 생성 실패")
            logger.warning(f"ai_report was dict, extracted string: {ai_report[:100]}")

        return {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "final_score": final_score,
            "signal": final_signal,
            "full_report": ai_report,
            "short_term": tf_results[0],
            "medium_term": tf_results[1],
            "long_term": tf_results[2],
            "all_patterns": all_patterns,
            "vix": vix_value,
            "index_df_available": index_df is not None,
        }

    async def _analyze_timeframe(self, ticker: str, timeframe: str, index_ticker: str) -> Dict[str, Any]:
        config = self.timeframe_config[timeframe]
        try:
            logger.info(f"Analyzing {ticker} for {timeframe}: Fetching stock data...")
            stock_data = await self.collector.get_ohlcv(
                ticker, period=config["data_period"], interval=config["data_interval"]
            )
            if stock_data is None or stock_data.empty:
                return self._empty_result(timeframe, "Data unavailable")

            if 'Date' in stock_data.columns:
                stock_data.set_index(pd.to_datetime(stock_data['Date']), inplace=True)
            
            analysis = self.analyst.analyze_ticker(ticker=ticker, daily_df=stock_data)
            detected_patterns = self.pattern_detector.detect_all_patterns(stock_data)

            # Generate chart image for medium timeframe (to be sent to Vision AI)
            chart_img = None
            if timeframe == "medium":
                chart_img = generate_chart_image(stock_data, ticker, config["data_interval"])
            
            logger.info(f"Analyzing {ticker} for {timeframe}: Analysis complete.")
            
            # 시간 프레임별 전략 필드 생성 (프론트엔드 AnalysisInsights에서 참조)
            raw_ind = analysis.get("daily_analysis", {}).get("raw_indicators", {})
            strategy_fields = self._generate_timeframe_strategy(timeframe, raw_ind)
            
            return {
                "timeframe": timeframe,
                "name": config["name"],
                "current_price": float(stock_data['Close'].iloc[-1]),
                "patterns": detected_patterns[:5],
                "full_analysis": analysis,
                "chart_image": chart_img,
                **strategy_fields,  # recommendation, focus_areas, holding_period 포함
            }
        except Exception as e:
            logger.error(f"❌ {ticker} {timeframe} error: {e}", exc_info=True)
            return self._empty_result(timeframe, str(e))
    
    def _empty_result(self, timeframe: str, reason: str) -> Dict[str, Any]:
        return {
            "timeframe": timeframe,
            "name": self.timeframe_config[timeframe]["name"],
            "error": reason,
            "full_analysis": {"error": reason},
            "recommendation": "데이터 부족으로 분석 불가",
            "focus_areas": "데이터를 확인해주세요",
            "holding_period": "N/A",
        }
    
    def _generate_timeframe_strategy(self, timeframe: str, raw_ind: dict, vix: float = 18.0) -> Dict[str, str]:
        """
        raw_indicators + VIX 기반으로 시간 프레임별 전략 요약을 규칙 기반으로 생성합니다.
        VIX가 높을 때는 RSI 임계값을 조절하여 가짜 신호를 필터링합니다.
        LLM 호출 없이 즉시 반환되므로 할당량에 영향 없음.
        """
        if not raw_ind:
            return {
                "recommendation": "지표 데이터 부족",
                "focus_areas": "분석에 필요한 기술적 지표가 아직 계산되지 않았습니다.",
                "holding_period": "N/A",
            }
        
        rsi = raw_ind.get("rsi")
        macd_hist = raw_ind.get("Hist") or raw_ind.get("macd_hist")
        adx = raw_ind.get("adx")
        close = raw_ind.get("Close", 0)
        sma_50 = raw_ind.get("sma_50", 0)
        sma_200 = raw_ind.get("sma_200", 0)
        stoch_k = raw_ind.get("stoch_k")
        bb_upper = raw_ind.get("bb_upper", 0)
        bb_lower = raw_ind.get("bb_lower", 0)
        
        # --- VIX 적응형 RSI 임계값 ---
        # VIX가 높으면(시장 공포) → RSI 매수 임계값을 낮추고, 매도 임계값을 높임
        # 이유: 변동성 큰 장에서 일반 임계값은 가짜 신호를 양산함
        if vix > 30:
            rsi_buy_threshold = 25     # 극도의 공포
            rsi_sell_threshold = 80
        elif vix > 22:
            rsi_buy_threshold = 30     # 공포 구간
            rsi_sell_threshold = 75
        else:
            rsi_buy_threshold = 35     # 정상 구간
            rsi_sell_threshold = 70
        
        # --- 1. Recommendation (추천 전략) ---
        bullish_signals = 0
        bearish_signals = 0
        
        if rsi is not None:
            if rsi < rsi_buy_threshold: bullish_signals += 2     # VIX 적응형 과매도
            elif rsi < 45: bullish_signals += 1
            elif rsi > rsi_sell_threshold: bearish_signals += 2  # VIX 적응형 과매수
            elif rsi > 55: bearish_signals += 1
                
        if macd_hist is not None:
            if macd_hist > 0: bullish_signals += 1
            else: bearish_signals += 1
                
        if close and sma_50:
            if close > sma_50: bullish_signals += 1
            else: bearish_signals += 1
                
        if close and sma_200:
            if close > sma_200: bullish_signals += 1
            else: bearish_signals += 1

        if adx is not None and adx > 25:
            # 강한 추세 — 추세 방향대로 가중치 추가
            if bullish_signals > bearish_signals: bullish_signals += 1
            else: bearish_signals += 1

        net = bullish_signals - bearish_signals
        
        # 시간 프레임별 맥락에 맞는 추천 생성
        tf_label = {"short": "단기", "medium": "중기", "long": "장기"}.get(timeframe, timeframe)
        
        if net >= 4:
            recommendation = f"🟢 {tf_label} 강한 매수 신호. 기술적 지표가 대부분 상승을 가리키고 있어 적극적인 진입을 고려할 수 있습니다."
        elif net >= 2:
            recommendation = f"🟢 {tf_label} 매수 우위. 분할 진입 또는 눌림목 대기 전략이 유효합니다."
        elif net >= 0:
            recommendation = f"🟡 {tf_label} 중립/관망. 명확한 방향성이 부족하므로 추세 확인 후 진입을 권장합니다."
        elif net >= -2:
            recommendation = f"🔴 {tf_label} 매도 우위. 리스크 관리를 강화하고 신규 진입은 보류하세요."
        else:
            recommendation = f"🔴 {tf_label} 강한 매도 신호. 기술적 지표가 하락을 시사하며 포지션 축소 또는 손절을 고려하세요."
        
        # VIX 경고 접미사
        if vix > 30:
            recommendation += f" ⚠️ VIX {vix:.1f} — 극단적 공포 구간! 포지션 사이즈를 절반 이하로 줄이세요."
        elif vix > 22:
            recommendation += f" ⚠️ VIX {vix:.1f} — 높은 변동성 주의. 보수적 진입 권장."
        
        # --- 2. Focus Areas (주요 관찰 포인트) ---
        focus_parts = []
        
        # VIX 상태 표시 (가장 먼저)
        if vix > 30:
            focus_parts.append(f"🔥 VIX {vix:.1f} 극단 공포")
        elif vix > 22:
            focus_parts.append(f"⚠️ VIX {vix:.1f} 경계")
        else:
            focus_parts.append(f"🟢 VIX {vix:.1f} 안정")
        
        if rsi is not None:
            if rsi > rsi_sell_threshold: focus_parts.append(f"RSI {rsi:.1f} 과매수 (VIX 조정 임계: {rsi_sell_threshold})")
            elif rsi < rsi_buy_threshold: focus_parts.append(f"RSI {rsi:.1f} 과매도 (VIX 조정 임계: {rsi_buy_threshold})")
            else: focus_parts.append(f"RSI {rsi:.1f} 중립")
        
        if close and sma_50 and sma_200:
            if sma_50 > sma_200: focus_parts.append("골든크로스 유지 중")
            elif sma_50 < sma_200: focus_parts.append("데드크로스 주의")
            
            if close > sma_50: focus_parts.append("SMA50 위 거래 (상승 지지)")
            else: focus_parts.append("SMA50 하회 (약세)")
        
        if adx is not None:
            if adx > 40: focus_parts.append(f"ADX {adx:.1f} 매우 강한 추세")
            elif adx > 25: focus_parts.append(f"ADX {adx:.1f} 추세 확인")
            else: focus_parts.append(f"ADX {adx:.1f} 추세 미약/횡보")
        
        if bb_upper and bb_lower and close:
            if close > bb_upper: focus_parts.append("볼린저 상단 돌파 (과열)")
            elif close < bb_lower: focus_parts.append("볼린저 하단 이탈 (과매도)")
        
        focus_areas = " | ".join(focus_parts) if focus_parts else "기술적 지표 데이터 확인 필요"
        
        # --- 3. Holding Period (추천 보유 기간) ---
        holding_map = {
            "short": "1~5 거래일 (스윙/데이 트레이딩)",
            "medium": "2주~3개월 (포지션 트레이딩)",
            "long": "3개월~1년 이상 (투자/자산배분)",
        }
        holding_period = holding_map.get(timeframe, "N/A")
        
        return {
            "recommendation": recommendation,
            "focus_areas": focus_areas,
            "holding_period": holding_period,
        }
