import itertools
import pandas as pd
from typing import Dict, Any, List
import logging
from src.backtest.engine import BacktestEngine
from src.backtest.strategies.basic import RsiStrategy, SmaCrossStrategy

logger = logging.getLogger(__name__)

class StrategyOptimizer:
    """
    Finds the optimal parameters for a trading strategy using Grid Search.
    Goal: Maximize Sharpe Ratio or Total Return.
    """
    
    def __init__(self, engine: BacktestEngine):
        self.engine = engine

    def optimize(self, df: pd.DataFrame, strategy_cls, search_space: Dict[str, List[Any]], target_metric: str = "sharpe_ratio"):
        """
        Input:
            search_space: {"fast": [5, 10, 20], "slow": [50, 60, 100]}
        Output:
            Best parameter set and result
        """
        # Generate all combinations of parameters
        keys, values = zip(*search_space.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        best_score = -float('inf')
        best_result = None
        best_params = None
        
        logger.info(f"🔍 Starting Optimization: {len(combinations)} combinations...")
        
        for params in combinations:
            # Instantiate strategy with current params
            try:
                strategy = strategy_cls(**params)
                result = self.engine.run(df, strategy)
                
                score = result.get(target_metric, -float('inf'))
                
                # Check for NaN score
                if pd.isna(score):
                    score = -float('inf')

                if score > best_score:
                    best_score = score
                    best_result = result
                    best_params = params
                    
            except Exception as e:
                logger.warning(f"Optimization warning for {params}: {e}")
                continue
                
        logger.info(f"✅ Optimization Complete. Best {target_metric}: {best_score:.4f} with {best_params}")
        
        return {
            "best_params": best_params,
            "best_metric_value": best_score,
            "best_result": best_result,
            "all_combinations_count": len(combinations)
        }
