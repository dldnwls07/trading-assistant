from fastapi import APIRouter, HTTPException
import logging

from src.api.utils import validate_ticker, safe_serialize
from src.api.dependencies import collector
from src.backtest.schemas import BacktestRequest, OptimizeRequest
from src.backtest.engine import BacktestEngine
from src.backtest.optimizer import StrategyOptimizer
from src.backtest.strategies.basic import RsiStrategy, SmaCrossStrategy
from src.backtest.strategies.advanced import BollingerStrategy, MacdStrategy

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Engine
backtest_engine = BacktestEngine(initial_capital=10000000)
strategy_optimizer = StrategyOptimizer(backtest_engine)

@router.post("/api/backtest/run")
async def run_backtest(req: BacktestRequest):
    """백테스팅 실행"""
    try:
        validate_ticker(req.ticker)
        df = await collector.get_ohlcv(req.ticker, period="2y", interval="1d")
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Historical data not found")
            
        strategy = None
        s_name = req.strategy_name.lower()
        
        if s_name == "rsi":
            period = req.params.get("period", 14)
            buy = req.params.get("buy_threshold", 30)
            sell = req.params.get("sell_threshold", 70)
            strategy = RsiStrategy(period=period, buy_threshold=buy, sell_threshold=sell)
            
        elif s_name in ["sma_cross", "golden_cross"]:
            fast = req.params.get("fast", 20)
            slow = req.params.get("slow", 60)
            strategy = SmaCrossStrategy(fast=fast, slow=slow)
            
        elif s_name == "bollinger":
            period = req.params.get("period", 20)
            std = req.params.get("std_dev", 2.0)
            strategy = BollingerStrategy(period=period, std_dev=std)
            
        elif s_name == "macd":
            fast = req.params.get("fast", 12)
            slow = req.params.get("slow", 26)
            sig = req.params.get("signal", 9)
            strategy = MacdStrategy(fast=fast, slow=slow, signal=sig)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy_name}")
            
        result = backtest_engine.run(df, strategy)
        return safe_serialize(result)
        
    except Exception as e:
        logger.error(f"Backtest run error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/backtest/optimize")
async def optimize_strategy(req: OptimizeRequest):
    """최적 파라미터 찾기 (Grid Search)"""
    try:
        validate_ticker(req.ticker)
        df = await collector.get_ohlcv(req.ticker, period="2y", interval="1d")
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="Historical data not found")
            
        strategy_cls = None
        s_name = req.strategy_name.lower()
        
        if s_name == "rsi":
            strategy_cls = RsiStrategy
        elif s_name in ["sma_cross", "golden_cross"]:
            strategy_cls = SmaCrossStrategy
        elif s_name == "bollinger":
            strategy_cls = BollingerStrategy
        elif s_name == "macd":
            strategy_cls = MacdStrategy
        else:
             raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy_name}")

        result = strategy_optimizer.optimize(
            df, 
            strategy_cls, 
            search_space=req.search_space,
            target_metric=req.target_metric
        )
        return safe_serialize(result)
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
