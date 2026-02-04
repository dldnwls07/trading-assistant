from pathlib import Path

import click
import pandas as pd

from . import data_source
from .ai_analysis import generate_analysis_prompt
from .validation import validate_ohlcv

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@click.group()
def main():
    """Trading Assistant CLI - prototype"""
    pass


@main.command()
@click.argument("ticker")
@click.option(
    "--period",
    default="1y",
    help="Data period (e.g., 1mo, 6mo, 1y)",
)
@click.option(
    "--interval",
    default="1d",
    help="Data interval (e.g., 1d, 1h)",
)
def fetch(ticker, period, interval):
    """Fetch OHLCV data for TICKER and save to data/<TICKER>.csv"""
    msg_head = f"Fetching {ticker} ({period},"
    msg_tail = f" {interval})..."
    click.echo(msg_head + msg_tail)

    try:
        df = data_source.fetch(ticker, period=period, interval=interval)
    except RuntimeError:
        click.echo("No data returned. Check ticker or network.")
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error fetching data: {e}")
        raise click.Abort()

    # Validate OHLCV structure and values
    try:
        validate_ohlcv(df)
    except ValueError as e:
        click.echo(f"Data validation failed: {e}")
        raise click.Abort()

    try:
        filepath = DATA_DIR / f"{ticker.upper()}.csv"
        df.to_csv(filepath)
        click.echo(f"Saved to {filepath}")
    except Exception as e:
        click.echo(f"Error saving data: {e}")
        raise click.Abort()


@main.command()
@click.argument("ticker")
def summary(ticker):
    """Show a brief summary for TICKER (last close, volume)"""
    filepath = DATA_DIR / f"{ticker.upper()}.csv"
    if not filepath.exists():
        msg = f"Data for {ticker} not found. Run `fetch` first."
        click.echo(msg)
        raise click.Abort()
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    last = df.iloc[-1]
    close = last["Close"]
    volume = int(last["Volume"])
    head = f"{ticker.upper()} - Close: {close},"
    tail = f" Volume: {volume}"
    click.echo(head + tail)


@main.command()
@click.argument("ticker")
def financials(ticker):
    """Fetch and display financial statements for TICKER."""
    click.echo(f"Fetching financials for {ticker.upper()}...")
    try:
        df = data_source.get_financials(ticker)
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print(df)
    except RuntimeError as e:
        click.echo(f"Error: {e}. Check ticker or network.")
        raise click.Abort()
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
        raise click.Abort()


@main.command()
@click.argument("ticker")
def analyze(ticker):
    """Analyze Moving Average Golden Cross (MA50 vs MA200)"""
    filepath = DATA_DIR / f"{ticker.upper()}.csv"
    if not filepath.exists():
        click.echo(f"Data for {ticker} not found. Run 'fetch {ticker}' first.")
        raise click.Abort()

    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    if len(df) < 200:
        click.echo(f"Not enough data for MA200 analysis (Rows: {len(df)})")
        raise click.Abort()

    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    last_ma50 = df["MA50"].iloc[-1]
    last_ma200 = df["MA200"].iloc[-1]

    signal = (
        "GOLDEN CROSS (Bullish) 📈"
        if last_ma50 > last_ma200
        else "DEATH CROSS (Bearish) 📉"
    )
    click.echo(
        f"[{ticker.upper()}] {signal}\nMA50: {last_ma50:.2f} | MA200: {last_ma200:.2f}"
    )


@main.command()
def screen():
    """Screen for Golden Cross (MA50 > MA200) across all saved data."""
    if not DATA_DIR.exists():
        click.echo("No data directory found. Run 'fetch' first.")
        raise click.Abort()

    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        click.echo("No data files found. Run 'fetch <ticker>' first.")
        raise click.Abort()

    click.echo(f"Screening {len(csv_files)} stocks for Golden Cross...")
    found = []

    for filepath in csv_files:
        try:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            if len(df) < 200:
                continue

            df["MA50"] = df["Close"].rolling(window=50).mean()
            df["MA200"] = df["Close"].rolling(window=200).mean()

            last_ma50 = df["MA50"].iloc[-1]
            last_ma200 = df["MA200"].iloc[-1]

            if last_ma50 > last_ma200:
                found.append((filepath.stem, last_ma50, last_ma200))
        except Exception:
            continue

    if found:
        click.echo(f"\nFound {len(found)} stocks with Golden Cross (Bullish) 🚀:")
        for ticker, ma50, ma200 in found:
            click.echo(f"- {ticker}: MA50({ma50:.2f}) > MA200({ma200:.2f})")
    else:
        click.echo("\nNo stocks found matching the criteria.")


@main.command()
@click.argument("ticker")
def ai_prompt(ticker):
    """Generate a prompt for AI analysis (Copy & Paste to ChatGPT/Claude)."""
    filepath = DATA_DIR / f"{ticker.upper()}.csv"
    if not filepath.exists():
        click.echo(f"Data for {ticker} not found. Run 'fetch {ticker}' first.")
        raise click.Abort()

    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    click.echo(f"Generating AI prompt for {ticker}...\n")
    click.echo("-" * 40)
    prompt = generate_analysis_prompt(ticker, df)
    click.echo(prompt)
    click.echo("-" * 40)
    click.echo("\nTip: Copy the text above and paste it into ChatGPT or Claude!")


@main.command()
@click.argument("ticker")
def quote(ticker):
    """Get a real-time quote for TICKER using Alpaca."""
    click.echo(f"Fetching real-time quote for {ticker.upper()}...")
    try:
        quote_data = data_source.get_realtime_quote(ticker)
        if quote_data:
            click.echo(
                f"[{quote_data['ticker'].upper()}] "
                f"Bid: {quote_data['bid_price']} | "
                f"Ask: {quote_data['ask_price']} | "
                f"Time: {quote_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
        else:
            click.echo("Could not retrieve quote.")
    except (ConnectionError, ImportError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        raise click.Abort()


@main.command()
def account():
    """Show Alpaca account summary (Paper Trading)."""
    click.echo("Fetching account info...")
    try:
        info = data_source.get_account_info()
        if info:
            click.echo(f"💰 Account Status: {info['status']}")
            click.echo(f"💵 Cash: ${info['cash']:,.2f}")
            click.echo(f"📈 Portfolio Value: ${info['portfolio_value']:,.2f}")
            click.echo(f"💪 Buying Power: ${info['buying_power']:,.2f}")
        else:
            click.echo("Could not retrieve account info.")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
@click.argument("ticker")
@click.argument("qty", type=float)
def buy(ticker, qty):
    """Place a market BUY order for TICKER with QUANTITY."""
    click.echo(f"Placing market BUY order for {qty} shares of {ticker.upper()}...")

    # Safety confirmation
    if not click.confirm(
        f"Are you sure you want to buy {qty} shares of {ticker.upper()}?"
    ):
        click.echo("Order cancelled.")
        return

    try:
        order = data_source.place_market_order(ticker, qty, side="buy")
        if order:
            click.echo("✅ Order Submitted Successfully!")
            click.echo(f"Order ID: {order['id']}")
            click.echo(f"Status: {order['status']}")
            click.echo(
                f"Details: {order['side'].upper()} {order['qty']} {order['symbol']}"
            )
        else:
            click.echo("❌ Failed to place order.")
    except Exception as e:
        click.echo(f"Error: {e}")


@main.command()
def version():
    """Show version"""
    from . import __version__

    click.echo(__version__)


if __name__ == "__main__":
    main()
