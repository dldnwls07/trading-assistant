from pathlib import Path

import click
import pandas as pd
import yfinance as yf

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
    default="1mo",
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
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
        )
        if df.empty:
            click.echo("No data returned. Check ticker or network.")
            raise click.Abort()
        filepath = DATA_DIR / f"{ticker.upper()}.csv"
        df.to_csv(filepath)
        click.echo(f"Saved to {filepath}")
    except Exception as e:
        click.echo(f"Error fetching data: {e}")
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
def version():
    """Show version"""
    from . import __version__

    click.echo(__version__)


if __name__ == "__main__":
    main()
