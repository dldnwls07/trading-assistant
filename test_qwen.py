import urllib.request
import json
import time

def test_qwen_report():
    url = "http://127.0.0.1:8000/analyze/ORCL?lang=ko"
    headers = {'X-API-Key': 'trading-assistant-secret-2024'}
    
    print(f"Requesting analysis for ORCL (expecting Qwen via Groq)...")
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            t1 = time.time()
            print(f"Done in {t1-t0:.2f}s")
            print(f"Signal: {data.get('signal')}")
            print(f"Score: {data.get('final_score')}")
            print("\n--- REPORT START ---")
            print(data.get('full_report'))
            print("--- REPORT END ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_qwen_report()
