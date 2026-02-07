import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """
    기술적 분석 수행 - RSI, MACD, 볼린저밴드, 이동평균선 분석
    """
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """RSI (상대강도지수) 계산"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """MACD 계산"""
        exp12 = data['Close'].ewm(span=12, adjust=False).mean()
        exp26 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        return pd.DataFrame({'MACD': macd, 'Signal': signal, 'Hist': macd - signal})

    def calculate_bollinger(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """볼린저 밴드 계산"""
        sma = data['Close'].rolling(window=window).mean()
        std = data['Close'].rolling(window=window).std()
        return pd.DataFrame({
            'BB_Upper': sma + (std * 2),
            'BB_Middle': sma,
            'BB_Lower': sma - (std * 2)
        })

    def find_support_resistance(self, data: pd.DataFrame) -> Dict[str, float]:
        """지지선/저항선 계산 (최근 60일 기준)"""
        recent = data.tail(60)
        return {
            'resistance': recent['High'].max(),
            'support': recent['Low'].min(),
            'pivot': (recent['High'].max() + recent['Low'].min() + recent['Close'].iloc[-1]) / 3
        }

    def detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """주요 차트 패턴 감지 (쌍바닥, 삼각형 등)"""
        patterns = []
        if len(df) < 60:
            return patterns
            
        close = df['Close'].values
        low = df['Low'].values
        high = df['High'].values
        
        # 1. 쌍바닥 (Double Bottom) 감지
        # 최근 40일 내의 저점 2개가 비슷한 수준인지 확인
        window = 40
        recent_lows = df['Low'].tail(window)
        # 국소 저점 찾기 (간단한 방식)
        l_min1_idx = recent_lows.iloc[:window//2].idxmin()
        l_min2_idx = recent_lows.iloc[window//2:].idxmin()
        
        val1 = df.loc[l_min1_idx, 'Low']
        val2 = df.loc[l_min2_idx, 'Low']
        
        # 두 저점의 가격 차이가 2% 이내이고, 그 사이 고점이 저점보다 높을 때
        if abs(val1 - val2) / val1 < 0.02:
            mid_slice = df.loc[l_min1_idx:l_min2_idx, 'High']
            if not mid_slice.empty and mid_slice.max() > max(val1, val2) * 1.02:
                patterns.append({
                    "name": "쌍바닥 (Double Bottom)",
                    "type": "bullish_reversal",
                    "confidence": 0.8,
                    "desc": "📉 가격이 비슷한 두 지점에서 반등했습니다. 강한 바닥 신호입니다."
                })

        # 2. 상승 삼각형 (Ascending Triangle) 감지
        # 고점은 일정하고 저점은 높아지는 패턴
        recent = df.tail(30)
        highs = recent['High'].values
        lows = recent['Low'].values
        
        # 저점 추세 확인 (선형 회귀 대신 간단한 비교)
        low_trend = (lows[-1] > lows[0]) and (lows[len(lows)//2] > lows[0])
        # 고점 정체 확인
        high_std = np.std(highs) / np.mean(highs)
        
        if low_trend and high_std < 0.015:
            patterns.append({
                "name": "상승 삼각형 (Ascending Triangle)",
                "type": "bullish_continuation",
                "confidence": 0.7,
                "desc": "📐 고저항선은 일정하고 저점이 높아지고 있습니다. 상향 돌파 가능성이 높습니다."
            })
            
        return patterns

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """상세 기술적 분석 수행"""
        if df is None or len(df) < 30:
            return {"score": 50, "summary": "데이터 부족", "details": [], "entry_points": {}}
            
        df = df.copy()
        df['RSI'] = self.calculate_rsi(df)
        macd_df = self.calculate_macd(df)
        df = df.join(macd_df)
        bb_df = self.calculate_bollinger(df)
        df = df.join(bb_df)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        current_price = latest['Close']
        
        score = 50
        reasons = []
        details = []
        
        # === RSI 분석 ===
        rsi = latest['RSI']
        if rsi < 30:
            score += 20
            reasons.append(f"강한 과매도 (RSI {rsi:.1f})")
            details.append(f"📈 RSI가 {rsi:.1f}로 30 이하입니다. 과매도 구간으로 반등 가능성이 높습니다.")
        elif rsi < 40:
            score += 10
            reasons.append(f"과매도 접근 (RSI {rsi:.1f})")
            details.append(f"📊 RSI가 {rsi:.1f}로 과매도 구간에 접근 중입니다. 매수 타이밍을 지켜보세요.")
        elif rsi > 70:
            score -= 20
            reasons.append(f"강한 과매수 (RSI {rsi:.1f})")
            details.append(f"📉 RSI가 {rsi:.1f}로 70 이상입니다. 과매수 구간으로 조정 가능성이 있습니다.")
        elif rsi > 60:
            score -= 5
            reasons.append(f"과매수 접근 (RSI {rsi:.1f})")
            details.append(f"⚠️ RSI가 {rsi:.1f}로 과매수 구간에 접근 중입니다.")
        else:
            details.append(f"✅ RSI가 {rsi:.1f}로 중립 구간입니다.")
            
        # === MACD 분석 ===
        macd_val = latest['MACD']
        signal_val = latest['Signal']
        prev_macd = prev['MACD']
        prev_signal = prev['Signal']
        
        # 골든크로스/데드크로스 감지
        if prev_macd <= prev_signal and macd_val > signal_val:
            score += 15
            reasons.append("MACD 골든크로스 발생!")
            details.append(f"🚀 MACD가 시그널선을 상향 돌파했습니다 (골든크로스). 강한 매수 신호입니다!")
        elif prev_macd >= prev_signal and macd_val < signal_val:
            score -= 15
            reasons.append("MACD 데드크로스 발생!")
            details.append(f"⚠️ MACD가 시그널선을 하향 돌파했습니다 (데드크로스). 매도 신호로 해석됩니다.")
        elif macd_val > signal_val:
            score += 5
            reasons.append("MACD 상승 추세")
            details.append(f"📈 MACD({macd_val:.2f})가 시그널({signal_val:.2f}) 위에서 유지 중입니다.")
        else:
            score -= 5
            reasons.append("MACD 하락 추세")
            details.append(f"📉 MACD({macd_val:.2f})가 시그널({signal_val:.2f}) 아래에 있습니다.")
            
        # === 볼린저 밴드 분석 ===
        bb_upper = latest['BB_Upper']
        bb_lower = latest['BB_Lower']
        
        if current_price <= bb_lower:
            score += 15
            reasons.append("볼린저 하단 터치")
            details.append(f"💡 현재가({current_price:,.0f})가 볼린저 하단({bb_lower:,.0f})에 도달했습니다. 반등 매수 타점입니다.")
        elif current_price >= bb_upper:
            score -= 10
            reasons.append("볼린저 상단 터치")
            details.append(f"⚠️ 현재가({current_price:,.0f})가 볼린저 상단({bb_upper:,.0f})에 도달했습니다. 단기 조정 가능성.")
            
        # === 이동평균선 분석 ===
        sma_20 = latest['SMA_20']
        sma_50 = latest.get('SMA_50', None)
        sma_200 = latest.get('SMA_200', None)
        
        if current_price > sma_20:
            score += 5
            reasons.append("20일선 상회")
        else:
            score -= 5
            reasons.append("20일선 하회")
            
        # 정배열/역배열 체크
        if sma_50 and sma_200 and not pd.isna(sma_50) and not pd.isna(sma_200):
            if current_price > sma_20 > sma_50 > sma_200:
                score += 10
                reasons.append("완벽한 정배열")
                details.append(f"🔥 이동평균선이 완벽한 정배열 상태입니다 (현재가 > 20일 > 50일 > 200일). 강한 상승 추세!")
            elif current_price < sma_20 < sma_50 < sma_200:
                score -= 10
                reasons.append("역배열 상태")
                details.append(f"❄️ 이동평균선이 역배열 상태입니다. 하락 추세 지속 가능성이 높습니다.")
        
        # === 차트 패턴 분석 ===
        patterns = self.detect_patterns(df)
        if patterns:
            details.append(f"\n🧩 **포착된 차트 패턴**")
            for p in patterns:
                reasons.append(p['name'])
                details.append(f"   • {p['name']}: {p['desc']}")
                # 패턴 유형에 따른 가중치 부여
                if p['type'] == "bullish_reversal" or p['type'] == "bullish_continuation":
                    score += 15
                elif p['type'] == "bearish":
                    score -= 15
        
        # === 지지선/저항선 계산 ===
        levels = self.find_support_resistance(df)
        
        # === 매수/매도 타점 계산 ===
        entry_points = {
            'buy_target_1': bb_lower,
            'buy_target_2': levels['support'],
            'sell_target_1': bb_upper,
            'sell_target_2': levels['resistance'],
            'stop_loss': levels['support'] * 0.97,  # 지지선 -3%
            'current_price': current_price
        }
        
        # 타점 설명 추가
        details.append(f"\n📍 **매수 타점 제안**")
        details.append(f"   • 1차 매수: {entry_points['buy_target_1']:,.0f} (볼린저 하단)")
        details.append(f"   • 2차 매수: {entry_points['buy_target_2']:,.0f} (지지선)")
        details.append(f"   • 손절가: {entry_points['stop_loss']:,.0f} (지지선 -3%)")
        details.append(f"\n📍 **매도 타점 제안**")
        details.append(f"   • 1차 매도: {entry_points['sell_target_1']:,.0f} (볼린저 상단)")
        details.append(f"   • 2차 매도: {entry_points['sell_target_2']:,.0f} (저항선)")
        
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "rsi": rsi,
            "macd": macd_val,
            "current_price": current_price,
            "summary": "; ".join(reasons) if reasons else "중립",
            "details": details,
            "entry_points": entry_points
        }

class FundamentalAnalyzer:
    """
    기본적 분석 - 재무제표 기반 분석
    """
    
    def analyze(self, financials: list[Any]) -> Dict[str, Any]:
        """재무제표 분석"""
        if not financials or len(financials) < 2:
            return {"score": 50, "summary": "재무 데이터 부족", "details": []}
            
        sorted_fin = sorted(financials, key=lambda x: x.report_date, reverse=True)
        current = sorted_fin[0]
        prev = sorted_fin[1]
        
        score = 50
        reasons = []
        details = []
        
        # 매출 성장
        if current.revenue and prev.revenue and prev.revenue != 0:
            growth = (current.revenue - prev.revenue) / abs(prev.revenue)
            if growth > 0.20:
                score += 20
                reasons.append(f"매출 급성장 +{growth*100:.1f}%")
                details.append(f"🚀 매출이 전년 대비 {growth*100:.1f}% 급성장했습니다. 매우 긍정적!")
            elif growth > 0.10:
                score += 15
                reasons.append(f"매출 성장 +{growth*100:.1f}%")
                details.append(f"📈 매출이 전년 대비 {growth*100:.1f}% 성장했습니다.")
            elif growth < -0.10:
                score -= 15
                reasons.append(f"매출 급감 {growth*100:.1f}%")
                details.append(f"📉 매출이 전년 대비 {growth*100:.1f}% 감소했습니다. 주의 필요.")
            elif growth < 0:
                score -= 5
                reasons.append(f"매출 감소 {growth*100:.1f}%")
                
        # 순이익
        if current.net_income:
            if current.net_income > 0:
                score += 10
                reasons.append("순이익 흑자")
                if prev.net_income and prev.net_income < 0:
                    score += 10
                    details.append(f"🎉 흑자 전환! 적자에서 흑자로 전환되었습니다.")
                else:
                    details.append(f"✅ 순이익 {current.net_income/1e9:.1f}B 흑자 유지 중입니다.")
            else:
                score -= 10
                reasons.append("순이익 적자")
                details.append(f"⚠️ 현재 순이익이 적자입니다. 실적 개선 여부를 지켜봐야 합니다.")
                
        # EPS 성장
        if current.eps and prev.eps and prev.eps != 0:
            eps_growth = (current.eps - prev.eps) / abs(prev.eps)
            if eps_growth > 0.15:
                score += 10
                reasons.append(f"EPS 성장 +{eps_growth*100:.1f}%")
                details.append(f"💰 주당순이익(EPS)이 {eps_growth*100:.1f}% 성장했습니다.")
            elif eps_growth < -0.15:
                score -= 10
                reasons.append(f"EPS 하락 {eps_growth*100:.1f}%")

        score = max(0, min(100, score))
        
        return {
            "score": score,
            "revenue": current.revenue,
            "period": current.period,
            "summary": "; ".join(reasons) if reasons else "변동 없음",
            "details": details
        }

class StockAnalyst:
    """
    종합 분석 엔진 - 기술적 + 기본적 분석 통합
    """
    def __init__(self):
        self.tech = TechnicalAnalyzer()
        self.fund = FundamentalAnalyzer()
        
    def analyze_ticker(self, ticker: str, price_history: pd.DataFrame, financials: list[Any]) -> Dict[str, Any]:
        t_res = self.tech.analyze(price_history)
        f_res = self.fund.analyze(financials)
        
        # 가중 점수 (기술 60%, 기본 40%)
        final_score = (t_res['score'] * 0.6) + (f_res['score'] * 0.4)
        
        # 신호 결정 (순서 수정: 높은 점수부터 체크)
        if final_score >= 85:
            signal = "🔥 강력 매수"
            signal_desc = "기술적/기본적 지표 모두 매우 긍정적입니다. 적극 매수를 고려하세요."
        elif final_score >= 70:
            signal = "📈 매수"
            signal_desc = "긍정적인 신호가 우세합니다. 분할 매수를 고려해보세요."
        elif final_score >= 55:
            signal = "🟡 관망"
            signal_desc = "뚜렷한 방향성이 없습니다. 추가 신호를 기다리세요."
        elif final_score >= 40:
            signal = "⚠️ 주의"
            signal_desc = "부정적 신호가 나타나고 있습니다. 신규 매수를 자제하세요."
        elif final_score >= 25:
            signal = "📉 매도"
            signal_desc = "하락 신호가 우세합니다. 보유 시 손절/익절을 고려하세요."
        else:
            signal = "🔻 강력 매도"
            signal_desc = "강한 하락 신호입니다. 즉시 포지션 정리를 권장합니다."
        
        # 상세 리포트 생성
        full_report = []
        full_report.append(f"═══════════════════════════════════════")
        full_report.append(f"📊 {ticker} 종합 분석 리포트")
        full_report.append(f"═══════════════════════════════════════")
        full_report.append(f"")
        full_report.append(f"🎯 종합 판단: {signal}")
        full_report.append(f"📊 종합 점수: {final_score:.1f}/100")
        full_report.append(f"")
        full_report.append(f"💡 {signal_desc}")
        full_report.append(f"")
        full_report.append(f"───────────────────────────────────────")
        full_report.append(f"📈 기술적 분석 (점수: {t_res['score']}/100)")
        full_report.append(f"───────────────────────────────────────")
        for detail in t_res.get('details', []):
            full_report.append(detail)
        full_report.append(f"")
        full_report.append(f"───────────────────────────────────────")
        full_report.append(f"📋 기본적 분석 (점수: {f_res['score']}/100)")
        full_report.append(f"───────────────────────────────────────")
        for detail in f_res.get('details', []):
            full_report.append(detail)
        
        return {
            "ticker": ticker,
            "signal": signal,
            "signal_desc": signal_desc,
            "final_score": round(final_score, 1),
            "technical": t_res,
            "fundamental": f_res,
            "full_report": "\n".join(full_report),
            "entry_points": t_res.get('entry_points', {})
        }
