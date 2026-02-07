import requests
import json

API_BASE = "http://localhost:8000"

def test_analyze(ticker):
    print(f"\n--- Testing /analyze/{ticker} ---")
    try:
        res = requests.get(f"{API_BASE}/analyze/{ticker}")
        data = res.json()
        print(f"Status: {res.status_code}")
        print(f"Display Name: {str(data.get('display_name')).encode('ascii', 'ignore').decode('ascii')}")
        print(f"Final Score: {data.get('final_score')}")
        print(f"Signal: {str(data.get('signal')).encode('ascii', 'ignore').decode('ascii')}")
        
        # Check if patterns have points
        daily = data.get('daily_analysis', {})
        daily_patterns = daily.get('patterns', []) if daily else []
        print(f"Patterns found: {len(daily_patterns)}")
        for p in daily_patterns:
            print(f"  - Pattern: {p.get('name', 'N/A').encode('ascii', 'ignore').decode('ascii')}, Points: {len(p.get('points', []))}")
            if p.get('points'):
                print(f"    First point: {p['points'][0]}")
    except Exception as e:
        print(f"Error: {e}")

def test_history(ticker, interval="1d"):
    print(f"\n--- Testing /history/{ticker}?interval={interval} ---")
    try:
        res = requests.get(f"{API_BASE}/history/{ticker}?interval={interval}")
        data = res.json()
        print(f"Status: {res.status_code}")
        print(f"Ticker: {data.get('ticker')}")
        print(f"Data points: {len(data.get('data', []))}")
        
        if data.get('data'):
            last = data['data'][-1]
            print(f"Last point sample keys: {list(last.keys())}")
            # Check for technical indicators in history
            indicators = ['sma20', 'rsi', 'macd', 'bb_upper']
            found = [k for k in last if k in indicators and last[k] is not None]
            print(f"Indicators found in last data point: {found}")
            if 'rsi' in last:
                print(f"  - RSI Value: {last['rsi']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_analyze("NVDA")
    test_analyze("삼성전자")
    test_history("NVDA", "1d")
    test_history("NVDA", "60m")
