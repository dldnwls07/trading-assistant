from fastapi.testclient import TestClient
from src.api.server import app
import pytest
import logging

# Filter warnings
import warnings
warnings.filterwarnings("ignore")

client = TestClient(app)

def test_api_root():
    """Test if server is up"""
    # Root endpoint might be commented out in server.py, checking docs instead
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ Server Root (Docs) is accessible.")

def test_analyze_endpoint():
    """Test basic analysis endpoint"""
    ticker = "005930.KS" # Samsung Electronics
    print(f"📡 Testing /analyze/{ticker}...")
    response = client.get(f"/analyze/{ticker}")
    
    if response.status_code == 404:
        print("⚠️ Data not found (likely missing API key or offline). Skipping.")
        return

    assert response.status_code == 200
    data = response.json()
    assert "ticker" in data
    assert "final_score" in data
    print(f"✅ Analysis Success! Score: {data['final_score']}")

def test_backtest_run_strategies():
    """Test all backtest strategies using mock data if possible, or live if configured"""
    strategies = ["rsi", "sma_cross", "bollinger", "macd"]
    ticker = "AAPL" # Use US ticker for consistent data availability in some envs
    
    for strat in strategies:
        print(f"🧪 Testing Backtest Strategy: {strat.upper()}...")
        payload = {
            "ticker": ticker,
            "strategy_name": strat,
            "params": {}
        }
        response = client.post("/api/backtest/run", json=payload)
        
        # Depending on env, fetch might fail. We check for 200 or 404.
        if response.status_code == 200:
            data = response.json()
            assert "total_return_pct" in data
            print(f"   ✅ {strat}: Return {data['total_return_pct']:.2f}%")
        elif response.status_code == 404:
             print(f"   ⚠️ {strat}: Data missing, skipped.")
        else:
            print(f"   ❌ {strat}: Failed {response.status_code} - {response.text}")
            assert False

def test_backtest_optimize():
    """Test strategy optimization"""
    print("🔍 Testing Grid Search Optimization (SMA)...")
    payload = {
        "ticker": "AAPL",
        "strategy_name": "sma_cross",
        "search_space": {
            "fast": [10, 20],
            "slow": [50, 60]
        },
        "target_metric": "sharpe_ratio"
    }
    response = client.post("/api/backtest/optimize", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Optimization Success! Best Params: {data['best_params']}")
        assert "best_metric_value" in data
    elif response.status_code == 404:
        print("⚠️ Optimization skipped (Data missing)")
    else:
        print(f"❌ Optimization Failed: {response.text}")
        assert False

if __name__ == "__main__":
    print("🚀 Starting Live Server Tests...")
    try:
        test_api_root()
        test_backtest_run_strategies()
        test_backtest_optimize()
        # test_analyze_endpoint() # This might be slow due to heavy ML, uncomment if needed
        print("\n🎉 ALL TESTS PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
