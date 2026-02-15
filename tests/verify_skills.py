import asyncio
import logging
from typing import Protocol, List, Optional, runtime_checkable
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# ==========================================
# 🧪 Skill Verification Script
# This script verifies that the core principles of our new skills
# (Python Expert, Quant Trader, Risk Manager) can be implemented correctly.
# ==========================================

# Setup Logging (Python Expert Skill)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SkillVerifier")

# --- 1. Python Expert Skill: Type Safety & Pydantic v2 ---

class MarketData(BaseModel):
    ticker: str
    price: float
    timestamp: datetime
    
    model_config = ConfigDict(frozen=True) # Immutable

# --- 2. Quant Trader Skill: Strategy Interface ---

@runtime_checkable
class TradingStrategy(Protocol):
    async def analyze(self, data: MarketData) -> str:
        """Returns 'BUY', 'SELL', or 'HOLD'"""
        ...

class MomentumStrategy:
    """Simple strategy implementation"""
    def __init__(self, threshold: float):
        self.threshold = threshold

    async def analyze(self, data: MarketData) -> str:
        # Mock logic: Buy if price is high (Momentum)
        if data.price > self.threshold:
            return "BUY"
        return "HOLD"

# --- 3. Risk Manager Skill: Validation ---

class RiskManager:
    def __init__(self, max_price: float):
        self.max_price = max_price

    def check_order(self, action: str, data: MarketData) -> bool:
        if action == "BUY" and data.price > self.max_price:
            logger.warning(f"🛡️ Risk Alert: Price {data.price} exceeds limit {self.max_price}")
            return False
        return True

# --- 4. Backend Engineer Skill: Async Orchestration ---

async def run_verification():
    logger.info("🚀 Starting Skill Verification...")
    
    # Setup
    strategy = MomentumStrategy(threshold=100.0)
    risk = RiskManager(max_price=150.0)
    
    # Mock Data Stream
    test_data = [
        MarketData(ticker="AAPL", price=90.0, timestamp=datetime.now()),
        MarketData(ticker="AAPL", price=110.0, timestamp=datetime.now()), # Signal: BUY
        MarketData(ticker="AAPL", price=160.0, timestamp=datetime.now()), # Signal: BUY but Risk Rejects
    ]
    
    results = []
    
    for data in test_data:
        # Async Analysis
        signal = await strategy.analyze(data)
        
        # Risk Check
        is_safe = risk.check_order(signal, data)
        
        final_action = signal if is_safe else "REJECTED"
        results.append(final_action)
        
        logger.info(f"Ticker: {data.ticker} | Price: {data.price} | Signal: {signal} -> Action: {final_action}")
        
    # Verification Assertions
    assert results == ["HOLD", "BUY", "REJECTED"]
    logger.info("✅ Verification Successful: All skills interacting correctly.")

if __name__ == "__main__":
    asyncio.run(run_verification())
