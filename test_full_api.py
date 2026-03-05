import urllib.request
import json
import time

def test_full_response():
    url = "http://127.0.0.1:8000/analyze/ORCL?lang=ko"
    headers = {'X-API-Key': 'trading-assistant-secret-2024'}
    
    print(f"Requesting full analysis for ORCL...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"Keys in response: {list(data.keys())}")
            if "events" in data:
                print(f"Events keys: {list(data['events'].keys())}")
                print(f"Earnings: {data['events'].get('earnings')}")
                print(f"Sector: {data['events'].get('sector')}")
                macro_count = len(data['events'].get('macro_events', []))
                print(f"Macro events count: {macro_count}")
                if macro_count > 0:
                    print(f"First macro event: {data['events']['macro_events'][0]['title']}")
            
            print("\nAI Report Summary:")
            print(data.get('full_report', '')[:100] + "...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_full_response()
