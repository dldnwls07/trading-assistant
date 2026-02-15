"""
다중 시간 프레임 분석 시스템
단기(데이 트레이딩), 중기(스윙), 장기(포지션) 각각의 독립적 신호 생성
+ 시간 프레임별 매수/매도 타점 제공
+ 고급 차트 패턴 감지 통합
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yfinance as yf

from src.agents.analyst import StockAnalyst
from src.agents.pattern_detector import AdvancedPatternDetector
from src.agents.ai_analyzer import AIAnalyzer
from src.data.collector import MarketDataCollector

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    """
    다중 시간 프레임 종합 분석
    - 단기 (1~5일): 분봉/시간봉 기반 데이 트레이딩
    - 중기 (1~3개월): 일봉 기반 스윙 트레이딩
    - 장기 (6개월~1년): 주봉/월봉 기반 포지션 트레이딩
    """
    
    TIMEFRAMES = {
        "short": {
            "name": "단기 (관점: 1개월)",
            "description": "최근 1개월간의 1시간봉 기반 정밀 분석",
            "data_period": "1mo",
            "data_interval": "1h",  # 1시간봉
            "holding_period": "1~4주",
            "focus": "기술적 지표, 단기 모멘텀, 거래량"
        },
        "medium": {
            "name": "중기 (관점: 6개월)",
            "description": "최근 12개월간의 일봉 기반 추세 분석",
            "data_period": "1y",
            "data_interval": "1d",  # 일봉
            "holding_period": "3~6개월",
            "focus": "차트 패턴, 이동평균선, 지지/저항"
        },
        "long": {
            "name": "장기 (관점: 1년 이상)",
            "description": "2년 이상의 주봉 기반 가치 및 거시 선행 분석",
            "data_period": "2y",
            "data_interval": "1wk",  # 주봉
            "holding_period": "1년 이상",
            "focus": "펀더멘털, 장기 추세, 거시 경제"
        }
    }
    
    def __init__(self):
        self.analyst = StockAnalyst()
        self.pattern_detector = AdvancedPatternDetector()
        self.ai_analyzer = AIAnalyzer()
        self.collector = MarketDataCollector()
    
    async def analyze_all_timeframes(self, 
                               ticker: str,
                               index_ticker: str = "^GSPC") -> Dict[str, Any]:
        """
        모든 시간 프레임에 대한 종합 분석 (비동기 병렬 처리)
        """
        logger.info(f"{ticker} 다중 시간 프레임 분석 시작")
        
        results = {
            "ticker": ticker,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "short_term": None,
            "medium_term": None,
            "long_term": None,
            "consensus": None,
            "all_patterns": []
        }
        
        # 각 시간 프레임별 분석 태스크 생성
        tasks = [self._analyze_timeframe(ticker, tf_key, index_ticker) for tf_key in ["short", "medium", "long"]]
        tf_results = await asyncio.gather(*tasks)
        
        # 결과 매핑 및 패턴 수집
        for i, tf_key in enumerate(["short", "medium", "long"]):
            tf_result = tf_results[i]
            results[f"{tf_key}_term"] = tf_result
            
            if tf_result and tf_result.get('patterns'):
                for pattern in tf_result['patterns']:
                    pattern['timeframe'] = tf_key
                    results['all_patterns'].append(pattern)
        
        # 종합 컨센서스 생성
        results["consensus"] = self._generate_consensus(results)
        
        # AI 수석 분석가 리포트 생성 (필요 시 비동기 지원 확인)
        # ai_analyzer.generate_report가 비동기라면 await 필수
        results["ai_report"] = self.ai_analyzer.generate_report(results)
        
        return results
    
    async def _analyze_timeframe(self, 
                          ticker: str,
                          timeframe: str,
                          index_ticker: str) -> Dict[str, Any]:
        """특정 시간 프레임 분석 (비동기)"""
        try:
            tf_config = self.TIMEFRAMES[timeframe]
            
            # 데이터 수집 (await 적용)
            stock_data = await self._fetch_data(
                ticker, 
                period=tf_config["data_period"],
                interval=tf_config["data_interval"]
            )
            
            index_data = await self._fetch_data(
                index_ticker,
                period=tf_config["data_period"],
                interval=tf_config["data_interval"]
            )
            
            if stock_data is None or stock_data.empty:
                return self._empty_result(timeframe, "데이터 수집 실패")
            
            # 종합 분석 수행
            analysis = self.analyst.analyze_ticker(
                ticker=ticker,
                daily_df=stock_data,
                index_df=index_data,
                financials=None,
                hourly_df=None,
                sentiment_data=None
            )
            
            # 시간 프레임별 특화 분석 추가
            specialized = self._apply_timeframe_specific_analysis(
                timeframe, stock_data, analysis
            )
            
            # 고급 패턴 감지
            detected_patterns = self.pattern_detector.detect_all_patterns(stock_data)
            
            # 패턴 인덱스를 타임스탬프로 변환 (차트 시각화용)
            for p in detected_patterns:
                if 'points' in p:
                    for pt in p['points']:
                        idx = pt.get('index')
                        if idx is not None and 0 <= idx < len(stock_data):
                            # 타임스탬프를 문자열로 변환 (ISO 형식 또는 날짜만)
                            ts = stock_data.index[idx]
                            if timeframe == "short":
                                pt['time'] = ts.strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                pt['time'] = ts.strftime('%Y-%m-%d')
            
            # 시간 프레임별 매수/매도 타점 계산
            entry_exit_points = self._calculate_timeframe_entry_points(
                timeframe, stock_data, analysis, detected_patterns
            )
            
            return {
                "timeframe": timeframe,
                "name": tf_config["name"],
                "description": tf_config["description"],
                "holding_period": tf_config["holding_period"],
                "focus_areas": tf_config["focus"],
                "score": analysis["final_score"],
                "signal": analysis["signal"],
                "current_price": stock_data['Close'].iloc[-1],
                "entry_points": entry_exit_points,  # 시간 프레임별 맞춤 타점
                "patterns": detected_patterns[:5],  # 상위 5개 패턴만
                "specialized_insights": specialized,
                "full_analysis": analysis,
                "recommendation": self._generate_timeframe_recommendation(
                    timeframe, analysis, specialized
                )
            }
            
        except Exception as e:
            logger.error(f"{ticker} {timeframe} 분석 실패: {e}")
            return self._empty_result(timeframe, str(e))
    
    def _apply_timeframe_specific_analysis(self,
                                          timeframe: str,
                                          data: pd.DataFrame,
                                          base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """시간 프레임별 특화 분석"""
        insights = {}
        
        if timeframe == "short":
            # 단기: 초단타 지표 중시
            insights["intraday_volatility"] = self._calculate_intraday_volatility(data)
            insights["volume_surge"] = self._detect_volume_surge(data)
            insights["quick_momentum"] = self._check_quick_momentum(data)
            
        elif timeframe == "medium":
            # 중기: 스윙 트레이딩 최적 구간
            insights["swing_zones"] = self._identify_swing_zones(data)
            insights["trend_strength"] = self._measure_trend_strength(data)
            insights["breakout_potential"] = self._assess_breakout_potential(data)
            
        elif timeframe == "long":
            # 장기: 펀더멘털 및 거시 추세
            insights["long_term_trend"] = self._analyze_long_term_trend(data)
            insights["accumulation_phase"] = self._detect_accumulation(data)
            insights["macro_alignment"] = self._check_macro_alignment(base_analysis)
        
        return insights
    
    def _calculate_intraday_volatility(self, data: pd.DataFrame) -> Dict[str, Any]:
        """일중 변동성 계산 (단기 트레이딩용)"""
        if len(data) < 5:
            return {"status": "insufficient_data"}
        
        recent = data.tail(10)
        avg_range = ((recent['High'] - recent['Low']) / recent['Close'] * 100).mean()
        
        return {
            "avg_range_pct": round(avg_range, 2),
            "interpretation": "높은 변동성" if avg_range > 3 else "낮은 변동성",
            "trading_suitability": "적합" if 1.5 < avg_range < 5 else "부적합"
        }
    
    def _detect_volume_surge(self, data: pd.DataFrame) -> Dict[str, Any]:
        """거래량 급증 감지"""
        if len(data) < 20:
            return {"detected": False}
        
        avg_vol = data['Volume'].tail(20).mean()
        current_vol = data['Volume'].iloc[-1]
        ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        return {
            "detected": ratio > 2.0,
            "volume_ratio": round(ratio, 2),
            "message": f"평균 대비 {ratio:.1f}배 거래량" if ratio > 1.5 else "정상 거래량"
        }
    
    def _check_quick_momentum(self, data: pd.DataFrame) -> Dict[str, Any]:
        """단기 모멘텀 체크 (최근 3~5봉)"""
        if len(data) < 5:
            return {"momentum": "neutral"}
        
        recent_5 = data['Close'].tail(5)
        change_pct = ((recent_5.iloc[-1] - recent_5.iloc[0]) / recent_5.iloc[0] * 100)
        
        if change_pct > 2:
            momentum = "strong_bullish"
        elif change_pct > 0.5:
            momentum = "bullish"
        elif change_pct < -2:
            momentum = "strong_bearish"
        elif change_pct < -0.5:
            momentum = "bearish"
        else:
            momentum = "neutral"
        
        return {
            "momentum": momentum,
            "change_pct": round(change_pct, 2),
            "message": f"최근 5봉 {change_pct:+.2f}% 변동"
        }
    
    def _identify_swing_zones(self, data: pd.DataFrame) -> Dict[str, Any]:
        """스윙 트레이딩 최적 구간 식별"""
        if len(data) < 50:
            return {"zones": []}
        
        # 최근 50일 고점/저점
        recent = data.tail(50)
        resistance = recent['High'].max()
        support = recent['Low'].min()
        current = data['Close'].iloc[-1]
        
        # 현재 위치 판단
        range_size = resistance - support
        position_pct = ((current - support) / range_size * 100) if range_size > 0 else 50
        
        if position_pct < 30:
            zone = "하단 (매수 적기)"
        elif position_pct > 70:
            zone = "상단 (매도 적기)"
        else:
            zone = "중간 (관망)"
        
        return {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "current_position": round(position_pct, 1),
            "zone": zone
        }
    
    def _measure_trend_strength(self, data: pd.DataFrame) -> Dict[str, Any]:
        """추세 강도 측정 (ADX 개념)"""
        if len(data) < 20:
            return {"strength": "unknown"}
        
        # 간단한 추세 강도: 20일 이평선 기울기
        sma_20 = data['Close'].rolling(20).mean()
        slope = (sma_20.iloc[-1] - sma_20.iloc[-10]) / sma_20.iloc[-10] * 100
        
        if abs(slope) > 5:
            strength = "strong"
        elif abs(slope) > 2:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "상승" if slope > 0 else "하락"
        
        return {
            "strength": strength,
            "direction": direction,
            "slope_pct": round(slope, 2),
            "message": f"{strength.upper()} {direction} 추세"
        }
    
    def _assess_breakout_potential(self, data: pd.DataFrame) -> Dict[str, Any]:
        """돌파 가능성 평가"""
        if len(data) < 30:
            return {"potential": "low"}
        
        # 최근 30일 박스권 여부
        recent = data.tail(30)
        high = recent['High'].max()
        low = recent['Low'].min()
        current = data['Close'].iloc[-1]
        
        # 박스권 범위 (0으로 나누기 방지)
        box_range = ((high - low) / low * 100) if low > 0 else 0
        
        # 현재가가 고점 근처인지
        near_high = (current / high) > 0.95
        
        if box_range < 10 and near_high:
            potential = "high"
            message = "박스권 상단 돌파 임박"
        elif box_range < 10:
            potential = "medium"
            message = "박스권 횡보 중"
        else:
            potential = "low"
            message = "변동성 높음, 돌파 불확실"
        
        return {
            "potential": potential,
            "box_range_pct": round(box_range, 2),
            "near_resistance": near_high,
            "message": message
        }
    
    def _analyze_long_term_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """장기 추세 분석 (주봉 기준)"""
        if len(data) < 52:  # 1년치 주봉
            return {"trend": "insufficient_data"}
        
        # 52주 이동평균
        sma_52 = data['Close'].rolling(52).mean()
        current = data['Close'].iloc[-1]
        
        if pd.isna(sma_52.iloc[-1]):
            return {"trend": "insufficient_data"}
        
        above_52w = current > sma_52.iloc[-1]
        
        # 1년 수익률
        year_return = ((current - data['Close'].iloc[-52]) / data['Close'].iloc[-52] * 100)
        
        return {
            "trend": "상승" if above_52w else "하락",
            "above_52w_ma": above_52w,
            "year_return_pct": round(year_return, 2),
            "message": f"52주 이평선 {'상회' if above_52w else '하회'}, 연간 수익률 {year_return:+.1f}%"
        }
    
    def _detect_accumulation(self, data: pd.DataFrame) -> Dict[str, Any]:
        """매집 국면 감지 (장기 투자용)"""
        if len(data) < 20:
            return {"phase": "unknown"}
        
        # OBV 추세
        obv = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
        obv_trend = obv.iloc[-1] > obv.iloc[-10]
        
        # 가격은 횡보하는데 OBV는 상승 = 매집
        price_flat = abs((data['Close'].iloc[-1] - data['Close'].iloc[-10]) / data['Close'].iloc[-10]) < 0.05
        
        if price_flat and obv_trend:
            phase = "accumulation"
            message = "가격 횡보 중 거래량 증가 → 세력 매집 가능성"
        elif obv_trend:
            phase = "markup"
            message = "가격 상승과 함께 거래량 증가 → 상승 추세"
        else:
            phase = "distribution"
            message = "거래량 감소 → 분산 또는 관망"
        
        return {
            "phase": phase,
            "obv_rising": obv_trend,
            "message": message
        }
    
    def _check_macro_alignment(self, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """거시 환경 정렬 확인"""
        macro = base_analysis.get('macro', {})
        macro_score = macro.get('score', 50)
        
        if macro_score > 60:
            alignment = "favorable"
            message = "거시 환경이 우호적입니다"
        elif macro_score < 40:
            alignment = "unfavorable"
            message = "거시 환경이 불리합니다"
        else:
            alignment = "neutral"
            message = "거시 환경은 중립적입니다"
        
        return {
            "alignment": alignment,
            "macro_score": macro_score,
            "message": message
        }
    
    def _calculate_timeframe_entry_points(self,
                                         timeframe: str,
                                         data: pd.DataFrame,
                                         analysis: Dict[str, Any],
                                         patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        시간 프레임별 맞춤 매수/매도 타점 계산
        
        Returns:
            {
                "buy_zone": [...],
                "sell_zone": [...],
                "stop_loss": float,
                "take_profit": [...],
                "risk_reward_ratio": float
            }
        """
        current_price = data['Close'].iloc[-1]
        
        if timeframe == "short":
            # 단기: 빠른 진입/청산
            return self._calculate_short_term_points(data, current_price, patterns)
        elif timeframe == "medium":
            # 중기: 스윙 존 기반
            return self._calculate_medium_term_points(data, current_price, patterns)
        else:  # long
            # 장기: 가치 기반 타점
            return self._calculate_long_term_points(data, current_price, analysis)
    
    def _calculate_short_term_points(self, data: pd.DataFrame, current: float, patterns: List) -> Dict:
        """단기 (데이 트레이딩) 타점"""
        # 최근 10봉 기준
        recent = data.tail(10)
        
        # 지지/저항 (단기)
        support = recent['Low'].min()
        resistance = recent['High'].max()
        
        # ATR 기반 손절/익절
        atr = ((recent['High'] - recent['Low']).mean())
        
        buy_zones = []
        sell_zones = []
        
        # 패턴 기반 타점 추가
        for p in patterns[:3]:
            if p.get('target'):
                if p['type'] in ['bullish_reversal', 'bullish_continuation']:
                    buy_zones.append({
                        "price": current * 0.995,  # 현재가 근처
                        "reason": f"{p['name']} 패턴 (신뢰도 {p['reliability']}/5)"
                    })
                    sell_zones.append({
                        "price": p['target'],
                        "reason": f"{p['name']} 목표가"
                    })
        
        # 기본 타점
        if not buy_zones:
            buy_zones.append({
                "price": round(support * 1.005, 2),
                "reason": "단기 지지선 근처"
            })
        
        if not sell_zones:
            sell_zones.append({
                "price": round(resistance * 0.995, 2),
                "reason": "단기 저항선 근처"
            })
        
        return {
            "buy_zone": buy_zones,
            "sell_zone": sell_zones,
            "stop_loss": round(current - atr * 1.5, 2),
            "take_profit": round(current + atr * 2, 2),
            "risk_reward_ratio": 1.33,
            "timeframe_note": "단기 트레이딩: 빠른 진입/청산 권장"
        }
    
    def _calculate_medium_term_points(self, data: pd.DataFrame, current: float, patterns: List) -> Dict:
        """중기 (스윙) 타점"""
        # 최근 50봉 기준
        recent = data.tail(50)
        
        support = recent['Low'].min()
        resistance = recent['High'].max()
        
        # 피보나치 되돌림 레벨
        fib_levels = {
            "0.236": resistance - (resistance - support) * 0.236,
            "0.382": resistance - (resistance - support) * 0.382,
            "0.500": resistance - (resistance - support) * 0.500,
            "0.618": resistance - (resistance - support) * 0.618
        }
        
        buy_zones = []
        sell_zones = []
        
        # 패턴 기반
        for p in patterns[:3]:
            if p.get('target') and p['type'] in ['bullish_reversal', 'bullish_continuation']:
                buy_zones.append({
                    "price": round(current * 0.98, 2),
                    "reason": f"{p['name']} (신뢰도 {p['confidence']}%)"
                })
                sell_zones.append({
                    "price": round(p['target'], 2),
                    "reason": f"{p['name']} 목표가"
                })
        
        # 피보나치 기반
        buy_zones.append({
            "price": round(fib_levels["0.618"], 2),
            "reason": "피보나치 0.618 되돌림 (황금비율)"
        })
        
        sell_zones.append({
            "price": round(resistance, 2),
            "reason": "50일 고점 저항선"
        })
        
        return {
            "buy_zone": buy_zones,
            "sell_zone": sell_zones,
            "stop_loss": round(support * 0.97, 2),
            "take_profit": round(resistance * 1.05, 2),
            "risk_reward_ratio": 2.0,
            "fibonacci_levels": fib_levels,
            "timeframe_note": "스윙 트레이딩: 1~3개월 보유 목표"
        }
    
    def _calculate_long_term_points(self, data: pd.DataFrame, current: float, analysis: Dict) -> Dict:
        """장기 (포지션) 타점"""
        # 200주 이평선 기준
        sma_200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else current * 0.9
        
        # 52주 고점/저점
        high_52w = data['High'].tail(52).max() if len(data) >= 52 else current * 1.2
        low_52w = data['Low'].tail(52).min() if len(data) >= 52 else current * 0.8
        
        buy_zones = [
            {
                "price": round(sma_200, 2),
                "reason": "200일 이동평균선 (장기 지지)"
            },
            {
                "price": round(low_52w * 1.05, 2),
                "reason": "52주 저점 근처 (가치 매수)"
            }
        ]
        
        sell_zones = [
            {
                "price": round(high_52w, 2),
                "reason": "52주 고점 (차익 실현)"
            },
            {
                "price": round(current * 1.3, 2),
                "reason": "장기 목표가 (+30%)"
            }
        ]
        
        return {
            "buy_zone": buy_zones,
            "sell_zone": sell_zones,
            "stop_loss": round(sma_200 * 0.90, 2),
            "take_profit": round(high_52w * 1.1, 2),
            "risk_reward_ratio": 3.0,
            "timeframe_note": "장기 투자: 6개월~수년 보유, 펀더멘털 중시"
        }
    
    def _generate_timeframe_recommendation(self,
                                          timeframe: str,
                                          analysis: Dict[str, Any],
                                          specialized: Dict[str, Any]) -> str:
        """시간 프레임별 맞춤 추천"""
        score = analysis['final_score']
        signal = analysis['signal']
        
        recommendations = []
        recommendations.append(f"[{self.TIMEFRAMES[timeframe]['name']}]")
        recommendations.append(f"종합 신호: {signal} ({score}점)")
        
        if timeframe == "short":
            vol = specialized.get('intraday_volatility', {})
            if vol.get('trading_suitability') == '적합':
                recommendations.append("✅ 단타 매매에 적합한 변동성입니다.")
            
            momentum = specialized.get('quick_momentum', {})
            if momentum.get('momentum') in ['strong_bullish', 'bullish']:
                recommendations.append("🚀 단기 상승 모멘텀이 감지되었습니다.")
        
        elif timeframe == "medium":
            zones = specialized.get('swing_zones', {})
            zone = zones.get('zone', '')
            if '매수' in zone:
                recommendations.append("💰 스윙 매수 적기입니다.")
            elif '매도' in zone:
                recommendations.append("💸 스윙 매도 적기입니다.")
        
        elif timeframe == "long":
            trend = specialized.get('long_term_trend', {})
            if trend.get('trend') == '상승':
                recommendations.append("📈 장기 상승 추세가 유지되고 있습니다.")
            
            accum = specialized.get('accumulation_phase', {})
            if accum.get('phase') == 'accumulation':
                recommendations.append("🎯 세력 매집 국면으로 보입니다. 장기 보유 고려.")
        
        return "\n".join(recommendations)
    
    def _generate_consensus(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """3개 시간 프레임 종합 컨센서스"""
        scores = []
        signals = []
        
        for tf in ["short_term", "medium_term", "long_term"]:
            if results[tf]:
                scores.append(results[tf]['score'])
                signals.append(results[tf]['signal'])
        
        if not scores:
            return {"consensus": "분석 불가", "confidence": 0}
        
        avg_score = np.mean(scores)
        
        # 신호 일치도
        bullish_count = sum(1 for s in signals if '매수' in s)
        bearish_count = sum(1 for s in signals if '매도' in s)
        
        if bullish_count >= 2:
            consensus = "🚀 다중 시간 프레임 매수 신호"
            confidence = 80 + (bullish_count - 2) * 10
        elif bearish_count >= 2:
            consensus = "📉 다중 시간 프레임 매도 신호"
            confidence = 80 + (bearish_count - 2) * 10
        else:
            consensus = "💬 시간 프레임 간 신호 불일치 (관망)"
            confidence = 50
        
        # 앙상블 합치기
        ensembles = []
        for tf in ["short_term", "medium_term", "long_term"]:
            if results[tf] and "full_analysis" in results[tf]:
                ensembles.append(results[tf]['full_analysis'].get('ensemble'))
            else:
                ensembles.append(None)
        global_ensemble = None
        if ensembles and ensembles[1]: # 중기(Daily) 앙상블을 메인으로 사용
            global_ensemble = ensembles[1]
        
        return {
            "consensus": consensus,
            "avg_score": round(avg_score, 1),
            "confidence": confidence,
            "global_ensemble": global_ensemble,
            "short_signal": results['short_term']['signal'] if results['short_term'] else "N/A",
            "medium_signal": results['medium_term']['signal'] if results['medium_term'] else "N/A",
            "long_signal": results['long_term']['signal'] if results['long_term'] else "N/A",
            "recommendation": self._final_recommendation(avg_score, confidence, bullish_count, bearish_count)
        }
    
    def _final_recommendation(self, avg_score: float, confidence: int, 
                             bullish: int, bearish: int) -> str:
        """최종 종합 추천"""
        lines = []
        
        if bullish >= 2 and avg_score > 65:
            lines.append("✅ 모든 시간 프레임에서 긍정적 신호가 포착되었습니다.")
            lines.append("💡 단기 트레이딩부터 장기 투자까지 모두 고려할 수 있습니다.")
        elif bearish >= 2:
            lines.append("⚠️ 여러 시간 프레임에서 부정적 신호가 감지되었습니다.")
            lines.append("💡 신규 진입보다는 관망 또는 기존 포지션 정리를 고려하세요.")
        else:
            lines.append("💬 시간 프레임별로 신호가 엇갈립니다.")
            lines.append("💡 본인의 투자 스타일에 맞는 시간 프레임의 신호를 우선 참고하세요.")
        
        return "\n".join(lines)
    
    async def _fetch_data(self, ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        """MarketDataCollector를 통한 데이터 수집 (비동기)"""
        try:
            # interval 정규화 (yf와 collector 간 차이 조정)
            if interval == "1h": interval = "60m"
            
            df = await self.collector.get_ohlcv(ticker, period=period, interval=interval)
            
            # 인덱스를 Datetime으로 설정 (패턴 감정 등에서 필요)
            if df is not None and not df.empty:
                if 'Date' in df.columns:
                    df.set_index(pd.to_datetime(df['Date']), inplace=True)
                return df
            return None
        except Exception as e:
            logger.warning(f"{ticker} 데이터 수집 실패 ({period}/{interval}): {e}")
            return None
    
    def _empty_result(self, timeframe: str, reason: str) -> Dict[str, Any]:
        """빈 결과 반환"""
        return {
            "timeframe": timeframe,
            "name": self.TIMEFRAMES[timeframe]["name"],
            "error": reason,
            "score": 50,
            "signal": "분석 불가"
        }


# 사용 예시
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MultiTimeframeAnalyzer()
    result = analyzer.analyze_all_timeframes("AAPL")
    
    print("\n=== 다중 시간 프레임 분석 결과 ===")
    print(f"\n{result['consensus']['consensus']}")
    print(f"신뢰도: {result['consensus']['confidence']}%")
    print(f"\n{result['consensus']['recommendation']}")
