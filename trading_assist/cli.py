import click
from pathlib import Path
import yfinance as yf
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@click.group()
def main():
    """Trading Assistant CLI - prototype"""
    pass

@main.command()
@click.argument('ticker')
@click.option('--period', default='1mo', help='Data period (e.g., 1mo, 6mo, 1y)')
@click.option('--interval', default='1d', help='Data interval (e.g., 1d, 1h)')
def fetch(ticker, period, interval):
    """Fetch OHLCV data for TICKER and save to data/<TICKER>.csv"""
    click.echo(f"Fetching {ticker} ({period}, {interval})...")
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
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
@click.argument('ticker')
def summary(ticker):
    """Show a brief summary for TICKER (last close, volume)"""
    filepath = DATA_DIR / f"{ticker.upper()}.csv"
    if not filepath.exists():
        click.echo(f"Data for {ticker} not found. Run `fetch` first.")
        raise click.Abort()
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    last = df.iloc[-1]
    click.echo(f"{ticker.upper()} - Close: {last['Close']}, Volume: {int(last['Volume'])}")

@main.command()
def version():
    """Show version"""
    from . import __version__
    click.echo(__version__)

if __name__ == '__main__':
    main()
