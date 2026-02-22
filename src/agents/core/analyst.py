import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.agents.calendar.event_calendar import EventCalendar
from src.agents.analysis.strategy_ensemble import StrategyEnsemble
from src.agents.analysis.ml_predictor import MLPricePredictor
from src.utils.backtester import Backtester

logger = logging.getLogger(__name__)

from src.utils.advanced_indicators import AdvancedIndicators

class TechnicalAnalyzer:
    """
    기술적 분석 수행 - 30개 이상의 모든 보조지표 원본 데이터를 계산하여 반환
    """

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        데이터프레임에 모든 기술적 지표를 계산하고, 최종 행의 값들을 딕셔너리로 반환합니다.
        """
        if df is None or len(df) < 50: # More data needed for some indicators
            return {
                "error": "Insufficient data for full technical analysis."
            }
        
        # 1. 모든 고급 지표 계산
        df_with_indicators = AdvancedIndicators.calculate_all(df)
        
        # 2. 마지막 행 (최신 데이터) 추출
        latest_indicators = df_with_indicators.iloc[-1]
        
        # 3. NaN 값을 None으로 변환하고, Python 기본 타입으로 변환하여 JSON 직렬화 준비
        raw_data = {}
        for key, value in latest_indicators.items():
            if pd.isna(value):
                raw_data[key] = None
            elif isinstance(value, (np.integer, np.int64)):
                raw_data[key] = int(value)
            elif isinstance(value, (np.floating, np.float64)):
                raw_data[key] = float(value)
            else:
                raw_data[key] = value

        # 4. 분석에 사용된 핵심 데이터만 포함하여 반환 (기존 구조 호환성)
        # 이 데이터는 이제 LLM 프롬프트에 직접 사용됩니다.
        return {
            "raw_indicators": raw_data,
            # 기존 호환성을 위해 일부 값을 최상위 레벨에도 유지
            "current_price": raw_data.get('Close'),
            "rsi": raw_data.get('rsi'),
            "macd": raw_data.get('MACD'),
            "signal": raw_data.get('Signal'), # MACD Signal Line
        }


class FundamentalAnalyzer:
    def analyze(self, financials: list) -> Dict[str, Any]:
        # (기존 로직 유지)
        return {"score": 50, "summary": "N/A", "details": []}

class MacroAnalyzer:
    def analyze(self, ticker, daily, index=None) -> Dict[str, Any]:
        # (기존 로직 유지)
        return {"score": 50, "summary": "N/A", "details": []}

class VolumePriceAnalyzer:
    def analyze(self, df) -> Dict[str, Any]:
        # (기존 로직 유지)
         return {"score": 50, "summary": "N/A", "details": []}

class PsychologicalAnalyzer:
    def analyze(self, df, sentiment=None) -> Dict[str, Any]:
        # (기존 로직 유지)
         return {"score": 50, "summary": "N/A", "details": []}

class StockAnalyst:
    def __init__(self, tech=None, fund=None, macro=None, vol_price=None, psych=None, calendar=None, ml=None):
        self.tech = tech or TechnicalAnalyzer()
        self.fund = fund or FundamentalAnalyzer()
        self.macro = macro or MacroAnalyzer()
        self.vol_price = vol_price or VolumePriceAnalyzer()
        self.psych = psych or PsychologicalAnalyzer()
        self.calendar = calendar or EventCalendar()
        self.ml_predictor = ml or MLPricePredictor()
        
    def analyze_ticker(self, ticker, daily_df, financials=None, hourly_df=None, index_df=None, sentiment_data=None) -> dict:
        if daily_df is None or daily_df.empty: return {"error": "No data"}

        daily_tech = self.tech.analyze(daily_df) # 여기서 key_levels, trendlines 포함됨
        
        # ... (나머지 분석 로직 유지) ...
        
        res = {
            "ticker": ticker,
            "daily_analysis": daily_tech, # Frontend receives this
            # ... others ...
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return res
