import requests
import json
import time

url = "http://127.0.0.1:8000/api/analysis/kr/news"
payload = {
    "ticker": "005930",
    "news": [
        "삼성전자, 2024년 1분기 잠정 영업이익 6.6조원 기록. 전년 대비 931% 증가.",
        "메모리 반도체 업황 회복 본격화 및 HBM3E 공급 가시화.",
        "글로벌 AI 서버 수요 증가로 인한 DDR5 수요 강세 지속."
    ]
}

print(f"📡 Sending request to {url}...")
print("⚠️ Note: The first request might take 1-2 minutes to load the 7B model into VRAM.")

try:
    start_time = time.time()
    response = requests.post(url, json=payload, timeout=300)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Analysis Complete!")
        print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")
        print("\n=== [Thought Process] ===")
        print(result['thought'])
        print("\n=== [Final Solution] ===")
        print(result['solution'])
    else:
        print(f"❌ Request failed with status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error during request: {e}")
