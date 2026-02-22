from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from src.domains.trading_signals.services.signal_service import SignalService
from src.domains.trading_signals.infrastructure.rl_agent_adapter import RLAgentAdapter
from src.domains.trading_signals.entities.signal import TradingSignal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trading/signals", tags=["Trading Signals"])

# Lazy-loaded adapter for resource management
RL_ADAPTER = RLAgentAdapter()
SIGNAL_SERVICE = SignalService(RL_ADAPTER)

@router.get("/rl/{ticker}", response_model=TradingSignal)
async def get_rl_trading_signal(ticker: str):
    """
    RL Trading Agent(PPO)를 사용하여 특정 종목의 매매 신호를 생성합니다.
    """
    try:
        # 모델은 첫 요청 시 로드
        if RL_ADAPTER.model is None:
            RL_ADAPTER.load_bundle()
            
        signal = await SIGNAL_SERVICE.generate_rl_signal(ticker)
        return signal
    except Exception as e:
        logger.error(f"Failed to generate RL signal for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RL Signal Generation Failed: {str(e)}")
