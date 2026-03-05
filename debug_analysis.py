import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

from src.services.integration_service import get_integration_service

async def test_analysis():
    logging.basicConfig(level=logging.INFO)
    service = get_integration_service()
    ticker = "TSLA"
    try:
        print(f"Starting analysis for {ticker}...")
        result = await service.run_comprehensive_analysis(ticker)
        if result.get("status") == "error":
            print(f"Error in result: {result.get('message')}")
        else:
            print(f"Success! Result keys: {result.keys()}")
            print(f"Signal: {result.get('consensus', {}).get('global_ensemble', {}).get('action')}")
    except Exception as e:
        print(f"Caught Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analysis())
