import pandas as pd
import numpy as np
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.utils.advanced_indicators import AdvancedIndicators
from src.agents.analyst import TechnicalAnalyzer, StockAnalyst
from src.utils.dictionary import get_explanation

def test_indicators():
    print("=== 1. Indicator Calculation Test (Pivot & SAR) ===")
    
    # 가상 데이터 생성 (100일)
    dates = pd.date_range(start='2024-01-01', periods=100)
    df = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 105,
        'Low': np.random.randn(100).cumsum() + 95,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.random.randint(1000, 10000, size=100)
    }, index=dates)
    
    # High가 Low보다 항상 크도록 보정
    df['High'] = df[['Open', 'Close', 'High']].max(axis=1) + 1
    df['Low'] = df[['Open', 'Close', 'Low']].min(axis=1) - 1

    # Pivot 계산
    try:
        pivots = AdvancedIndicators._pivot_points(df)
        if 'pivot_classic' in pivots.columns and not pivots['pivot_classic'].isnull().all():
            print(f"[PASS] Pivot Points Calculation Success (Classic Pivot: {pivots['pivot_classic'].iloc[-1]:.2f})")
        else:
            print("[FAIL] Pivot Points Calculation Failed (Empty Result)")
    except Exception as e:
        print(f"[FAIL] Pivot Points Error: {e}")

    # SAR 계산
    try:
        sar = AdvancedIndicators._parabolic_sar(df)
        if not sar.isnull().all():
            print(f"[PASS] Parabolic SAR Calculation Success (Last SAR: {sar.iloc[-1]:.2f})")
        else:
            print("[FAIL] Parabolic SAR Calculation Failed (Empty Result)")
    except Exception as e:
        print(f"[FAIL] Parabolic SAR Error: {e}")

def test_dictionary():
    print("\n=== 2. Dictionary Test ===")
    
    terms = ["RSI", "MACD", "Pivot Points", "Parabolic SAR", "Bollinger Bands", "AI Score"]
    all_pass = True
    
    for term in terms:
        expl = get_explanation(term, "beginner")
        if "준비 중" in expl:
            print(f"[WARN] {term} Explanation Missing: {expl}")
            all_pass = False
        else:
            pass
    
    if all_pass:
        print("[PASS] Key Indicators Explanation Check Complete")

def test_analyst():
    print("\n=== 3. Analyst Scenario Test ===")
    
    analyzer = TechnicalAnalyzer()
    
    # 가상 데이터
    dates = pd.date_range(start='2024-01-01', periods=60)
    # 초기값 설정
    closes = np.linspace(100, 110, 60)
    highs = closes + 2
    lows = closes - 2
    
    df = pd.DataFrame({
        'Open': closes,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': [1000] * 60
    }, index=dates)
    
    try:
        # 데이터프레임 형식 디버깅
        # print(f"DEBUG: df shape={df.shape}, columns={df.columns}")
        
        scenarios = analyzer.get_price_scenarios(df)
        
        if 'bearish' in scenarios and 'bullish' in scenarios:
            print("[PASS] Scenario Generation Success")
            # print(f"   [Bearish] {scenarios['bearish']}")
            # print(f"   [Bullish] {scenarios['bullish']}")
        else:
            print("[FAIL] Scenario Generation Failed (Keys missing)")
            print(f"DEBUG: scenarios keys={scenarios.keys()}")
            
    except Exception as e:
        print(f"[FAIL] Analyst Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        test_indicators()
        test_dictionary()
        test_analyst()
        print("\n[ALL TEST COMPLETE]")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Test Script Failed: {e}")
