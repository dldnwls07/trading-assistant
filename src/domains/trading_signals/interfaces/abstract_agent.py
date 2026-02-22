from abc import ABC, abstractmethod
from src.domains.trading_signals.entities.signal import TradingSignal
import pandas as pd

class RLTether(ABC):
    """
    강화학습 모델과의 연결을 위한 인터페이스
    """
    @abstractmethod
    async def predict_action(self, ticker: str, df: pd.DataFrame) -> TradingSignal:
        """
        OHLCV 및 기술적 지표 데이터프레임을 받아 다음 행동을 예측
        """
        pass

    @abstractmethod
    def load_agent(self, model_path: str):
        pass
