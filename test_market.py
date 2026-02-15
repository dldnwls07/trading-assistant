from src.utils.market_utils import is_market_open, get_market_time

def test_market_utils():
    tickers = ["AAPL", "005930.KS", "NVDA", "068270.KS"]
    print("=== Market Status Check ===")
    for t in tickers:
        open_status = is_market_open(t)
        m_time = get_market_time(t)
        print(f"Ticker: {t:10} | Open: {str(open_status):5} | Market Time: {m_time}")

if __name__ == "__main__":
    test_market_utils()
