import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf
import asyncio
import json

from src.config import settings
from src.agents.analyst import StockAnalyst
from src.agents.pattern_detector import AdvancedPatternDetector
from src.agents.ai_analyzer import AIAnalyzer
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
    
    async def analyze_all_timeframes(self, ticker: str, index_ticker: str = "^GSPC", skip_report: bool = False) -> Dict[str, Any]:
        """모든 시간 프레임의 원본 지표를 수집하고, LLM에 분석을 요청합니다."""
        logger.info(f"🚀 {ticker} LLM-centric multi-timeframe analysis started...")
        
        tasks = [
            self._analyze_timeframe(ticker, tf_key, index_ticker) 
            for tf_key in ["short", "medium", "long"]
        ]
        tf_results = await asyncio.gather(*tasks)
        
        # Aggregate patterns and create the payload for the LLM
        all_patterns = []
        for i, res in enumerate(tf_results):
            if res and res.get('patterns'):
                for p in res['patterns']:
                    p['timeframe'] = ["short", "medium", "long"][i]
                    all_patterns.append(p)
                    
        # Extract chart image from medium timeframe result
        chart_image_bytes = tf_results[1].get("chart_image") if tf_results[1] else None

        # analyze_ticker()는 {"daily_analysis": {"raw_indicators": {...}}, ...} 구조를 반환하므로
        # full_analysis → daily_analysis → raw_indicators 경로로 접근해야 함
        def _extract_raw(tf_result) -> dict:
            """타임프레임 결과에서 raw_indicators를 안전하게 추출"""
            if not tf_result:
                return {}
            full = tf_result.get("full_analysis", {})
            # daily_analysis 하위에 raw_indicators가 있는 경우 (analyze_ticker 반환 구조)
            raw = full.get("daily_analysis", {}).get("raw_indicators")
            if raw:
                return raw
            # 혹시 직접 raw_indicators가 있는 경우 (구버전 호환)
            return full.get("raw_indicators") or {}

        llm_payload = {
            "ticker": ticker,
            "short_term_indicators": _extract_raw(tf_results[0]),
            "medium_term_indicators": _extract_raw(tf_results[1]),
            "long_term_indicators": _extract_raw(tf_results[2]),
            "all_patterns": all_patterns,
        }
        
        final_score = 50
        final_signal = "HOLD"
        ai_report = "AI 분석 모델을 호출하는 데 실패했습니다. API 키 또는 할당량을 확인해주세요."
        
        if not skip_report:
            try:
                # generate_report가 이제 Dict[str, Any]를 반환하며, 이미지도 받음
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

        # ai_report가 딕셔너리로 잘못 저장된 경우 문자열로 변환 (React 렌더링 에러 방지)
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
            return {
                "timeframe": timeframe,
                "name": config["name"],
                "current_price": float(stock_data['Close'].iloc[-1]),
                "patterns": detected_patterns[:5],
                "full_analysis": analysis,
                "chart_image": chart_img
            }
        except Exception as e:
            logger.error(f"❌ {ticker} {timeframe} error: {e}", exc_info=True)
            return self._empty_result(timeframe, str(e))
    
    def _empty_result(self, timeframe: str, reason: str) -> Dict[str, Any]:
        return {
            "timeframe": timeframe,
            "name": self.timeframe_config[timeframe]["name"],
            "error": reason,
            "full_analysis": {"error": reason}
        }
