import requests
import json
import time

url = "http://127.0.0.1:8000/api/analysis/kr/hybrid"
payload = {
    "ticker": "005930.KS", # Ticker naming consistency
    "news": [
        "삼성전자, 차세대 반도체 공정 양산 성공 발표",
        "외국인 투자자 삼성전자 대규모 순매수 지속",
        "글로벌 경제 위축 우려로 인한 IT 수요 감소 불안감 존재"
    ]
}

print(f"📡 Sending HYBRID request to {url}...")
print("⚠️ Note: This involves multiple AI models (Local LLM + RL + Gemini).")

try:
    start_time = time.time()
    response = requests.post(url, json=payload, timeout=300)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Hybrid Analysis Complete!")
        print(f"⏱️ Time taken: {end_time - start_time:.2f} seconds")
        print(f"\n[RL Signal] Action: {result['rl_action']}, Confidence: {result['rl_confidence']*100:.1f}%")
        print("\n[WON-Reasoning Thought]")
        print(result['thought'][:200] + "...")
        print("\n[Hybrid Expert Comment (Gemini Synthesis)]")
        print(result['hybrid_comment'])
    else:
        print(f"❌ Request failed with status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error during request: {e}")
