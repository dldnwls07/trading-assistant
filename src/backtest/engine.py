import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    High-Performance Vectorized Backtesting Engine.
    Simulates trading strategies on historical data.
    """
    
    def __init__(self, initial_capital: float = 10000.0, fee_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate # 0.1% per trade

    def run(self, df: pd.DataFrame, strategy) -> Dict[str, Any]:
        """
        Executes the strategy on the provided DataFrame.
        """
        if df is None or df.empty:
            return {"error": "No data provided"}

        logger.info(f"🚀 Running Backtest: {strategy.name} on {len(df)} candles...")
        
        # 1. Get Signals (-1, 0, 1)
        df = strategy.generate_signals(df)
        
        # 2. Simulate Trades (Shift signals by 1 to avoid look-ahead bias)
        # We enter at Open of T+1 based on Signal at Close of T
        df['position'] = df['Signal'].shift(1).fillna(0)
        
        # 3. Calculate Returns
        df['pct_change'] = df['Close'].pct_change()
        
        # Strategy Return: Position(yesterday) * Return(today)
        # If position is 1 (Long), we gain if price goes up.
        # If position is -1 (Short), we gain if price goes down.
        df['strategy_return'] = df['position'] * df['pct_change']
        
        # 4. Apply Transaction Costs
        # Trades occur when position changes
        trades = df['position'].diff().fillna(0).abs()
        df['strategy_return'] -= (trades * self.fee_rate)

        # 5. Calculate Cumulative Equity
        df['equity_curve'] = (1 + df['strategy_return']).cumprod() * self.initial_capital
        df['benchmark_curve'] = (1 + df['pct_change']).cumprod() * self.initial_capital
        
        # 6. Calculate Metrics
        final_equity = df['equity_curve'].iloc[-1]
        total_return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        
        # Sharpe Ratio (Annaulized, assuming daily data)
        risk_free_rate = 0.02
        excess_return = df['strategy_return'] - (risk_free_rate / 252)
        sharpe_ratio = np.sqrt(252) * (excess_return.mean() / excess_return.std())
        
        # MDD (Max Drawdown)
        rolling_max = df['equity_curve'].cummax()
        drawdown = df['equity_curve'] / rolling_max - 1.0
        max_drawdown = drawdown.min() * 100

        # Win Rate
        winning_days = len(df[df['strategy_return'] > 0])
        total_trading_days = len(df[df['position'] != 0])
        win_rate = (winning_days / total_trading_days * 100) if total_trading_days > 0 else 0

        logger.info(f"🏁 Backtest Complete. Return: {total_return_pct:.2f}% | Sharpe: {sharpe_ratio:.2f}")

        return {
            "strategy": strategy.name,
            "initial_capital": self.initial_capital,
            "final_equity": final_equity,
            "total_return_pct": total_return_pct,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_pct": max_drawdown,
            "win_rate": win_rate,
            "trade_count": trades.sum(),
            "equity_curve": df['equity_curve'].tolist(), # For plotting
            "dates": df.index.strftime('%Y-%m-%d').tolist() if isinstance(df.index, pd.DatetimeIndex) else df.index.tolist()
        }
