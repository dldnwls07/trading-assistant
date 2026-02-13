import pandas as pd
import numpy as np

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """RSI (상대강도지수) 계산 - analyst.py의 로직"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 테스트 데이터
data = pd.DataFrame({
    'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]
})

rsi = calculate_rsi(data)
print("상승장 RSI:")
print(rsi.tail())

data2 = pd.DataFrame({
    'Close': [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85]
})

rsi2 = calculate_rsi(data2)
print("\n하락장 RSI:")
print(rsi2.tail())

data3 = pd.DataFrame({
    'Close': [100] * 20
})
rsi3 = calculate_rsi(data3)
print("\n횡보(변화없음) RSI:")
print(rsi3.tail())
