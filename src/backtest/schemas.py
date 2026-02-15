from datetime import datetime
from pydantic import BaseModel, Field

# Backtest Requests
class BacktestRequest(BaseModel):
    ticker: str = Field(..., description="Target Ticker (e.g., BTC-USD, 005930.KS)")
    strategy_name: str = Field("sma_cross", description="Strategy Name (rsi, sma_cross)")
    start_date: str = Field("2023-01-01", description="Start Date (YYYY-MM-DD)")
    end_date: str = Field(datetime.now().strftime("%Y-%m-%d"), description="End Date")
    initial_capital: float = Field(10000000, description="Initial Capital")
    params: dict = Field({}, description="Strategy Parameters (fast, slow, period, etc.)")

# Optimizer Requests
class OptimizeRequest(BaseModel):
    ticker: str
    strategy_name: str
    target_metric: str = Field("sharpe_ratio", description="Target Metric to maximize")
    search_space: dict = Field(..., description="Grid Search Space")
    # Example: {"fast": [10, 20, 30], "slow": [50, 100, 200]}
