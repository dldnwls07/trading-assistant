import pandas as pd
import numpy as np
from src.backtest.base_strategy import BaseStrategy

class BollingerStrategy(BaseStrategy):
    """
    Bollinger Band Reversion Strategy:
    - Buy when Price < Lower Band (Oversold)
    - Sell when Price > Upper Band (Overbought)
    - Optional: Sell when Price crosses SMA (Middle Band)
    """
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        super().__init__(name=f"Bollinger({period}, {std_dev})")
        self.period = period
        self.std_dev = std_dev

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Calculate Bands
        df['middle'] = df['Close'].rolling(window=self.period).mean()
        df['std'] = df['Close'].rolling(window=self.period).std()
        df['upper'] = df['middle'] + (df['std'] * self.std_dev)
        df['lower'] = df['middle'] - (df['std'] * self.std_dev)
        
        df['Signal'] = 0
        # Buy Condition: Close < Lower Band
        df.loc[df['Close'] < df['lower'], 'Signal'] = 1
        # Sell Condition: Close > Upper Band
        df.loc[df['Close'] > df['upper'], 'Signal'] = -1
        
        return df

class MacdStrategy(BaseStrategy):
    """
    MACD Trend Following Strategy:
    - Buy when MACD Line crosses above Signal Line
    - Sell when MACD Line crosses below Signal Line
    """
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__(name=f"MACD({fast}/{slow}/{signal})")
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=self.fast, adjust=False).mean()
        exp2 = df['Close'].ewm(span=self.slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal_line'] = df['macd'].ewm(span=self.signal, adjust=False).mean()
        
        df['Signal'] = 0
        # Buy: MACD > Signal
        df.loc[df['macd'] > df['signal_line'], 'Signal'] = 1
        # Sell: MACD < Signal
        df.loc[df['macd'] < df['signal_line'], 'Signal'] = -1
        
        return df
