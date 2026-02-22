from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class TradingSignal(BaseModel):
    """
    RL 모델이 생성한 기술적 매매 신호 엔티티
    """
    ticker: str
    action: Literal["BUY", "SELL", "HOLD"]
    position_size: float  # 0.0 ~ 1.0
    generated_at: datetime = datetime.now()
    metadata: dict = {}

    @property
    def summary(self) -> str:
        return f"[{self.ticker}] Action: {self.action} ({self.position_size*100:.1f}%)"
