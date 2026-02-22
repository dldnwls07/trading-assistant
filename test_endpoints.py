import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print('Importing FastAPI app...')
try:
    from src.api.server import app
except Exception as e:
    print(f'Import error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

client = TestClient(app)

endpoints_to_test = [
    ('/api/calendar', 'GET', {}),
    ('/api/virtual/account', 'GET', {}),
    ('/api/screener/recommendations?style=balanced&market=US', 'GET', {}),
    ('/api/chat', 'POST', {'message': 'Hello'}),
]

print('Testing endpoints...')
for url, method, data in endpoints_to_test:
    print(f'Testing {method} {url}...')
    try:
        if method == 'GET':
            response = client.get(url)
        else:
            response = client.post(url, json=data)
        print(f'[{url}] Status code: {response.status_code}')
        # Check if 500
        if response.status_code >= 500:
            print(f'Error details: {response.text}')
    except Exception as e:
        print(f'[{url}] Exception: {e}')
        
print('Test complete!')
