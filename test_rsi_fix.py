import pandas as pd
import numpy as np

def calculate_rsi_new(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """Wilder's Smoothing을 사용한 표준 RSI 계산"""
    delta = data['Close'].diff()
    
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    loss = abs(loss)
    
    # Wilder's Smoothing (alpha = 1/window)
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
    # NaN 방지 및 0 나누기 처리
    rsi = pd.Series(np.nan, index=data.index)
    
    # 1. 둘 다 0인 경우 (변동 없음) -> 50
    no_move = (avg_gain == 0) & (avg_loss == 0)
    rsi[no_move] = 50.0
    
    # 2. loss만 0인 경우 (계속 상승) -> 100
    always_up = (avg_gain > 0) & (avg_loss == 0)
    rsi[always_up] = 100.0
    
    # 3. gain만 0인 경우 (계속 하락) -> 0
    always_down = (avg_gain == 0) & (avg_loss > 0)
    rsi[always_down] = 0.0
    
    # 4. 일반적인 경우
    normal = (avg_gain > 0) & (avg_loss > 0)
    rs = avg_gain[normal] / avg_loss[normal]
    rsi[normal] = 100.0 - (100.0 / (1.0 + rs))
    
    return rsi

# 테스트
df = pd.DataFrame({'Close': [100]*20})
print("횡보 RSI:", calculate_rsi_new(df).iloc[-1])

df2 = pd.DataFrame({'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]})
print("상승 RSI:", calculate_rsi_new(df2).iloc[-1])

df3 = pd.DataFrame({'Close': [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85]})
print("하락 RSI:", calculate_rsi_new(df3).iloc[-1])
