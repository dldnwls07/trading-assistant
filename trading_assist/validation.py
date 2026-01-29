import pandas as pd

REQUIRED_COLS = ["Open", "High", "Low", "Close", "Volume"]


def validate_ohlcv(df: pd.DataFrame) -> None:
    """Raise ValueError if df is not a valid OHLCV DataFrame.

    Checks:
    - Required columns present
    - No NaN in price columns
    - Close price > 0
    - Volume >= 0
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input is not a pandas DataFrame")

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # price cols not null
    price_cols = ["Open", "High", "Low", "Close"]
    if df[price_cols].isnull().any().any():
        raise ValueError("NaN detected in price columns")

    if (df["Close"] <= 0).any():
        raise ValueError("Non-positive close price detected")

    if (df["Volume"] < 0).any():
        raise ValueError("Negative volume detected")

    # basic range checks (optional)
    if (df["High"] < df["Low"]).any():
        raise ValueError("High < Low detected in data")
