import pandas as pd
from . import config

def calculate_golden_cross(
    df: pd.DataFrame, 
    short_window: int = config.DEFAULT_MA_SHORT_WINDOW, 
    long_window: int = config.DEFAULT_MA_LONG_WINDOW
) -> dict:
    """
    Analyzes Moving Average Golden Cross (short_window vs long_window).

    Args:
        df: DataFrame with at least a 'Close' column.
        short_window: The short moving average window.
        long_window: The long moving average window.

    Returns:
        A dictionary containing the analysis result.
    """
    if df.empty or 'Close' not in df.columns:
        raise ValueError("Input DataFrame is empty or missing 'Close' column.")

    if len(df) < long_window:
        return {
            "error": f"Not enough data for {long_window}-day analysis (rows: {len(df)})"
        }

    # Use a copy to avoid SettingWithCopyWarning
    df_analysis = df.copy()
    
    df_analysis['MA_short'] = df_analysis["Close"].rolling(window=short_window).mean()
    df_analysis['MA_long'] = df_analysis["Close"].rolling(window=long_window).mean()

    last_ma_short = df_analysis['MA_short'].iloc[-1]
    last_ma_long = df_analysis['MA_long'].iloc[-1]

    signal = "Golden Cross (Bullish)" if last_ma_short > last_ma_long else "Death Cross (Bearish)"
    
    return {
        "signal": signal,
        "short_window": short_window,
        "long_window": long_window,
        f"ma_{short_window}": round(last_ma_short, 2),
        f"ma_{long_window}": round(last_ma_long, 2),
    }
