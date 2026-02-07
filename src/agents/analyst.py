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
        """
        주요 차트 패턴 감지 및 시각화용 좌표 리턴
        """
        patterns = []
        if len(df) < 60:
            return patterns
            
        window = 60
        section = df.tail(window)
        
        # 날짜 포맷팅 함수 (ISO 스트링 또는 인덱스)
        def get_time(idx): return str(df.loc[idx, 'Date']) if 'Date' in df.columns else str(idx)

        # --- 1. 쌍바닥 (Double Bottom) + 드로잉 좌표 ---
        l_min1_idx = section.iloc[:window//2]['Low'].idxmin()
        l_min2_idx = section.iloc[window//2:]['Low'].idxmin()
        val1, val2 = df.loc[l_min1_idx, 'Low'], df.loc[l_min2_idx, 'Low']
        
        if abs(val1 - val2) / val1 < 0.025:
            mid_h_idx = df.loc[l_min1_idx:l_min2_idx, 'High'].idxmax()
            mid_h = df.loc[mid_h_idx, 'High']
            if mid_h > max(val1, val2) * 1.03:
                patterns.append({
                    "name": "쌍바닥 (W패턴)",
                    "type": "bullish_reversal",
                    "points": [
                        {"time": get_time(l_min1_idx), "price": float(val1)},
                        {"time": get_time(mid_h_idx), "price": float(mid_h)},
                        {"time": get_time(l_min2_idx), "price": float(val2)}
                    ],
                    "desc": "강력한 바닥 지지 신호입니다. W의 중앙 고점 돌파 시 추세 전환이 확정됩니다."
                })

        # --- 2. 헤드 앤 숄더 (Head & Shoulders) + 드로잉 좌표 ---
        p1 = section.iloc[0:20]['High'].idxmax()
        p2 = section.iloc[20:40]['High'].idxmax()
        p3 = section.iloc[40:60]['High'].idxmax()
        v1, v2, v3 = df.loc[p1, 'High'], df.loc[p2, 'High'], df.loc[p3, 'High']
        
        if v2 > v1 * 1.03 and v2 > v3 * 1.03 and abs(v1-v3)/v1 < 0.05:
            patterns.append({
                "name": "헤드 앤 숄더",
                "type": "bearish_reversal",
                "points": [
                    {"time": get_time(p1), "price": float(v1)},
                    {"time": get_time(p2), "price": float(v2)},
                    {"time": get_time(p3), "price": float(v3)}
                ],
                "desc": "전형적인 천장 신호입니다. 세 번째 산인 오른쪽 어깨 이후 하락세가 강화될 수 있습니다."
            })

        # --- 3. 추세선 (Trend Lines) - 지지 및 저항 추세 ---
        # 지지 추세선: 최근 두 개의 저점 연결
        recent_lows = section.sort_values('Low').head(5).index.sort_values()
        if len(recent_lows) >= 2:
            idx1, idx2 = recent_lows[0], recent_lows[-1]
            if (idx2 - idx1) > 10: # 너무 붙어있지 않은 두 지점
                patterns.append({
                    "name": "상승/지지 추세선",
                    "type": "trend_line",
                    "points": [
                        {"time": get_time(idx1), "price": float(df.loc[idx1, 'Low'])},
                        {"time": get_time(idx2), "price": float(df.loc[idx2, 'Low'])}
                    ],
                    "desc": "가격의 하단을 지지해주는 핵심 추세 추종 라인입니다."
                })

        # 저항 추세선: 최근 두 개의 고점 연결
        recent_highs = section.sort_values('High', ascending=False).head(5).index.sort_values()
        if len(recent_highs) >= 2:
            idx1, idx2 = recent_highs[0], recent_highs[-1]
            if (idx2 - idx1) > 10:
                patterns.append({
                    "name": "하락/저항 추세선",
                    "type": "resistance_line",
                    "points": [
                        {"time": get_time(idx1), "price": float(df.loc[idx1, 'High'])},
                        {"time": get_time(idx2), "price": float(df.loc[idx2, 'High'])}
                    ],
                    "desc": "가격을 누르고 있는 저항 구간으로, 돌파 시 급등 가능성이 있습니다."
                })

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

class StockAnalyst:
    """
    종합 분석 엔진 - 기술적 + 기본적 분석 통합
    """
    def __init__(self):
        self.tech = TechnicalAnalyzer()
        self.fund = FundamentalAnalyzer()
        
    def analyze_ticker(self, ticker: str, daily_df: pd.DataFrame, financials: list = None, hourly_df: pd.DataFrame = None) -> dict:
        """
        Daily(추세) + Hourly(타점) 복합 스마트 분석
        """
        res = {
            "ticker": ticker,
            "daily_analysis": self._analyze_df(daily_df),
            "hourly_analysis": self._analyze_df(hourly_df) if hourly_df is not None else None,
            "fundamental": self._analyze_fundamentals(financials) if financials else {"score": 50, "summary": "재무 데이터 없음"},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 종합 점수 산출 (Danelfin/Fint 스타일)
        res["final_score"] = self._calculate_smart_score(res)
        res["signal"] = self._get_signal_text(res["final_score"])
        
        # 매수/매도 타점 제안
        res["entry_points"] = self._calculate_entry_points(daily_df, hourly_df)
        
        # 상세 리포트 생성
        res["full_report"] = self._generate_full_report(res)

        return res

    def _analyze_df(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty: return None
        
        # 기존 TechnicalAnalyzer의 analyze 메서드를 사용하여 지표 계산
        tech_analysis_result = self.tech.analyze(df)
        
        analysis = {
            "last_close": float(df['Close'].iloc[-1]),
            "score": tech_analysis_result['score'],
            "rsi": tech_analysis_result['rsi'],
            "macd": {'MACD': tech_analysis_result['macd'], 'Signal': tech_analysis_result['signal']},
            "summary": tech_analysis_result['summary'],
            "details": tech_analysis_result['details'],
            "patterns": tech_analysis_result['patterns'],
            "entry_points": tech_analysis_result['entry_points']
        }
        return analysis

    def _analyze_fundamentals(self, financials: list[Any]) -> Dict[str, Any]:
        return self.fund.analyze(financials)

    def _calculate_smart_score(self, res: dict) -> int:
        score = 50
        daily = res["daily_analysis"]
        hourly = res["hourly_analysis"]
        
        # Daily analysis contributes to overall trend (e.g., 40% weight)
        if daily:
            # Use the score from TechnicalAnalyzer for daily data as a base
            score += (daily["score"] - 50) * 0.4 # Adjust based on daily score deviation from 50
            
            # Additional specific daily indicators
            rsi_d = daily.get("rsi")
            if rsi_d is not None:
                if rsi_d < 30: score += 5
                if rsi_d > 70: score -= 5
            
            macd_d = daily.get("macd")
            if macd_d and macd_d.get("MACD") is not None and macd_d.get("Signal") is not None:
                if macd_d["MACD"] > macd_d["Signal"]: score += 5
            
            # Pattern weighting
            for p in daily["patterns"]:
                if p["type"] == "bullish_reversal" or p["type"] == "bullish_continuation": score += 5
                if p["type"] == "bearish": score -= 5

        # Hourly analysis contributes to entry/exit timing (e.g., 30% weight)
        if hourly:
            # Use the score from TechnicalAnalyzer for hourly data
            score += (hourly["score"] - 50) * 0.3 # Adjust based on hourly score deviation from 50

            # Additional specific hourly indicators for timing
            rsi_h = hourly.get("rsi")
            if rsi_h is not None and rsi_h < 35: score += 5
            
            macd_h = hourly.get("macd")
            if macd_h and macd_h.get("MACD") is not None and macd_h.get("Signal") is not None:
                if macd_h["MACD"] > macd_h["Signal"]: score += 3
            
        # Fundamental analysis contributes to long-term value (e.g., 30% weight)
        fund_score = res["fundamental"].get("score", 50)
        score += (fund_score - 50) * 0.3 # Adjust based on fundamental score deviation from 50
        
        return int(max(0, min(100, score)))

    def _get_signal_text(self, score: int) -> str:
        if score >= 85: return "🚀 강력 매수 (Strong Buy)"
        if score >= 65: return "📈 매수 권고 (Buy)"
        if score >= 45: return "💬 중립 (Neutral)"
        if score >= 25: return "📉 매도 권고 (Sell)"
        return "⚠️ 강력 매도 (Strong Sell)"

    def _calculate_entry_points(self, daily_df: pd.DataFrame, hourly_df: pd.DataFrame) -> Dict[str, Any]:
        # Prioritize hourly entry points if available, otherwise use daily
        if hourly_df is not None and not hourly_df.empty:
            hourly_tech_res = self.tech.analyze(hourly_df)
            return hourly_tech_res.get('entry_points', {})
        elif daily_df is not None and not daily_df.empty:
            daily_tech_res = self.tech.analyze(daily_df)
            return daily_tech_res.get('entry_points', {})
        return {}

    def _generate_full_report(self, res: dict) -> str:
        ticker = res["ticker"]
        signal = res["signal"]
        final_score = res["final_score"]
        daily = res["daily_analysis"]
        fundamental = res["fundamental"]
        
        # 상세 리포트 생성
        full_report = []
        full_report.append(f"═══════════════════════════════════════")
        full_report.append(f"📊 {ticker} Smart Analysis Report")
        full_report.append(f"═══════════════════════════════════════")
        full_report.append(f"")
        full_report.append(f"🎯 종합 판단: {signal}")
        full_report.append(f"📊 AI 확률 스코어: {final_score}/100")
        full_report.append(f"")
        
        if daily:
            full_report.append(f"───────────────────────────────────────")
            full_report.append(f"📉 기술적 분석 지표 (일봉)")
            full_report.append(f"───────────────────────────────────────")
            for detail in daily.get('details', []):
                full_report.append(detail)
            
        full_report.append(f"")
        full_report.append(f"───────────────────────────────────────")
        full_report.append(f"📋 기본적 분석 (재무제표)")
        full_report.append(f"───────────────────────────────────────")
        for detail in fundamental.get('details', []):
            full_report.append(detail)
            
        return "\n".join(full_report)
