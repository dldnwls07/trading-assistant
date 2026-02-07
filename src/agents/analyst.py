import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """
    Performs technical analysis on OHLCV data.
    """
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculates Relative Strength Index."""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculates MACD, Signal, and Histogram."""
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Hist': macd - signal})

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes the latest data point.
        """
        if df is None or len(df) < 30:
            return {"score": 50, "summary": "데이터 부족"}
            
        df = df.copy()
        df['RSI'] = self.calculate_rsi(df)
        macd_df = self.calculate_macd(df)
        df = df.join(macd_df)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        
        score = 50
        reasons = []
        
        # RSI Logic
        rsi = latest['RSI']
        if rsi < 30:
            score += 20
            reasons.append(f"과매도 (RSI {rsi:.1f})")
        elif rsi > 70:
            score -= 20
            reasons.append(f"과매수 (RSI {rsi:.1f})")
            
        # MACD Logic
        if latest['MACD'] > latest['Signal']:
            score += 10
            reasons.append("MACD 골든크로스")
        else:
            score -= 10
            reasons.append("MACD 데드크로스")
            
        # Trend Logic
        if latest['Close'] > latest['SMA_20']:
            score += 10
            reasons.append("20일 이평선 상회")
        else:
            score -= 10
            reasons.append("20일 이평선 하회")
            
        # Clamp score
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "rsi": rsi,
            "macd": latest['MACD'],
            "summary": "; ".join(reasons) if reasons else "중립"
        }

class FundamentalAnalyzer:
    """
    Performs fundamental analysis based on financial statements.
    """
    
    def analyze(self, financials: list[Any]) -> Dict[str, Any]:
        """
        Analyzes list of Financials objects (from DB).
        """
        if not financials or len(financials) < 2:
            return {"score": 50, "summary": "재무 데이터 부족"}
            
        # Sort by date descending
        sorted_fin = sorted(financials, key=lambda x: x.report_date, reverse=True)
        current = sorted_fin[0]
        prev = sorted_fin[1]
        
        score = 50
        reasons = []
        
        # Revenue Growth
        if current.revenue and prev.revenue:
            growth = (current.revenue - prev.revenue) / prev.revenue
            if growth > 0.10: # > 10% growth
                score += 15
                reasons.append(f"매출 성장 {growth*100:.1f}%")
            elif growth < 0:
                score -= 15
                reasons.append(f"매출 감소 {growth*100:.1f}%")
                
        # Net Income
        if current.net_income and current.net_income > 0:
            score += 10
            reasons.append("순이익 흑자")
        elif current.net_income and current.net_income < 0:
            score -= 10
            reasons.append("순이익 적자")
            
        # EPS Growth
        if current.eps and prev.eps and prev.eps > 0:
            eps_growth = (current.eps - prev.eps) / abs(prev.eps)
            if eps_growth > 0.10:
                score += 10
                reasons.append(f"EPS 성장 {eps_growth*100:.1f}%")

        score = max(0, min(100, score))
        
        return {
            "score": score,
            "revenue": current.revenue,
            "period": current.period,
            "summary": "; ".join(reasons) if reasons else "변동 없음"
        }

class StockAnalyst:
    def __init__(self):
        self.tech = TechnicalAnalyzer()
        self.fund = FundamentalAnalyzer()
        
    def analyze_ticker(self, ticker: str, price_history: pd.DataFrame, financials: list[Any]) -> Dict[str, Any]:
        t_res = self.tech.analyze(price_history)
        f_res = self.fund.analyze(financials)
        
        # Weighted Score (60% Tech, 40% Fund for now, customizable)
        final_score = (t_res['score'] * 0.6) + (f_res['score'] * 0.4)
        
        signal = "관망 (HOLD)"
        if final_score >= 70: signal = "매수 (BUY)"
        elif final_score >= 85: signal = "강력 매수 (STRONG BUY)"
        elif final_score <= 30: signal = "매도 (SELL)"
        elif final_score <= 15: signal = "강력 매도 (STRONG SELL)"
        
        return {
            "ticker": ticker,
            "signal": signal,
            "final_score": round(final_score, 1),
            "technical": t_res,
            "fundamental": f_res
        }
