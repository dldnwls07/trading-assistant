from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract Base Class for all trading strategies.
    By enforcing this contract, we ensure all strategies are compatible with the BacktestEngine.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Input: DataFrame with OHLCV data
        Output: DataFrame with an added 'Signal' column (-1: Sell, 0: Hold, 1: Buy)
        
        Using vectorized operations(pandas/numpy) is mandatory for performance.
        NO LOOPS allowed here.
        """
        pass
