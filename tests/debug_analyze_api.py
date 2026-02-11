
import requests
import json

def test_analyze_api(ticker="AAPL"):
    url = f"http://127.0.0.1:8000/analyze/{ticker}"
    print(f"Testing API: {url}")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Response received successfully!")
            print(f"Keys in response: {list(data.keys())}")
            
            # Check for multi-timeframe data
            timeframe_keys = ["short_term", "medium_term", "long_term", "consensus"]
            found_keys = [k for k in timeframe_keys if k in data]
            
            if found_keys:
                print(f"💡 Found timeframe keys: {found_keys}")
            else:
                print("❌ Multi-timeframe analysis (short/medium/long) is MISSING in the current API response.")
                
            # Check for portfolio/recommendation related structure if possible
            # (Note: analyze result is for a single stock, so we check general structure)
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_analyze_api()
