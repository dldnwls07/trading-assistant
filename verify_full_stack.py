import asyncio
import logging
import sys
import io

# Set encoding to avoid unicode errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Mock environment if needed
import os
os.environ["GEMINI_API_KEY"] = "test_key"

from src.agents.screener import StockScreener
from src.services.integration_service import get_integration_service

logging.basicConfig(level=logging.INFO)

async def main():
    print("=== Testing StockScreener Output ===")
    screener = StockScreener()
    # Mock data fetching to return predictable results if possible, 
    # but for now we rely on the logic structure.
    
    # We will invoke _generate_reason directly with a mock result to see what it produces
    mock_result = {
        'consensus': {'consensus': '매수 권고 (Buy)', 'avg_score': 65},
        'short_term': {'signal': '매수'},
        'medium_term': {
            'signal': '중립',
            'full_analysis': {
                'market_regime': {'regime': 'Bear', 'label': '약세장 (Bear Market)', 'color': '#f43f5e', 'desc': '장기 이평선 아래에서 하락 압박을 받고 있습니다.'}
            }
        },
        'long_term': {'signal': '매수'}
    }
    
    reason = screener._generate_reason(mock_result, "balanced")
    print(f"Generated Reason:\n{reason}")
    
    print("\n=== Testing Integration Service (Mock) ===")
    # Integration service calls multi_analyzer, which might be okay.
    # But the issue is likely in screener.py as that's where get_recommendations comes from.

if __name__ == "__main__":
    asyncio.run(main())
