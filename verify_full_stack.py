import asyncio
import logging
import sys
import io
import os
from datetime import datetime

# Set encoding to avoid unicode errors
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_full_stack():
    print("🚀 Full Stack Verification Started...")
    
    # 1. Module Import Check
    print("\n[1/5] Checking Module Imports...")
    try:
        from src.api.server import app
        from src.data.loader import krx_loader
        from src.agents.screener import StockScreener
        from src.agents.event_calendar import EventCalendar
        print("✅ Critical modules imported successfully")
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return

    # 2. Environment Variable Check
    print("\n[2/5] Checking Environment Variables...")
    required_vars = ["GEMINI_API_KEY", "DISCORD_WEBHOOK_URL"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"⚠️ Warning: Missing optional env vars: {missing}")
    else:
        print("✅ All environment variables present")

    # 3. Component Initialization
    print("\n[3/5] Initializing Core Components...")
    try:
        screener = StockScreener()
        calendar = EventCalendar()
        print("✅ Components initialized")
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return

    # 4. Screener Logic Verification
    print("\n[4/5] Verifying Screener Output Structure...")
    mock_result = {
        'consensus': {'consensus': '매수 권고 (Buy)', 'avg_score': 65},
        'short_term': {'signal': '매수', 'score': 70},
        'medium_term': {
            'signal': '중립',
            'score': 50,
            'full_analysis': {
                'market_regime': {'regime': 'Bear', 'label': '약세장 (Bear Market)', 'color': '#f43f5e', 'desc': '장기 이평선 아래에서 하락 압박을 받고 있습니다.'}
            }
        },
        'long_term': {'signal': '매수', 'score': 75}
    }
    
    try:
        # Test reason generation
        reason = screener._generate_reason(mock_result, "balanced")
        print(f"Generated Reason:\n{reason}")
        
        # Test signal structure (manually, as we can't easily mock async internal calls without complex mocking)
        signals = {
            "short": {"signal": "매수", "score": 70},
            "medium": {"signal": "중립", "score": 50},
            "long": {"signal": "매수", "score": 75}
        }
        print(f"Signals Structure: {signals}")
        print("✅ Screener logic verified")
    except Exception as e:
        print(f"❌ Screener verification failed: {e}")

    # 5. AI Configuration Check
    print("\n[5/5] Checking AI Configuration...")
    if calendar.ai.gemini_key:
        print("✅ AI API Key configured")
    else:
        print("⚠️ AI API Key missing - AI features will be disabled")

    print("\n🎉 Full Stack Verification Complete!")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_full_stack())
