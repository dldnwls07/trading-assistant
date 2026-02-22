from abc import ABC, abstractmethod
from src.domains.analysis_kr.entities.analysis import WONAnalysisResult

class LocalAnalyst(ABC):
    """
    로컬 AI 분석가를 위한 추상 인터페이스
    """
    @abstractmethod
    async def analyze(self, ticker: str, context: str) -> WONAnalysisResult:
        pass

    @abstractmethod
    def load_model(self):
        pass
