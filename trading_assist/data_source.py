"""Data source abstraction for fetching OHLCV data.

Provides a single function `fetch` that wraps the underlying data provider
(yfinance for now). This makes it easy to swap providers or to mock in tests.
"""

from typing import Optional

import pandas as pd
import yfinance as yf


def fetch(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data for `ticker`.

    Raises RuntimeError if no data is returned.
    """
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise RuntimeError("No data returned")
    return df
