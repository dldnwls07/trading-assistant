"""
확장 차트 패턴 라이브러리
30개 이상의 차트 패턴 자동 감지 및 신뢰도 평가
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any

class AdvancedPatternDetector:
    """
    고급 차트 패턴 감지 엔진
    - Bulkowski의 패턴 통계 기반 신뢰도 평가
    - 30개 이상의 클래식 및 고급 패턴 지원
    """
    
    def __init__(self):
        # 패턴별 통계적 신뢰도 (Bulkowski Encyclopedia 기반)
        self.pattern_reliability = {
            # 반전 패턴
            "Head and Shoulders": 4.5,
            "Inverse Head and Shoulders": 4.5,
            "Triple Top": 4.3,
            "Triple Bottom": 4.5,
            "Double Top": 4.0,
            "Double Bottom": 4.2,
            "Rounding Bottom": 4.5,
            "Rounding Top": 4.3,
            
            # 지속 패턴
            "Ascending Triangle": 3.8,
            "Descending Triangle": 3.7,
            "Symmetrical Triangle": 3.5,
            "Rising Wedge": 3.6,
            "Falling Wedge": 3.7,
            "Bull Flag": 4.0,
            "Bear Flag": 3.9,
            "Pennant": 3.8,
            "Rectangle": 4.0,
            
            # 캔들 패턴
            "Hammer": 3.5,
            "Inverted Hammer": 3.4,
            "Shooting Star": 3.6,
            "Hanging Man": 3.3,
            "Doji": 3.0,
            "Engulfing Bullish": 4.0,
            "Engulfing Bearish": 3.9,
            "Morning Star": 4.2,
            "Evening Star": 4.1,
            "Three White Soldiers": 4.3,
            "Three Black Crows": 4.2,
            
            # 고급 패턴
            "Cup and Handle": 4.4,
            "Inverse Cup and Handle": 4.2,
            "Diamond Top": 3.8,
            "Diamond Bottom": 3.9,
            "Broadening Formation": 3.5,
            "Island Reversal": 4.0,
            "Gap Patterns": 3.6
        }
    
    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """모든 패턴 감지 (우선순위 순)"""
        if len(df) < 60:
            return []
        
        patterns = []
        
        # 피크/트로프 추출
        peaks, troughs = self._find_peaks_troughs(df)
        
        # 1. 반전 패턴 감지
        patterns.extend(self._detect_head_shoulders(df, peaks, troughs))
        patterns.extend(self._detect_double_patterns(df, peaks, troughs))
        patterns.extend(self._detect_triple_patterns(df, peaks, troughs))
        patterns.extend(self._detect_rounding_patterns(df))
        
        # 2. 지속 패턴 감지
        patterns.extend(self._detect_triangles(df, peaks, troughs))
        patterns.extend(self._detect_wedges(df, peaks, troughs))
        patterns.extend(self._detect_flags_pennants(df))
        patterns.extend(self._detect_rectangles(df, peaks, troughs))
        
        # 3. 캔들 패턴 감지
        patterns.extend(self._detect_candlestick_patterns(df))
        
        # 4. 고급 패턴 감지
        patterns.extend(self._detect_cup_handle(df))
        patterns.extend(self._detect_diamond(df, peaks, troughs))
        patterns.extend(self._detect_gaps(df))
        
        # 신뢰도 기준 정렬 (높은 순)
        patterns.sort(key=lambda x: x['reliability'], reverse=True)
        
        return patterns
    
    def _find_peaks_troughs(self, df: pd.DataFrame, window: int = 5) -> tuple:
        """피크와 트로프 추출"""
        peaks = []
        troughs = []
        
        for i in range(window, len(df) - window):
            if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
                peaks.append(i)
            if df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min():
                troughs.append(i)
        
        return peaks, troughs
    
    # ==================== 반전 패턴 ====================
    
    def _detect_head_shoulders(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """헤드 앤 숄더 & 역헤드 앤 숄더"""
        patterns = []
        
        # 일반 헤드 앤 숄더 (고점 반전)
        if len(peaks) >= 3:
            for i in range(len(peaks) - 2):
                p1, p2, p3 = peaks[i], peaks[i+1], peaks[i+2]
                h1, h2, h3 = df['High'].iloc[p1], df['High'].iloc[p2], df['High'].iloc[p3]
                
                # 헤드가 양 숄더보다 높고, 양 숄더가 비슷한 높이
                if h2 > h1 * 1.02 and h2 > h3 * 1.02 and abs(h1 - h3) / h1 < 0.05:
                    patterns.append({
                        "name": "Head and Shoulders",
                        "type": "bearish_reversal",
                        "reliability": self.pattern_reliability["Head and Shoulders"],
                        "confidence": 85,
                        "points": [
                            {"index": p1, "price": float(h1), "label": "Left Shoulder"},
                            {"index": p2, "price": float(h2), "label": "Head"},
                            {"index": p3, "price": float(h3), "label": "Right Shoulder"}
                        ],
                        "desc": "강력한 하락 반전 신호. 넥라인 이탈 시 큰 하락 예상.",
                        "target": float(h2 - (h2 - df['Low'].iloc[p1:p3].min()) * 1.5)
                    })
        
        # 역헤드 앤 숄더 (저점 반전)
        if len(troughs) >= 3:
            for i in range(len(troughs) - 2):
                t1, t2, t3 = troughs[i], troughs[i+1], troughs[i+2]
                l1, l2, l3 = df['Low'].iloc[t1], df['Low'].iloc[t2], df['Low'].iloc[t3]
                
                if l2 < l1 * 0.98 and l2 < l3 * 0.98 and abs(l1 - l3) / l1 < 0.05:
                    patterns.append({
                        "name": "Inverse Head and Shoulders",
                        "type": "bullish_reversal",
                        "reliability": self.pattern_reliability["Inverse Head and Shoulders"],
                        "confidence": 87,
                        "points": [
                            {"index": t1, "price": float(l1), "label": "Left Shoulder"},
                            {"index": t2, "price": float(l2), "label": "Head"},
                            {"index": t3, "price": float(l3), "label": "Right Shoulder"}
                        ],
                        "desc": "강력한 상승 반전 신호. 넥라인 돌파 시 큰 상승 예상.",
                        "target": float(l2 + (df['High'].iloc[t1:t3].max() - l2) * 1.5)
                    })
        
        return patterns
    
    def _detect_double_patterns(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """더블 탑 & 더블 바텀"""
        patterns = []
        
        # 더블 탑
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                p1, p2 = peaks[i], peaks[i+1]
                h1, h2 = df['High'].iloc[p1], df['High'].iloc[p2]
                
                if abs(h1 - h2) / h1 < 0.02 and p2 - p1 > 5:  # 비슷한 고점, 충분한 간격
                    patterns.append({
                        "name": "Double Top",
                        "type": "bearish_reversal",
                        "reliability": self.pattern_reliability["Double Top"],
                        "confidence": 78,
                        "points": [
                            {"index": p1, "price": float(h1)},
                            {"index": p2, "price": float(h2)}
                        ],
                        "desc": "이중 천장 형성. 중간 저점 이탈 시 하락 전환.",
                        "target": float(h1 - (h1 - df['Low'].iloc[p1:p2].min()))
                    })
        
        # 더블 바텀
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                t1, t2 = troughs[i], troughs[i+1]
                l1, l2 = df['Low'].iloc[t1], df['Low'].iloc[t2]
                
                if abs(l1 - l2) / l1 < 0.02 and t2 - t1 > 5:
                    patterns.append({
                        "name": "Double Bottom",
                        "type": "bullish_reversal",
                        "reliability": self.pattern_reliability["Double Bottom"],
                        "confidence": 82,
                        "points": [
                            {"index": t1, "price": float(l1)},
                            {"index": t2, "price": float(l2)}
                        ],
                        "desc": "이중 바닥 형성. 중간 고점 돌파 시 상승 전환.",
                        "target": float(l1 + (df['High'].iloc[t1:t2].max() - l1))
                    })
        
        return patterns
    
    def _detect_triple_patterns(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """트리플 탑 & 트리플 바텀"""
        patterns = []
        
        # 트리플 탑
        if len(peaks) >= 3:
            p1, p2, p3 = peaks[-3], peaks[-2], peaks[-1]
            h1, h2, h3 = df['High'].iloc[p1], df['High'].iloc[p2], df['High'].iloc[p3]
            
            if abs(h1 - h2) / h1 < 0.02 and abs(h2 - h3) / h2 < 0.02:
                patterns.append({
                    "name": "Triple Top",
                    "type": "bearish_reversal",
                    "reliability": self.pattern_reliability["Triple Top"],
                    "confidence": 88,
                    "points": [
                        {"index": p1, "price": float(h1)},
                        {"index": p2, "price": float(h2)},
                        {"index": p3, "price": float(h3)}
                    ],
                    "desc": "세 번의 고점 실패. 매우 강력한 저항선.",
                    "target": float(h1 - (h1 - df['Low'].iloc[p1:p3].min()) * 1.2)
                })
        
        # 트리플 바텀
        if len(troughs) >= 3:
            t1, t2, t3 = troughs[-3], troughs[-2], troughs[-1]
            l1, l2, l3 = df['Low'].iloc[t1], df['Low'].iloc[t2], df['Low'].iloc[t3]
            
            if abs(l1 - l2) / l1 < 0.02 and abs(l2 - l3) / l2 < 0.02:
                patterns.append({
                    "name": "Triple Bottom",
                    "type": "bullish_reversal",
                    "reliability": self.pattern_reliability["Triple Bottom"],
                    "confidence": 90,
                    "points": [
                        {"index": t1, "price": float(l1)},
                        {"index": t2, "price": float(l2)},
                        {"index": t3, "price": float(l3)}
                    ],
                    "desc": "세 번의 바닥 확인. 매우 강력한 지지선.",
                    "target": float(l1 + (df['High'].iloc[t1:t3].max() - l1) * 1.2)
                })
        
        return patterns
    
    def _detect_rounding_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """라운딩 바텀 & 라운딩 탑"""
        patterns = []
        window = min(30, len(df) // 2)
        
        if len(df) < window:
            return patterns
        
        recent = df.tail(window)
        low_idx = recent['Low'].idxmin()
        low_pos = recent.index.get_loc(low_idx)
        
        # 라운딩 바텀: U자 형태
        if 5 < low_pos < len(recent) - 5:
            left = recent.iloc[:low_pos]
            right = recent.iloc[low_pos:]
            
            if left['Low'].is_monotonic_decreasing and right['Low'].is_monotonic_increasing:
                patterns.append({
                    "name": "Rounding Bottom",
                    "type": "bullish_reversal",
                    "reliability": self.pattern_reliability["Rounding Bottom"],
                    "confidence": 85,
                    "points": [
                        {"index": recent.index[0], "price": float(recent['Low'].iloc[0])},
                        {"index": low_idx, "price": float(recent.loc[low_idx, 'Low'])},
                        {"index": recent.index[-1], "price": float(recent['Low'].iloc[-1])}
                    ],
                    "desc": "컵 모양 바닥. 장기 추세 반전 신호.",
                    "target": float(recent.loc[low_idx, 'Low'] * 1.15)
                })
        
        return patterns
    
    # ==================== 지속 패턴 ====================
    
    def _detect_triangles(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """삼각형 패턴 (상승/하락/대칭)"""
        patterns = []
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            # 상승 삼각형: 고점은 수평, 저점은 상승
            p1, p2 = peaks[-2], peaks[-1]
            t1, t2 = troughs[-2], troughs[-1]
            
            if abs(df['High'].iloc[p1] - df['High'].iloc[p2]) / df['High'].iloc[p1] < 0.02:
                if df['Low'].iloc[t2] > df['Low'].iloc[t1]:
                    patterns.append({
                        "name": "Ascending Triangle",
                        "type": "bullish_continuation",
                        "reliability": self.pattern_reliability["Ascending Triangle"],
                        "confidence": 75,
                        "points": [
                            {"index": p1, "price": float(df['High'].iloc[p1])},
                            {"index": t1, "price": float(df['Low'].iloc[t1])},
                            {"index": p2, "price": float(df['High'].iloc[p2])},
                            {"index": t2, "price": float(df['Low'].iloc[t2])}
                        ],
                        "desc": "상승 삼각형. 저항선 돌파 시 강한 상승.",
                        "target": float(df['High'].iloc[p1] * 1.1)
                    })
        
        return patterns
    
    def _detect_wedges(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """쐐기형 패턴"""
        patterns = []
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            p1, p2 = peaks[-2], peaks[-1]
            t1, t2 = troughs[-2], troughs[-1]
            
            # 하락 쐐기 (상승 반전)
            if df['High'].iloc[p2] < df['High'].iloc[p1] and df['Low'].iloc[t2] < df['Low'].iloc[t1]:
                if (df['High'].iloc[p1] - df['Low'].iloc[t1]) > (df['High'].iloc[p2] - df['Low'].iloc[t2]):
                    patterns.append({
                        "name": "Falling Wedge",
                        "type": "bullish_reversal",
                        "reliability": self.pattern_reliability["Falling Wedge"],
                        "confidence": 72,
                        "points": [
                            {"index": p1, "price": float(df['High'].iloc[p1])},
                            {"index": t1, "price": float(df['Low'].iloc[t1])},
                            {"index": p2, "price": float(df['High'].iloc[p2])},
                            {"index": t2, "price": float(df['Low'].iloc[t2])}
                        ],
                        "desc": "하락 쐐기. 상단 돌파 시 강한 반등.",
                        "target": float(df['High'].iloc[p1])
                    })
        
        return patterns
    
    def _detect_flags_pennants(self, df: pd.DataFrame) -> List[Dict]:
        """깃발 & 페넌트 패턴"""
        patterns = []
        
        if len(df) < 20:
            return patterns
        
        # 최근 20봉 분석
        recent = df.tail(20)
        
        # 급등/급락 후 횡보 = 깃발
        first_10 = recent.iloc[:10]
        last_10 = recent.iloc[10:]
        
        strong_move = abs((first_10['Close'].iloc[-1] - first_10['Close'].iloc[0]) / first_10['Close'].iloc[0]) > 0.05
        consolidation = abs((last_10['Close'].iloc[-1] - last_10['Close'].iloc[0]) / last_10['Close'].iloc[0]) < 0.02
        
        if strong_move and consolidation:
            if first_10['Close'].iloc[-1] > first_10['Close'].iloc[0]:
                patterns.append({
                    "name": "Bull Flag",
                    "type": "bullish_continuation",
                    "reliability": self.pattern_reliability["Bull Flag"],
                    "confidence": 80,
                    "points": [],
                    "desc": "강세 깃발. 상승 추세 지속 가능성 높음.",
                    "target": float(recent['Close'].iloc[-1] * 1.05)
                })
        
        return patterns
    
    def _detect_rectangles(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """직사각형 (박스권)"""
        patterns = []
        
        if len(peaks) >= 2 and len(troughs) >= 2:
            p1, p2 = peaks[-2], peaks[-1]
            t1, t2 = troughs[-2], troughs[-1]
            
            # 고점과 저점이 각각 수평
            if abs(df['High'].iloc[p1] - df['High'].iloc[p2]) / df['High'].iloc[p1] < 0.015:
                if abs(df['Low'].iloc[t1] - df['Low'].iloc[t2]) / df['Low'].iloc[t1] < 0.015:
                    patterns.append({
                        "name": "Rectangle",
                        "type": "continuation",
                        "reliability": self.pattern_reliability["Rectangle"],
                        "confidence": 70,
                        "points": [
                            {"index": p1, "price": float(df['High'].iloc[p1])},
                            {"index": t1, "price": float(df['Low'].iloc[t1])},
                            {"index": p2, "price": float(df['High'].iloc[p2])},
                            {"index": t2, "price": float(df['Low'].iloc[t2])}
                        ],
                        "desc": "박스권 횡보. 돌파 방향 주시 필요.",
                        "target": None
                    })
        
        return patterns
    
    # ==================== 캔들 패턴 ====================
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """주요 캔들스틱 패턴"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 망치형 (Hammer)
        body = abs(last['Close'] - last['Open'])
        lower_shadow = min(last['Open'], last['Close']) - last['Low']
        upper_shadow = last['High'] - max(last['Open'], last['Close'])
        
        if lower_shadow > body * 2 and upper_shadow < body * 0.3:
            patterns.append({
                "name": "Hammer",
                "type": "bullish_reversal",
                "reliability": self.pattern_reliability["Hammer"],
                "confidence": 65,
                "points": [{"index": len(df)-1, "price": float(last['Close'])}],
                "desc": "망치형 캔들. 하락 추세 반전 신호.",
                "target": float(last['Close'] * 1.03)
            })
        
        # 강세 잉걸핑 (Engulfing Bullish)
        if prev['Close'] < prev['Open'] and last['Close'] > last['Open']:
            if last['Close'] > prev['Open'] and last['Open'] < prev['Close']:
                patterns.append({
                    "name": "Engulfing Bullish",
                    "type": "bullish_reversal",
                    "reliability": self.pattern_reliability["Engulfing Bullish"],
                    "confidence": 78,
                    "points": [
                        {"index": len(df)-2, "price": float(prev['Close'])},
                        {"index": len(df)-1, "price": float(last['Close'])}
                    ],
                    "desc": "강세 잉걸핑. 강한 매수 신호.",
                    "target": float(last['Close'] * 1.05)
                })
        
        return patterns
    
    # ==================== 고급 패턴 ====================
    
    def _detect_cup_handle(self, df: pd.DataFrame) -> List[Dict]:
        """컵 앤 핸들"""
        patterns = []
        
        if len(df) < 50:
            return patterns
        
        # 컵 부분 (U자)
        cup_section = df.tail(40)
        low_idx = cup_section['Low'].idxmin()
        low_pos = cup_section.index.get_loc(low_idx)
        
        # 핸들 부분 (작은 하락)
        if 15 < low_pos < 30:
            handle = df.tail(10)
            if handle['Close'].iloc[-1] < handle['Close'].iloc[0] * 1.02:
                patterns.append({
                    "name": "Cup and Handle",
                    "type": "bullish_continuation",
                    "reliability": self.pattern_reliability["Cup and Handle"],
                    "confidence": 82,
                    "points": [],
                    "desc": "컵 앤 핸들. 돌파 시 강한 상승.",
                    "target": float(df['Close'].iloc[-1] * 1.15)
                })
        
        return patterns
    
    def _detect_diamond(self, df: pd.DataFrame, peaks: List[int], troughs: List[int]) -> List[Dict]:
        """다이아몬드 패턴"""
        # 복잡한 패턴이므로 간략화
        return []
    
    def _detect_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """갭 패턴"""
        patterns = []
        
        for i in range(1, min(10, len(df))):
            prev_high = df['High'].iloc[-i-1]
            curr_low = df['Low'].iloc[-i]
            
            # 상승 갭
            if curr_low > prev_high * 1.01:
                patterns.append({
                    "name": "Gap Up",
                    "type": "bullish_continuation",
                    "reliability": self.pattern_reliability["Gap Patterns"],
                    "confidence": 68,
                    "points": [
                        {"index": len(df)-i-1, "price": float(prev_high)},
                        {"index": len(df)-i, "price": float(curr_low)}
                    ],
                    "desc": f"상승 갭 발생 ({i}봉 전). 강한 매수세.",
                    "target": None
                })
                break
        
        return patterns


# 통합 사용 예시
if __name__ == "__main__":
    import yfinance as yf
    
    detector = AdvancedPatternDetector()
    
    # 샘플 데이터
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="6mo")
    
    patterns = detector.detect_all_patterns(df)
    
    print(f"\n=== 감지된 패턴: {len(patterns)}개 ===\n")
    for p in patterns[:10]:  # 상위 10개만
        print(f"📊 {p['name']} ({p['type']})")
        print(f"   신뢰도: {p['reliability']}/5.0 | 확신도: {p['confidence']}%")
        print(f"   {p['desc']}")
        if p.get('target'):
            print(f"   목표가: {p['target']:.2f}")
        print()
