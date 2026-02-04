"""Data source abstraction for fetching market data.

Provides functions to wrap underlying data providers (e.g., yfinance, tradingeconomics).
This makes it easy to swap providers or to mock in tests.
"""

import os
from typing import Optional

import pandas as pd
import yfinance as yf

try:
    import tradingeconomics as te
except ImportError:
    te = None
try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest
    from alpaca.trading.client import TradingClient
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.trading.requests import MarketOrderRequest
except Exception:
    StockHistoricalDataClient = None
    StockLatestQuoteRequest = None
    TradingClient = None
    MarketOrderRequest = None
    OrderSide = None
    TimeInForce = None


def fetch(ticker: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data for `ticker`.

    Raises RuntimeError if no data is returned.
    """
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise RuntimeError("No data returned")

    # Flatten MultiIndex columns if present (fix for yfinance v0.2+)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Remove duplicate columns if any (fixes yfinance returning duplicates)
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def get_economic_calendar(country: str = "United States") -> Optional[pd.DataFrame]:
    """
    Fetches economic calendar data for a given country.

    Returns a pandas DataFrame or None if an error occurs.
    """
    if te is None:
        print("tradingeconomics library is not installed. Skipping.")
        return None
    try:
        # Initialize with API key from environment variable if it exists.
        # The library works with sample data even if the key is not provided.
        te_key = os.getenv("TRADING_ECONOMICS_KEY")
        if te_key:
            te.login(te_key)
        else:
            # Login with 'guest:guest' for sample data
            te.login("guest:guest")

        # Fetch calendar data
        calendar_df = te.getCalendarData(country=country, output_type="df")

        if isinstance(calendar_df, pd.DataFrame) and not calendar_df.empty:
            return calendar_df
        else:
            print("No economic calendar data returned.")
            return None
    except Exception as e:
        print(f"An error occurred while fetching economic calendar data: {e}")
        return None


def get_financials(ticker: str) -> pd.DataFrame:
    """Fetch financial statements for `ticker`.

    Raises RuntimeError if no data is returned.
    """
    t = yf.Ticker(ticker)
    # financials is a DataFrame
    financials = t.financials
    if financials.empty:
        raise RuntimeError("No financial data returned")
    return financials


def get_realtime_quote(ticker: str) -> Optional[dict]:
    """
    Fetches the latest real-time quote for a ticker using Alpaca.
    Requires APCA_API_KEY_ID and APCA_API_SECRET_KEY environment variables.
    """
    if StockHistoricalDataClient is None:
        raise ImportError("alpaca-py is not installed. Try 'pip install alpaca-py'.")

    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")

    if not api_key or not secret_key:
        raise ConnectionError("Alpaca API keys not configured in environment variables")

    client = StockHistoricalDataClient(api_key, secret_key)

    try:
        ticker = ticker.upper()
        request_params = StockLatestQuoteRequest(symbol_or_symbols=ticker)
        res = client.get_stock_latest_quote(request_params)
        if ticker not in res:
            return None
        quote = res[ticker]
        return {
            "ticker": ticker,
            "bid_price": quote.bid_price,
            "ask_price": quote.ask_price,
            "timestamp": pd.to_datetime(quote.timestamp).tz_convert("Asia/Seoul"),
        }
    except Exception as e:
        print(f"Error fetching real-time quote for {ticker} from Alpaca: {e}")
        return None


def get_account_info() -> Optional[dict]:
    """
    Fetches account information using Alpaca Trading API.
    """
    if TradingClient is None:
        raise ImportError("alpaca-py is not installed. Try 'pip install alpaca-py'.")

    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")

    if api_key and not api_key.startswith("PK"):
        print("⚠️  WARNING: Your API Key does not start with 'PK'.")
        print(
            "   You are configured for Paper Trading (paper=True), but this looks like a Live Trading key."
        )
        print("   This may result in an 'unauthorized' error.")

    # Default to paper=True for safety in prototype
    client = TradingClient(api_key, secret_key, paper=True)

    try:
        account = client.get_account()
        return {
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "currency": account.currency,
            "status": account.status,
        }
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return None


def place_market_order(ticker: str, qty: float, side: str = "buy") -> Optional[dict]:
    """
    Places a market order using Alpaca Trading API.
    """
    if TradingClient is None:
        raise ImportError("alpaca-py is not installed. Try 'pip install alpaca-py'.")

    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")

    if not api_key or not secret_key:
        raise ConnectionError("Alpaca API keys not configured")

    if api_key and not api_key.startswith("PK"):
        print("⚠️  WARNING: Your API Key does not start with 'PK'.")
        print(
            "   You are configured for Paper Trading (paper=True), but this looks like a Live Trading key."
        )
        print("   This may result in an 'unauthorized' error.")

    client = TradingClient(api_key, secret_key, paper=True)

    try:
        ticker = ticker.upper()
        order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        market_order_data = MarketOrderRequest(
            symbol=ticker, qty=qty, side=order_side, time_in_force=TimeInForce.DAY
        )

        order = client.submit_order(order_data=market_order_data)
        return {
            "id": str(order.id),
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty else 0.0,
            "side": str(order.side),
            "status": str(order.status),
        }
    except Exception as e:
        print(f"Error placing order: {e}")
        if "unauthorized" in str(e).lower():
            print(
                "Hint: You are using Paper Trading (paper=True). Ensure your API Key starts with 'PK'."
            )
            print(
                "      If using Live keys, you must change the code to use paper=False."
            )
        return None
