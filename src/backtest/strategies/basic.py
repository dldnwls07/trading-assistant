import pandas as pd
import numpy as np
from src.backtest.base_strategy import BaseStrategy

class RsiStrategy(BaseStrategy):
    """
    Basic Mean Reversion Strategy:
    - Buy when RSI < 30 (Oversold)
    - Sell when RSI > 70 (Overbought)
    """
    def __init__(self, period: int = 14, buy_threshold: int = 30, sell_threshold: int = 70):
        super().__init__(name=f"RSI({period}) Strategy")
        self.period = period
        self.buy_k = buy_threshold
        self.sell_k = sell_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Avoid modifying the original dataframe
        df = df.copy()
        
        # 1. Calculate RSI Vectorized
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 2. Generate Signals (1: Buy, -1: Sell, 0: Hold)
        df['Signal'] = 0
        df.loc[df['rsi'] < self.buy_k, 'Signal'] = 1
        df.loc[df['rsi'] > self.sell_k, 'Signal'] = -1
        
        return df

class SmaCrossStrategy(BaseStrategy):
    """
    Trend Following Strategy:
    - Buy when Fast SMA crosses above Slow SMA (Golden Cross)
    - Sell when Fast SMA crosses below Slow SMA (Death Cross)
    """
    def __init__(self, fast: int = 20, slow: int = 60):
        super().__init__(name=f"SMA Cross({fast}/{slow})")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df['sma_fast'] = df['Close'].rolling(window=self.fast).mean()
        df['sma_slow'] = df['Close'].rolling(window=self.slow).mean()
        
        df['Signal'] = 0
        
        # Vectorized Cross logic implies checking previous state vs current state, 
        # but for simple signal generation, we can just denote the regime.
        # 1 = Long Regime, -1 = Short Regime
        df.loc[df['sma_fast'] > df['sma_slow'], 'Signal'] = 1
        df.loc[df['sma_fast'] < df['sma_slow'], 'Signal'] = -1
        
        return df
