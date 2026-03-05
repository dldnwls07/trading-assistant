import urllib.request
import urllib.error
import json

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8000/analyze/ORCL?lang=ko', 
        headers={'X-API-Key': 'trading-assistant-secret-2024'}
    )
    with urllib.request.urlopen(req) as response:
        content = response.read().decode()
    with open('out.json', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success. Saved to out.json.")
except urllib.error.HTTPError as e:
    content = e.read().decode()
    with open('out.json', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"HTTP Error {e.code}. Saved to out.json.")
except Exception as e:
    print(f"Error: {e}")
