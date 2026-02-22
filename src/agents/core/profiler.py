"""
투자자 프로파일링 시스템
사용자의 투자 성향을 분석하여 맞춤형 투자 스타일 분류
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class InvestorProfiler:
    """
    투자자 성향 분석 및 프로파일 관리
    """
    
    STYLES = {
        "aggressive_growth": {
            "name": "공격적 성장형",
            "description": "고위험 고수익을 추구하며, 성장주 중심의 단기 트레이딩을 선호합니다.",
            "risk_tolerance": "high",
            "time_horizon": "short",
            "preferred_sectors": ["Technology", "Healthcare", "Consumer Discretionary"]
        },
        "dividend": {
            "name": "안정적 배당형",
            "description": "저위험 안정 수익을 추구하며, 배당주 중심의 장기 보유를 선호합니다.",
            "risk_tolerance": "low",
            "time_horizon": "long",
            "preferred_sectors": ["Utilities", "Consumer Staples", "Real Estate"]
        },
        "value": {
            "name": "가치 투자형",
            "description": "저평가된 종목을 발굴하며, 펀더멘털을 중시하는 중장기 투자를 선호합니다.",
            "risk_tolerance": "medium",
            "time_horizon": "medium_long",
            "preferred_sectors": ["Financials", "Industrials", "Energy"]
        },
        "momentum": {
            "name": "모멘텀 트레이딩형",
            "description": "기술적 분석을 중시하며, 추세를 추종하는 단기~중기 투자를 선호합니다.",
            "risk_tolerance": "medium_high",
            "time_horizon": "short_medium",
            "preferred_sectors": ["Technology", "Communication Services", "Consumer Discretionary"]
        },
        "balanced": {
            "name": "균형 포트폴리오형",
            "description": "성장주와 안정주를 혼합하며, 리스크를 분산하는 중도적 투자를 선호합니다.",
            "risk_tolerance": "medium",
            "time_horizon": "medium",
            "preferred_sectors": ["Technology", "Healthcare", "Financials", "Consumer Staples"]
        }
    }
    
    def __init__(self, profile_path: str = "user_profile.json"):
        self.profile_path = profile_path
        self.profile = self._load_profile()
    
    def create_profile_from_survey(self, answers: Dict[str, Any]) -> str:
        """
        설문 응답을 바탕으로 투자 스타일 자동 분류
        
        Args:
            answers: 설문 응답 딕셔너리
                - risk_tolerance: 1~5 (1=매우 보수적, 5=매우 공격적)
                - time_horizon: "short" | "medium" | "long"
                - loss_tolerance: 1~5 (1=5% 손실도 힘듦, 5=30% 손실 감내 가능)
                - investment_goal: "growth" | "income" | "preservation" | "balanced"
                - trading_frequency: "daily" | "weekly" | "monthly" | "rarely"
        
        Returns:
            투자 스타일 키 (예: "aggressive_growth")
        """
        score = {
            "aggressive_growth": 0,
            "dividend": 0,
            "value": 0,
            "momentum": 0,
            "balanced": 0
        }
        
        # 1. 위험 감수도
        risk = answers.get('risk_tolerance', 3)
        if risk >= 4:
            score["aggressive_growth"] += 3
            score["momentum"] += 2
        elif risk <= 2:
            score["dividend"] += 3
            score["value"] += 1
        else:
            score["balanced"] += 2
            score["value"] += 1
        
        # 2. 투자 기간
        horizon = answers.get('time_horizon', 'medium')
        if horizon == "short":
            score["aggressive_growth"] += 2
            score["momentum"] += 3
        elif horizon == "long":
            score["dividend"] += 3
            score["value"] += 2
        else:
            score["balanced"] += 2
            score["value"] += 1
        
        # 3. 손실 감내도
        loss_tol = answers.get('loss_tolerance', 3)
        if loss_tol >= 4:
            score["aggressive_growth"] += 2
            score["momentum"] += 1
        elif loss_tol <= 2:
            score["dividend"] += 2
        
        # 4. 투자 목표
        goal = answers.get('investment_goal', 'balanced')
        if goal == "growth":
            score["aggressive_growth"] += 3
            score["momentum"] += 1
        elif goal == "income":
            score["dividend"] += 3
        elif goal == "preservation":
            score["dividend"] += 2
            score["value"] += 1
        else:
            score["balanced"] += 3
        
        # 5. 거래 빈도
        freq = answers.get('trading_frequency', 'monthly')
        if freq in ["daily", "weekly"]:
            score["momentum"] += 2
            score["aggressive_growth"] += 1
        elif freq == "rarely":
            score["dividend"] += 2
            score["value"] += 1
        
        # 최고 점수 스타일 선택
        style = max(score, key=score.get)
        
        # 프로파일 저장
        self.profile = {
            "style": style,
            "style_name": self.STYLES[style]["name"],
            "survey_answers": answers,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._save_profile()
        
        return style
    
    def get_style(self) -> Optional[str]:
        """현재 투자 스타일 반환"""
        return self.profile.get('style') if self.profile else None
    
    def get_style_info(self, style: str = None) -> Dict[str, Any]:
        """투자 스타일 상세 정보 반환"""
        if style is None:
            style = self.get_style()
        return self.STYLES.get(style, self.STYLES["balanced"])
    
    def update_profile(self, updates: Dict[str, Any]):
        """프로파일 업데이트"""
        if self.profile:
            self.profile.update(updates)
            self.profile['updated_at'] = datetime.now().isoformat()
            self._save_profile()
    
    def _load_profile(self) -> Optional[Dict[str, Any]]:
        """저장된 프로파일 로드"""
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"프로파일 로드 실패: {e}")
        return None
    
    def _save_profile(self):
        """프로파일 저장"""
        try:
            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.profile, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"프로파일 저장 실패: {e}")


# 사용 예시
if __name__ == "__main__":
    profiler = InvestorProfiler()
    
    # 설문 응답 예시
    survey_answers = {
        "risk_tolerance": 4,  # 높은 위험 감수
        "time_horizon": "short",  # 단기 투자
        "loss_tolerance": 4,  # 높은 손실 감내
        "investment_goal": "growth",  # 성장 추구
        "trading_frequency": "weekly"  # 주간 거래
    }
    
    style = profiler.create_profile_from_survey(survey_answers)
    print(f"분류된 투자 스타일: {profiler.STYLES[style]['name']}")
    print(f"설명: {profiler.STYLES[style]['description']}")
