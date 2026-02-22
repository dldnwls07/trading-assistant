from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WONAnalysisResult(BaseModel):
    """
    WON-Reasoning 모델의 분석 결과를 담는 도메인 엔티티
    """
    ticker: str
    thought: str  # 모델의 생각 과정 (<think> 태그 내용)
    solution: str # 모델의 최종 결론 (<solution> 태그 내용)
    analyzed_at: datetime = datetime.now()
    
    @property
    def full_report(self) -> str:
        return f"--- Reasoning Path ---\n{self.thought}\n\n--- Final Solution ---\n{self.solution}"
