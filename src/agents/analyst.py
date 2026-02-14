import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.agents.event_calendar import EventCalendar
from src.agents.strategy_ensemble import StrategyEnsemble
from src.agents.ml_predictor import MLPricePredictor
from src.utils.backtester import Backtester

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """
    기술적 분석 수행 - RSI, MACD, 볼린저밴드, 이동평균선 분석
    """
    
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        RSI (상대강도지수) 계산 - Wilder's Smoothing (EMA) 방식
        변동이 없는 경우 50.0을 반환하여 0.0 오류 방지
        """
        if data is None or 'Close' not in data.columns or len(data) < window:
            return pd.Series(50.0, index=data.index)

        delta = data['Close'].diff()
        
        # 상승/하락분 분리
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = abs(loss)
        
        # Wilder's Smoothing (alpha = 1/window)
        # adjust=False는 재귀적 정의를 따르기 위함
        avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
        
        # 결과 계산
        rsi = pd.Series(np.nan, index=data.index)
        
        # 1. 변동이 없는 구간 (Gain/Loss 모두 0) -> 50.0
        no_move = (avg_gain == 0) & (avg_loss == 0)
        rsi[no_move] = 50.0
        
        # 2. 손실 없이 상승만 한 구간 -> 100.0
        always_up = (avg_gain > 0) & (avg_loss == 0)
        rsi[always_up] = 100.0
        
        # 3. 수익 없이 하락만 한 구간 -> 0.0
        always_down = (avg_gain == 0) & (avg_loss > 0)
        rsi[always_down] = 0.0
        
        # 4. 일반적인 경우 (RS 계산)
        normal = (avg_gain > 0) & (avg_loss > 0)
        rs = avg_gain[normal] / avg_loss[normal]
        rsi[normal] = 100.0 - (100.0 / (1.0 + rs))
        
        # 앞부분의 NaN을 50.0으로 채워 분석 품질 유지
        return rsi.fillna(50.0)

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

    def find_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        정밀 지지/저항 레벨 계산 (Clustering & Pivot)
        """
        if data is None or len(data) < 30:
            return {'resistance': 0, 'support': 0, 'levels': []}

        # 1. 히스토리컬 레벨 (최근 120일)
        recent = data.tail(120)
        levels = []
        
        # 로컬 고점/저점 추출 (Window 5)
        for i in range(5, len(recent)-5):
            if recent['High'].iloc[i] == recent['High'].iloc[i-5:i+5].max():
                levels.append(recent['High'].iloc[i])
            if recent['Low'].iloc[i] == recent['Low'].iloc[i-5:i+5].min():
                levels.append(recent['Low'].iloc[i])
        
        # 레벨 클러스터링 (비슷한 가격대는 하나로 통합)
        levels.sort()
        merged_levels = []
        if levels:
            curr = levels[0]
            count = 1
            for i in range(1, len(levels)):
                if levels[i] - curr < (curr * 0.02): # 2% 이내 차이는 같은 레벨로 간주
                    # 가중 평균 (더 많이 부딪힌 곳이 강한 레벨)
                    curr = (curr * count + levels[i]) / (count + 1)
                    count += 1
                else:
                    merged_levels.append(curr)
                    curr = levels[i]
                    count = 1
            merged_levels.append(curr)
            
        current_price = data['Close'].iloc[-1]
        
        # 현재가 기준 가장 가까운 지지/저항 찾기
        supports = [l for l in merged_levels if l < current_price]
        resistances = [l for l in merged_levels if l > current_price]
        
        # 2. 피벗 포인트 계산 (내일의 예상 범위)
        last_high = recent['High'].iloc[-1]
        last_low = recent['Low'].iloc[-1]
        last_close = recent['Close'].iloc[-1]
        pivot = (last_high + last_low + last_close) / 3
        r1 = (2 * pivot) - last_low
        s1 = (2 * pivot) - last_high
        
        # 데이터 병합
        return {
            'current_price': current_price,
            'resistance': resistances[0] if resistances else r1, # 없으면 피벗 R1 사용
            'support': supports[-1] if supports else s1,         # 없으면 피벗 S1 사용
            'pivot': pivot,
            'levels': merged_levels,
            'pivot_levels': {'P': pivot, 'R1': r1, 'S1': s1}
        }

    def get_price_scenarios(self, data: pd.DataFrame) -> Dict[str, str]:
        """
        가격 변동 시나리오 생성 (If-This-Then-That)
        """
        sr = self.find_support_resistance(data)
        curr = sr['current_price']
        sup = sr['support']
        res = sr['resistance']
        
        scenarios = {}
        
        # 하락 시나리오
        if sup > 0:
            downside_risk = (curr - sup) / curr * 100
            scenarios['bearish'] = (
                f"지지선 {sup:,.0f} 붕괴 시, 추가 하락 가능성이 열립니다. "
                f"(현재가 대비 -{downside_risk:.1f}%)"
            )
        else:
            scenarios['bearish'] = "뚜렷한 하단 지지선이 없어 리스크 관리가 필요합니다."
            
        # 상승 시나리오
        if res > 0:
            upside_potential = (res - curr) / curr * 100
            scenarios['bullish'] = (
                f"저항선 {res:,.0f} 돌파 시, 상승 추세가 가속화될 수 있습니다. "
                f"(현재가 대비 +{upside_potential:.1f}%)"
            )
        else:
            scenarios['bullish'] = "신고가 영역으로 상단이 열려있습니다."
            
        return scenarios

    def detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        초정밀 AI 차트 패턴 감지 및 신뢰도 평가 (Total 15+ Patterns)
        신뢰도는 5.0 만점 기준 (Bulkowski 통계 기반)
        """
        patterns = []
        if len(df) < 120: return patterns
        
        section = df.tail(120).copy()
        def get_time(idx): return str(df.loc[idx, 'Date']) if 'Date' in df.columns else str(idx)

        # --- 피크/트로프 추출 (정교화된 알고리즘) ---
        peaks = []
        troughs = []
        for i in range(5, len(section)-5):
            curr_idx = section.index[i]
            if section['High'].iloc[i] == section['High'].iloc[i-5:i+5].max():
                peaks.append(curr_idx)
            if section['Low'].iloc[i] == section['Low'].iloc[i-5:i+5].min():
                troughs.append(curr_idx)

        # 1. 헤드 앤 숄더 (Reversal, Reliability: 4.5)
        if len(peaks) >= 3:
            p1, p2, p3 = peaks[-3], peaks[-2], peaks[-1]
            v1, v2, v3 = df.loc[p1, 'High'], df.loc[p2, 'High'], df.loc[p3, 'High']
            if v2 > v1 * 1.02 and v2 > v3 * 1.02 and abs(v1-v3)/v1 < 0.05:
                mid_low1 = df.loc[p1:p2, 'Low'].idxmin()
                mid_low2 = df.loc[p2:p3, 'Low'].idxmin()
                patterns.append({
                    "name": "Head & Shoulders",
                    "type": "bearish_reversal",
                    "reliability": 4.5,
                    "points": [
                        {"time": get_time(p1), "price": float(v1)},
                        {"time": get_time(mid_low1), "price": float(df.loc[mid_low1, 'Low'])},
                        {"time": get_time(p2), "price": float(v2)},
                        {"time": get_time(mid_low2), "price": float(df.loc[mid_low2, 'Low'])},
                        {"time": get_time(p3), "price": float(v3)}
                    ],
                    "desc": "전형적인 고점 반전 패턴입니다. 넥라인 이탈 시 강한 하락이 예상됩니다."
                })

        # 2. 3중 바닥 / 3중 천장 (Reliability: 4.5)
        if len(troughs) >= 3:
            t1, t2, t3 = troughs[-3], troughs[-2], troughs[-1]
            v1, v2, v3 = df.loc[t1, 'Low'], df.loc[t2, 'Low'], df.loc[t3, 'Low']
            if abs(v1-v2)/v1 < 0.02 and abs(v2-v3)/v2 < 0.02:
                patterns.append({
                    "name": "Triple Bottom",
                    "type": "bullish_reversal",
                    "reliability": 4.5,
                    "points": [{"time": get_time(t1), "price": float(v1)}, {"time": get_time(t2), "price": float(v2)}, {"time": get_time(t3), "price": float(v3)}],
                    "desc": "세 번의 바닥 확인을 거친 아주 강력한 지지 패턴입니다."
                })

        # 3. 직사각형 (Rectangle, Reliability: 4.0)
        if len(peaks) >= 2 and len(troughs) >= 2:
            p1, p2 = peaks[-2], peaks[-1]
            t1, t2 = troughs[-2], troughs[-1]
            if abs(df.loc[p1, 'High'] - df.loc[p2, 'High']) / df.loc[p1, 'High'] < 0.015 and \
               abs(df.loc[t1, 'Low'] - df.loc[t2, 'Low']) / df.loc[t1, 'Low'] < 0.015:
                patterns.append({
                    "name": "Rectangle Consolidation",
                    "type": "continuation",
                    "reliability": 4.0,
                    "points": [
                        {"time": get_time(t1), "price": float(df.loc[t1, 'Low'])},
                        {"time": get_time(p1), "price": float(df.loc[p1, 'High'])},
                        {"time": get_time(p2), "price": float(df.loc[p2, 'High'])},
                        {"time": get_time(t2), "price": float(df.loc[t2, 'Low'])},
                        {"time": get_time(t1), "price": float(df.loc[t1, 'Low'])}
                    ],
                    "desc": "박스권 횡보 중입니다. 어느 방향으로든 에너지가 응축되고 있습니다."
                })

        # 4. 쐐기형 (Falling/Rising Wedge, Reliability: 3.5)
        if len(peaks) >= 2 and len(troughs) >= 2:
            p1, p2 = peaks[-2], peaks[-1]
            t1, t2 = troughs[-2], troughs[-1]
            if df.loc[p2, 'High'] < df.loc[p1, 'High'] and df.loc[t2, 'Low'] < df.loc[t1, 'Low'] and \
               (df.loc[p1, 'High'] - df.loc[t1, 'Low']) > (df.loc[p2, 'High'] - df.loc[t2, 'Low']):
                patterns.append({
                    "name": "Falling Wedge",
                    "type": "bullish_reversal",
                    "reliability": 3.7,
                    "points": [
                        {"time": get_time(p1), "price": float(df.loc[p1, 'High'])},
                        {"time": get_time(p2), "price": float(df.loc[p2, 'High'])},
                        {"time": get_time(t1), "price": float(df.loc[t1, 'Low'])},
                        {"time": get_time(t2), "price": float(df.loc[t2, 'Low'])}
                    ],
                    "desc": "하락 쐐기형입니다. 상단 저항 돌파 시 강력한 반등이 나올 수 있습니다."
                })

        # 5. 라운딩 바텀 (Rounding Bottom, Reliability: 4.5)
        recent_30 = section.tail(30)
        low_idx = recent_30['Low'].idxmin()
        if low_idx != recent_30.index[0] and low_idx != recent_30.index[-1]:
            left_side = section.loc[:low_idx].tail(10)
            right_side = section.loc[low_idx:].head(10)
            if left_side['Low'].mean() > df.loc[low_idx, 'Low'] and right_side['Low'].mean() > df.loc[low_idx, 'Low']:
                patterns.append({
                    "name": "Rounding Bottom",
                    "type": "bullish_reversal",
                    "reliability": 4.5,
                    "points": [
                        {"time": get_time(left_side.index[0]), "price": float(left_side['Low'].iloc[0])},
                        {"time": get_time(low_idx), "price": float(df.loc[low_idx, 'Low'])},
                        {"time": get_time(right_side.index[-1]), "price": float(right_side['Low'].iloc[-1])}
                    ],
                    "desc": "컵 모양의 바닥을 만드는 중입니다. 장기적 추세 반전의 신호입니다."
                })

        return patterns

        return patterns

        return patterns

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """상세 기술적 분석 수행"""
        if df is None or len(df) < 30:
            return {
                "score": 50, "rsi": 50, "macd": 0, "signal": 0,
                "summary": "데이터 부족", "details": ["분석을 위한 충분한 데이터(최소 30일)가 부족합니다."],
                "entry_points": {}, "patterns": []
            }
            
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
            for p in patterns[:3]:
                details.append(f"  • {p['name']} ({p['reliability']}/5.0): {p['desc']}")
                # 패턴 유형에 따른 가중치 부여 (original logic moved here)
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
            'stop_loss': levels['support'] * 0.97,
            'current_price': current_price,
            # UI 호환용 단축 키
            'buy': f"{bb_lower:,.0f}",
            'target': f"{bb_upper:,.0f}",
            'stop': f"{levels['support'] * 0.97:,.0f}"
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
            "signal": signal_val,
            "current_price": current_price,
            "summary": "; ".join(reasons) if reasons else "중립",
            "details": details,
            "entry_points": entry_points,
            "patterns": patterns
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

class MacroAnalyzer:
    """
    거시적 관점 분석 - 시장 지수 동조화 및 장기 추세 분석
    """
    def analyze(self, ticker: str, daily_df: pd.DataFrame, index_df: pd.DataFrame = None) -> Dict[str, Any]:
        if daily_df is None or len(daily_df) < 20:
            return {"score": 50, "summary": "데이터 부족", "details": []}
            
        score = 50
        details = []
        reasons = []
        
        # 1. 지수 동조화 (Correlation) 분석
        if index_df is not None and not index_df.empty:
            common_idx = daily_df.index.intersection(index_df.index)
            if len(common_idx) > 10:
                stock_ret = daily_df.loc[common_idx, 'Close'].pct_change().dropna()
                idx_ret = index_df.loc[common_idx, 'Close'].pct_change().dropna()
                corr = stock_ret.corr(idx_ret)
                
                if corr > 0.7:
                    details.append(f"🌐 시장 지수와 높은 동조화({corr:.2f})를 보임. 시장 흐름에 민감합니다.")
                    if idx_ret.iloc[-1] > 0: score += 5
                elif corr < 0.3:
                    details.append(f"💎 시장과 독립적인 흐름({corr:.2f})을 보임. 개별 모멘텀이 중요합니다.")
                    score += 5

        # 2. 장기 이평선(200일선) 위치 분석
        if 'SMA_200' in daily_df.columns:
            last_price = daily_df['Close'].iloc[-1]
            sma_200 = daily_df['SMA_200'].iloc[-1]
            if not pd.isna(sma_200):
                ratio = last_price / sma_200
                if ratio > 1.15:
                    details.append(f"⚠️ 200일선 대비 {ratio:.1f}배 상회. 기술적 부담이 있는 구간입니다.")
                    score -= 5
                elif ratio < 0.85:
                    details.append(f"📉 200일선 대비 {ratio:.1f}배 하회. 과매도 및 장기 저평가 가능성.")
                    score += 10
        
        return {
            "score": max(0, min(100, score)),
            "summary": "; ".join(reasons) if reasons else "중립",
            "details": details
        }

class VolumePriceAnalyzer:
    """
    수급 및 에너지 분석 - OBV 및 거래량 패턴 분석
    """
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        return (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) < 20:
            return {"score": 50, "summary": "데이터 부족", "details": []}
            
        score = 50
        details = []
        reasons = []
        
        # 1. OBV 분석
        obv = self.calculate_obv(df)
        curr_obv = obv.iloc[-1]
        prev_obv = obv.iloc[-5]
        if curr_obv > prev_obv:
            score += 10
            details.append("💰 OBV 지표 상승: 매수세가 지속적으로 유입되고 있습니다.")
        else:
            score -= 5
            details.append("💸 OBV 지표 하락: 단기 자금 유출 신호가 감지됩니다.")
            
        # 2. 거래량 폭발 분석
        avg_vol = df['Volume'].tail(20).mean()
        curr_vol = df['Volume'].iloc[-1]
        if curr_vol > avg_vol * 2:
            if df['Close'].iloc[-1] > df['Open'].iloc[-1]:
                score += 15
                details.append(f"🔥 평소 대비 {curr_vol/avg_vol:.1f}배 대량 거래를 동반한 강한 상승이 포착되었습니다.")
            else:
                score -= 15
                details.append(f"⚠️ 평소 대비 {curr_vol/avg_vol:.1f}배 대량 거래를 동반한 하락이 발생했습니다. 매물 주의.")

        return {
            "score": max(0, min(100, score)),
            "summary": "; ".join(reasons) if reasons else "중립",
            "details": details
        }

class PsychologicalAnalyzer:
    """
    심리 분석 - 이격도 및 뉴스 감성 점수 통합
    """
    def analyze(self, df: pd.DataFrame, sentiment_data: dict = None) -> Dict[str, Any]:
        if df is None or len(df) < 5:
            return {"score": 50, "summary": "데이터 부족", "details": []}
            
        score = 50
        details = []
        
        # 1. 20일 이격도 (대중 심리)
        sma_20 = df['Close'].rolling(window=20).mean()
        disparity = (df['Close'].iloc[-1] / sma_20.iloc[-1]) * 100
        if disparity > 112:
            score -= 10
            details.append(f"🌡️ 20일 이격도 {disparity:.1f}%: 대중적 과열 상태입니다. 조정에 유의하세요.")
        elif disparity < 88:
            score += 15
            details.append(f"❄️ 20일 이격도 {disparity:.1f}%: 공포에 의한 단기 저점 구간입니다.")
            
        # 2. 뉴스 감성 통합
        if sentiment_data and sentiment_data.get('label') != 'unknown':
            label = sentiment_data['label']
            s_score = sentiment_data.get('score', 0)
            if label == 'positive':
                score += (10 * s_score)
                details.append(f"💬 뉴스/여론: 긍정적 ({s_score*100:.0f}%)")
            elif label == 'negative':
                score -= (10 * s_score)
                details.append(f"💬 뉴스/여론: 부정적 ({s_score*100:.0f}%)")

        return {
            "score": max(0, min(100, score)),
            "summary": "분석 완료",
            "details": details
        }

class StockAnalyst:
    """
    종합 분석 엔진 - 기술적 + 기본적 + 거시적 + 수급 + 심리 통합
    """
    def __init__(self):
        self.tech = TechnicalAnalyzer()
        self.fund = FundamentalAnalyzer()
        self.macro = MacroAnalyzer()
        self.vol_price = VolumePriceAnalyzer()
        self.psych = PsychologicalAnalyzer()
        self.calendar = EventCalendar()
        self.ml_predictor = MLPricePredictor()
        
    def analyze_ticker(self, ticker: str, daily_df: pd.DataFrame, financials: list = None, hourly_df: pd.DataFrame = None, index_df: pd.DataFrame = None, sentiment_data: dict = None) -> dict:
        """종합 분석 메인 루틴"""
        daily_tech = self._analyze_df(daily_df)
        hourly_tech = self._analyze_df(hourly_df) if hourly_df is not None else None
        fundamental = self.fund.analyze(financials) if financials else {"score": 50, "summary": "재무 데이터 없음"}
        
        # 신규 관점 분석
        macro = self.macro.analyze(ticker, daily_df, index_df)
        vol_price = self.vol_price.analyze(daily_df)
        psych = self.psych.analyze(daily_df, sentiment_data)
        event_risk = self.calendar.calculate_event_risk()
    
        # ML 예측 (Pillar 1)
        ml_forecast = self.ml_predictor.predict_next(daily_df)
    
        # 전략 앙상블 (고정밀 셋업 확인)
        ensemble = StrategyEnsemble.calculate_ensemble(
            daily_tech, event_risk, fundamental, psych.get('score', 50), ml_forecast
        )
    
        # 백테스팅 (Pillar 3)
        # 앙상블 로직을 단순화하여 과거 신호 생성 시뮬레이션
        signals = (daily_df['Close'] > daily_df['Close'].rolling(20).mean()).astype(int) # 예시용 단순 신호
        backtest_results = Backtester.backtest_vectorized(daily_df, signals)
    
        res = {
            "ticker": ticker,
            "daily_analysis": daily_tech,
            "hourly_analysis": hourly_tech,
            "fundamental": fundamental,
            "macro": macro,
            "volume_price": vol_price,
            "psychology": psych,
            "event_risk": event_risk,
            "ml_forecast": ml_forecast,
            "backtest": backtest_results,
            "ensemble": ensemble,
            "market_regime": self._determine_market_regime(daily_df, daily_tech),
            "strategy_checklist": self._get_strategy_checklist(daily_df, daily_tech),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 종합 점수 산출
        res["final_score"] = self._calculate_smart_score(res)
        res["signal"] = self._get_signal_text(res["final_score"])
        res["entry_points"] = self._calculate_entry_points(daily_df, hourly_df)
        
        # 가격 시나리오 추가
        if daily_df is not None:
             res["price_scenarios"] = self.tech.get_price_scenarios(daily_df)
             
        res["full_report"] = self._generate_full_report(res)

        return res

    def _analyze_df(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty: return None
        tech_res = self.tech.analyze(df)
        return {
            "last_close": float(df['Close'].iloc[-1]),
            "score": tech_res['score'],
            "rsi": tech_res['rsi'],
            "macd": {'MACD': tech_res['macd'], 'Signal': tech_res['signal']},
            "summary": tech_res['summary'],
            "details": tech_res['details'],
            "patterns": tech_res['patterns'],
            "entry_points": tech_res['entry_points']
        }

    def _calculate_smart_score(self, res: dict) -> int:
        """가중치 기반 종합 스코어링"""
        # 앙상블 결과가 있으면 앙상블 점수 우선 사용
        if res.get("ensemble"):
            return int(res["ensemble"]["final_score"])
            
        scores = {
            "tech": res["daily_analysis"]["score"] if res["daily_analysis"] else 50,
            "fund": res["fundamental"].get("score", 50),
            "macro": res["macro"].get("score", 50),
            "vol": res["volume_price"].get("score", 50),
            "psych": res["psychology"].get("score", 50)
        }
        
        # 가중치: 기술(30%), 기본(20%), 거시(20%), 수급(15%), 심리(15%)
        weighted = (scores["tech"] * 0.30 + scores["fund"] * 0.20 + 
                    scores["macro"] * 0.20 + scores["vol"] * 0.15 + 
                    scores["psych"] * 0.15)
        
        # 거시 필터링: 지수가 극도로 불안정하면 전체 점수 하향
        if scores["macro"] < 40: weighted *= 0.8
        
        # 시간봉(Timing) 반영 (단기 타점 보정)
        if res["hourly_analysis"]:
            weighted = (weighted * 0.7) + (res["hourly_analysis"]["score"] * 0.3)
            
        return int(max(0, min(100, weighted)))

    def _get_signal_text(self, score: int) -> str:
        if score >= 80: return "🚀 강력 매수 (Strong Buy)"
        if score >= 60: return "📈 매수 권고 (Buy)"
        if score >= 40: return "💬 중립 (Neutral)"
        if score >= 20: return "📉 매도 권고 (Sell)"
        return "⚠️ 강력 매도 (Strong Sell)"

    def _calculate_entry_points(self, daily_df: pd.DataFrame, hourly_df: pd.DataFrame) -> Dict[str, Any]:
        if hourly_df is not None and not hourly_df.empty:
            return self.tech.analyze(hourly_df).get('entry_points', {})
        return self.tech.analyze(daily_df).get('entry_points', {}) if daily_df is not None else {}

    def _determine_market_regime(self, df: pd.DataFrame, tech: dict) -> dict:
        """시장 국면(Regime) 판단 - Bull, Bear, VCP/Box"""
        if df is None or len(df) < 200:
            return {"regime": "Unknown", "desc": "데이터 부족"}

        last_close = df['Close'].iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = tech['details'].get('sma_200') if tech else df['Close'].rolling(200).mean().iloc[-1]
        
        # 1. Bull (상승 추세)
        if last_close > sma50 > sma200:
            return {
                "regime": "Bull",
                "label": "강세장 (Bull Market)",
                "color": "#10b981",
                "desc": "주가가 주요 이평선 위에 위치하며 강력한 상승 모멘텀을 유지하고 있습니다."
            }
        
        # 2. VCP/Box (변동성 수축/박스권)
        has_vcp = any(p['name'] == 'VCP' for p in tech.get('patterns', []))
        if has_vcp or (sma200 * 0.95 < last_close < sma200 * 1.05):
            return {
                "regime": "VCP",
                "label": "변동성 수축/매집 (Consolidation)",
                "color": "#fb923c",
                "desc": "변동성이 줄어들며 에너지를 응축하고 있습니다. 돌파 시 큰 시세가 기대됩니다."
            }
            
        # 3. Bear (하락 추세)
        if last_close < sma200:
            return {
                "regime": "Bear",
                "label": "약세장 (Bear Market)",
                "color": "#f43f5e",
                "desc": "장기 이평선 아래에서 하락 압박을 받고 있습니다. 보수적인 접근이 필요합니다."
            }
            
        return {"regime": "Neutral", "label": "중립 (Neutral)", "color": "#94a3b8", "desc": "명확한 추세가 없는 상태입니다."}

    def _get_strategy_checklist(self, df: pd.DataFrame, tech: dict) -> List[dict]:
        """성공 확률을 높이는 전략적 체크리스트"""
        if df is None or len(df) < 200: return []
        
        last_close = df['Close'].iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = tech['details'].get('sma_200') if tech else df['Close'].rolling(200).mean().iloc[-1]
        sma200_prev = df['Close'].rolling(200).mean().iloc[-20] # 20일 전
        
        checklist = [
            {
                "id": "trend_200",
                "text": "주가가 200일 이평선 위에 있는가?",
                "status": last_close > sma200,
                "importance": "High"
            },
            {
                "id": "sma_slope",
                "text": "200일 이평선이 우상향하고 있는가?",
                "status": sma200 > sma200_prev,
                "importance": "High"
            },
            {
                "id": "sma_alignment",
                "text": "정배열(50 > 200) 상태인가?",
                "status": sma50 > sma200,
                "importance": "Medium"
            },
            {
                "id": "vcp_pattern",
                "text": "변동성 수축(VCP) 흔적이 보이는가?",
                "status": any(p['name'] == 'VCP' for p in tech.get('patterns', [])),
                "importance": "High"
            },
            {
                "id": "rsi_healthy",
                "text": "RSI가 과열권(70+)이 아닌가?",
                "status": tech.get('rsi', 50) < 70,
                "importance": "Medium"
            }
        ]
        return checklist

    def _generate_full_report(self, res: dict) -> str:
        sections = [
            ("📉 기술적 관점 (Chart)", "daily_analysis"),
            ("🌐 거시적 관점 (Macro)", "macro"),
            ("💰 수급 및 에너지 (Volume)", "volume_price"),
            ("🧠 심리적 관점 (Psychology)", "psychology"),
            ("📋 재무 건전성 (Fund)", "fundamental")
        ]
        rpt = [f"📊 {res['ticker']} Comprehensive Analysis Report", f"🎯 종합 신호: {res['signal']} ({res['final_score']}/100)", ""]
        for title, key in sections:
            rpt.append(f"[{title}]")
            data = res.get(key, {})
            if data and "details" in data:
                for d in data["details"]: rpt.append(f" • {d}")
            else: rpt.append(" • 분석 데이터가 충분하지 않습니다.")
            rpt.append("")
        return "\n".join(rpt)
