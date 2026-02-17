import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from typing import Optional

def generate_chart_image(df: pd.DataFrame, ticker: str, interval: str = "1d") -> Optional[bytes]:
    """
    OHLCV 데이터프레임을 받아 캔들스틱 차트 이미지를 생성하고 바이트로 반환합니다.
    """
    if df is None or df.empty:
        return None

    try:
        # 데이터 전처리
        data = df.copy()
        if not isinstance(data.index, pd.DatetimeIndex):
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date'])
                data.set_index('Date', inplace=True)
            else:
                data.index = pd.to_datetime(data.index)
        
        # 최근 60개 캔들만 사용 (너무 많으면 보기 힘듦)
        data = data.tail(60)
        
        # Plot 설정
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 캔들스틱 그리기 (간단하게 구현)
        # 상승(양봉): 빨강, 하락(음봉): 파랑 (한국 스타일)
        up = data[data.Close >= data.Open]
        down = data[data.Close < data.Open]
        
        # 꼬리
        ax.vlines(up.index, up.Low, up.High, color='red', linewidth=1)
        ax.vlines(down.index, down.Low, down.High, color='blue', linewidth=1)
        
        # 몸통 (width는 데이터 간격에 따라 조절 필요, 여기선 0.6일로 고정)
        # Matplotlib date numbering issue 방지 위해 width 조절 필요하나, 간단히 처리
        width = 0.6
        if interval in ['1m', '5m', '15m', '30m', '1h']:
             width = 0.02 # 분/시간 단위는 width 작게
        
        # bar plotting with dates
        # Note: matplotlib treats dates as floats. 
        # For simplicity in this agent environment, we use simple styling.
        
        # 상승봉
        ax.bar(up.index, up.Close - up.Open, bottom=up.Open, color='red', width=width)
        # 하락봉
        ax.bar(down.index, down.Close - down.Open, bottom=down.Open, color='blue', width=width)
        
        # 이동평균선 추가
        if 'Close' in data.columns:
            ax.plot(data.index, data['Close'].rolling(window=20).mean(), label='MA20', color='orange', linewidth=1.5)
            ax.plot(data.index, data['Close'].rolling(window=60).mean(), label='MA60', color='green', linewidth=1.5)

        ax.set_title(f"{ticker} ({interval}) Chart Analysis")
        ax.set_ylabel("Price")
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 날짜 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xticks(rotation=45)
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        return buf.getvalue()
        
    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None
