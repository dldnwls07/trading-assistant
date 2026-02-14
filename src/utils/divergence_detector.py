import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from scipy.signal import argrelextrema

class DivergenceDetector:
    """
    다이버전스 감지 시스템
    주가와 보조지표(RSI, MACD) 간의 괴리를 포착하여 반전 신호 생성
    """
    
    @staticmethod
    def detect_all(df: pd.DataFrame, indicator_col: str = 'RSI', window: int = 5) -> List[Dict[str, Any]]:
        """
        특정 지표와 가격 사이의 모든 다이버전스 감지
        """
        if indicator_col not in df.columns:
            return []
            
        divergences = []
        
        # 1. 고점(Peaks) 및 저점(Troughs) 추출
        prices = df['Close'].values
        indicators = df[indicator_col].values
        
        # 로컬 피크/트로프 (주변 window개 보다 크거나 작은 지점)
        price_peaks = argrelextrema(prices, np.greater, order=window)[0]
        price_troughs = argrelextrema(prices, np.less, order=window)[0]
        
        indic_peaks = argrelextrema(indicators, np.greater, order=window)[0]
        indic_troughs = argrelextrema(indicators, np.less, order=window)[0]
        
        # --- 상승 다이버전스 (Bullish) ---
        # 주가 저점은 낮아지는데, 지표 저점은 높아지는 경우 (일반)
        # 주가 저점은 높아지는데, 지표 저점은 낮아지는 경우 (히든)
        if len(price_troughs) >= 2:
            for i in range(len(price_troughs) - 1):
                p1, p2 = price_troughs[i], price_troughs[i+1]
                
                # 지표에도 해당 기간 근처에 저점이 있는지 확인
                # 지표 저점 중 p1, p2와 가장 가까운 지점 찾기
                i1_candidates = [it for it in indic_troughs if abs(it - p1) <= 2]
                i2_candidates = [it for it in indic_troughs if abs(it - p2) <= 2]
                
                if not i1_candidates or not i2_candidates:
                    continue
                
                i1, i2 = i1_candidates[-1], i2_candidates[-1]
                
                # 일반 상승 다이버전스 (Regular Bullish) - 반전
                if prices[p1] > prices[p2] and indicators[i1] < indicators[i2]:
                    divergences.append({
                        "type": "Regular Bullish",
                        "indicator": indicator_col,
                        "p1_idx": int(p1), "p2_idx": int(p2),
                        "p1_price": float(prices[p1]), "p2_price": float(prices[p2]),
                        "p1_indic": float(indicators[i1]), "p2_indic": float(indicators[i2]),
                        "strength": "Strong" if indicators[i1] < 30 else "Normal",
                        "message": f"주가는 하락했으나 {indicator_col} 저점은 상승했습니다. 하락 추세 반전(상승)이 기대됩니다."
                    })
                
                # 히든 상승 다이버전스 (Hidden Bullish) - 지속
                elif prices[p1] < prices[p2] and indicators[i1] > indicators[i2]:
                    divergences.append({
                        "type": "Hidden Bullish",
                        "indicator": indicator_col,
                        "p1_idx": int(p1), "p2_idx": int(p2),
                        "strength": "Medium",
                        "message": f"주가 저점은 높아졌으나 {indicator_col} 저점은 낮아졌습니다. 기존 상승 추세가 강력하게 유지될 것으로 보입니다."
                    })

        # --- 하락 다이버전스 (Bearish) ---
        if len(price_peaks) >= 2:
            for i in range(len(price_peaks) - 1):
                p1, p2 = price_peaks[i], price_peaks[i+1]
                
                i1_candidates = [ip for ip in indic_peaks if abs(ip - p1) <= 2]
                i2_candidates = [ip for ip in indic_peaks if abs(ip - p2) <= 2]
                
                if not i1_candidates or not i2_candidates:
                    continue
                
                i1, i2 = i1_candidates[-1], i2_candidates[-1]
                
                # 일반 하락 다이버전스 (Regular Bearish) - 반전
                if prices[p1] < prices[p2] and indicators[i1] > indicators[i2]:
                    divergences.append({
                        "type": "Regular Bearish",
                        "indicator": indicator_col,
                        "p1_idx": int(p1), "p2_idx": int(p2),
                        "strength": "Strong" if indicators[i1] > 70 else "Normal",
                        "message": f"주가는 상승했으나 {indicator_col} 고점은 낮아졌습니다. 상승 추세 약화 및 하락 반전이 경고됩니다."
                    })
                
                # 히든 하락 다이버전스 (Hidden Bearish) - 지속
                elif prices[p1] > prices[p2] and indicators[i1] < indicators[i2]:
                    divergences.append({
                        "type": "Hidden Bearish",
                        "indicator": indicator_col,
                        "p1_idx": int(p1), "p2_idx": int(p2),
                        "strength": "Medium",
                        "message": f"주가 고점은 낮아졌으나 {indicator_col} 고점은 높아졌습니다. 하락 추세가 지속될 가능성이 높습니다."
                    })

        return divergences

    @staticmethod
    def get_summary_score(divergences: List[Dict[str, Any]]) -> int:
        """다이버전스 목록을 바탕으로 가중치 점수 계산 (중립 0 기준)"""
        score = 0
        for div in divergences:
            weight = 15 if div['strength'] == "Strong" else 10
            if "Bullish" in div['type']:
                score += weight
            else:
                score -= weight
        return score
