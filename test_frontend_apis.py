import urllib.request
import urllib.error
import json

def test_json_api(url, name):
    print(f"\n[{name}] Testing {url} ...")
    try:
        req = urllib.request.Request(url, headers={'X-API-Key': 'trading-assistant-secret-2024'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode()
            print(f"✅ Success! Response length: {len(data)}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"❌ Other Error: {e}")

if __name__ == "__main__":
    ticker = "ORCL"
    # Test 1: Analysis
    test_json_api(f"http://127.0.0.1:8000/analyze/{ticker}?lang=ko", "Analysis API")
    
    # Test 2: History
    test_json_api(f"http://127.0.0.1:8000/history/{ticker}?interval=1d", "History API")
    
    # Test 3: Hybrid
    try:
        print(f"\n[Hybrid API] Testing POST http://127.0.0.1:8000/api/analysis/kr/hybrid ...")
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/analysis/kr/hybrid",
            method="POST",
            headers={'X-API-Key': 'trading-assistant-secret-2024', 'Content-Type': 'application/json'},
            data=json.dumps({"ticker": ticker, "news": ["test"]}).encode('utf-8')
        )
        with urllib.request.urlopen(req) as response:
            data = response.read().decode()
            print(f"✅ Success! Response length: {len(data)}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"❌ Other Error: {e}")
