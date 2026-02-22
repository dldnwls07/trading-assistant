import asyncio
import logging
from src.domains.trading_signals.infrastructure.rl_agent_adapter import RLAgentAdapter
from src.domains.trading_signals.services.signal_service import SignalService

logging.basicConfig(level=logging.INFO)

async def test_rl_signal():
    print("🚀 Testing RL Trading Agent Integration...")
    
    # 1. Setup
    adapter = RLAgentAdapter()
    service = SignalService(adapter)
    
    ticker = "AAPL" # Apple Inc.
    
    try:
        # 2. Generate Signal (This will trigger model download on first run)
        print(f"📡 Generating signal for {ticker}...")
        signal = await service.generate_rl_signal(ticker)
        
        # 3. Output
        print("\n✅ RL Signal Generated Successfully!")
        print(f"Ticker: {signal.ticker}")
        print(f"Action: {signal.action}")
        print(f"Position Size: {signal.position_size * 100:.1f}%")
        print(f"Metadata: {signal.metadata}")
        
    except Exception as e:
        print(f"❌ Error during RL signal test: {e}")

if __name__ == "__main__":
    asyncio.run(test_rl_signal())
