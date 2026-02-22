import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class StrategyEnsemble:
    """
    고정밀 전략 앙상블 엔진
    여러 독자적 분석 엔진의 결과를 통합하여 최종 '거래 셋업'의 등급과 신뢰도를 산출
    """
    
    @staticmethod
    def calculate_ensemble(tech_results: Dict[str, Any], 
                           event_results: Dict[str, Any],
                           fund_results: Dict[str, Any],
                           sentiment_score: float = 50.0,
                           ml_forecast: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        앙상블 점수 계산
        - tech_results: TechnicalAnalyzer.analyze 결과 (patterns, divergences 포함)
        - event_results: EventCalendar.calculate_event_risk 결과
        - fund_results: FundamentalAnalyzer.analyze 결과
        """
        
        base_score = tech_results.get('score', 50)
        conf_details = []
        
        # 1. Technical Confluence (지표 합치) 보너스
        confluence_bonus = 0
        patterns = tech_results.get('patterns', [])
        divergences = tech_results.get('divergences', [])
        
        # 패턴과 다이버전스가 동시에 존재하는 경우 강력한 가중치
        bullish_patterns = [p for p in patterns if 'bullish' in p['type']]
        bullish_divs = [d for d in divergences if 'Bullish' in d['type']]
        
        if bullish_patterns and bullish_divs:
            confluence_bonus += 15
            conf_details.append("🔥 기술적 지표 합치: 차트 패턴과 보조지표 다이버전스가 동시에 상승을 가리킴 (강력한 신호)")
            
        # 2. Event Alignment (이벤트 정렬)
        event_impact = event_results.get('impact_score', 0.5) # 0.0 ~ 1.0 (낮을수록 안전)
        risk_adjustment = 0
        
        if event_impact > 0.8:
            risk_adjustment -= 10
            conf_details.append("⚠️ 고위험 이벤트 주의: 단기적으로 극심한 변동성이 예상되어 신뢰도 하향 조정")
        elif event_results.get('is_fomc_week', False):
            risk_adjustment -= 5
            conf_details.append("📅 FOMC 주간: 거시적 불확실성으로 인해 보수적 접근 권장")

        # 3. Fundamental Filter
        fund_score = fund_results.get('score', 50)
        fund_bonus = 0
        if fund_score > 70 and base_score > 60:
            fund_bonus += 10
            conf_details.append("💎 펀더멘탈 뒷받침: 우량한 재무 상태가 기술적 상승 셋업을 지지함")

        # 4. ML Forecast Bonus (Pillar 1)
        ml_bonus = 0
        if ml_forecast and ml_forecast.get('success'):
            if ml_forecast['direction'] == "상승" and ml_forecast['confidence'] > 70:
                ml_bonus += 10
                conf_details.append(f"🤖 AI ML 엔진 합치: 머신러닝이 5거래일 내 {ml_forecast['predicted_return']*100:.1f}% 상승을 예측함")

        # 최종 앙상블 점수 산출
        weighted_score = (base_score * 0.5) + (fund_score * 0.3) + (sentiment_score * 0.2)
        final_score = weighted_score + confluence_bonus + risk_adjustment + fund_bonus + ml_bonus
        final_score = max(0, min(100, final_score))
        
        # 셋업 등급 결정
        grade = "C"
        if final_score >= 85: grade = "S (자동매매 가능)"
        elif final_score >= 75: grade = "A (적극 권장)"
        elif final_score >= 65: grade = "B (양호)"
        
        return {
            "final_score": round(final_score, 1),
            "grade": grade,
            "confidence": min(98, final_score), # 100%는 없으므로 캡핑
            "confluence_details": conf_details,
            "risk_impact": event_impact,
            "recommendation": StrategyEnsemble._get_recommendation(grade, final_score)
        }

    @staticmethod
    def _get_recommendation(grade: str, score: float) -> str:
        if "S" in grade:
            return "최상의 트레이딩 옵션입니다. 모든 조건이 부합하며 자동 매매 집행이 가능한 고신뢰도 구간입니다."
        if "A" in grade:
            return "강력한 매수/매도 셋업입니다. 분할 진입을 고려할 수 있는 우수한 기회입니다."
        if "B" in grade:
            return "전략적으로 유효한 구간이나, 약간의 보수적인 접근이 필요합니다."
        return "현재는 확실한 셋업이 발견되지 않았습니다. 관망하며 다음 기회를 기다리세요."
