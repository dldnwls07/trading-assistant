import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any

from src.domains.trading_signals.infrastructure.rl_agent_adapter import RLAgentAdapter
from src.domains.trading_signals.entities.signal import TradingSignal
from src.data.collector import MarketDataCollector

class SignalService:
    """
    기술적 매매 신호를 관리하는 도메인 서비스
    """
    def __init__(self, rl_adapter: RLAgentAdapter, collector: MarketDataCollector = None):
        self.rl_adapter = rl_adapter
        self.collector = collector or MarketDataCollector(use_db=False)

    async def generate_rl_signal(self, ticker: str) -> TradingSignal:
        """
        특정 종목에 대해 RL 에이전트 기반의 매매 신호를 생성합니다.
        """
        # 1. 충분한 과거 데이터 수집 (60일 시퀀스 + 보조지표 계산용 여유분 = 약 120일)
        df = await self.collector.get_ohlcv(ticker, period="1y", interval="1d")
        if df is None or len(df) < 100:
            raise ValueError(f"Insufficient data for ticker {ticker}. Needed at least 100 days.")

        # 2. 전처리 (Adilbai dataprocessor.py 로직 재현)
        processed_df = self._calculate_technical_features(df)
        
        # 3. 모델 입력용 시퀀스 생성 (최근 60일 데이터)
        # 50 features * 60 days
        if len(processed_df) < 60:
            raise ValueError("Sequence length error: Not enough processed data.")
            
        market_sequence = processed_df.tail(60).values # (60, 50)
        
        # 4. 포트폴리오 상태 생성 (8개 가상 피처)
        # 실제 환경이 아니므로 초기 상태(Clean State)로 가정
        portfolio_state = np.array([
            1.0, # balance / initial
            0.0, # position / initial
            1.0, # net_worth / initial
            0.0, # return
            0.0, # num_trades / 100
            0.0, # costs / initial
            0.0, # max_drawdown
            0.0  # volatility
        ])
        
        # 5. 예측
        action_str, confidence = self.rl_adapter.predict(market_sequence, portfolio_state)
        
        return TradingSignal(
            ticker=ticker,
            action=action_str,
            position_size=confidence,
            generated_at=datetime.now(),
            metadata={
                "source": "RL_AGENT_PPO",
                "current_price": float(df['Close'].iloc[-1]),
                "logic": "Technical RL Analysis (SB3/PPO)"
            }
        )

    def _calculate_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adilbai 모델이 기대하는 50개 피처(20개 기본 + 30개 지연) 계산"""
        temp = df.copy().sort_values('Date')
        
        # --- 20 Base Features ---
        # Moving Averages
        temp['SMA_5'] = temp['Close'].rolling(window=5).mean()
        temp['SMA_10'] = temp['Close'].rolling(window=10).mean()
        temp['SMA_20'] = temp['Close'].rolling(window=20).mean()
        temp['SMA_50'] = temp['Close'].rolling(window=50).mean()
        
        # EMAs
        temp['EMA_12'] = temp['Close'].ewm(span=12).mean()
        temp['EMA_26'] = temp['Close'].ewm(span=26).mean()
        
        # MACD
        temp['MACD'] = temp['EMA_12'] - temp['EMA_26']
        temp['MACD_Signal'] = temp['MACD'].ewm(span=9).mean()
        
        # RSI
        delta = temp['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        temp['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        bb_mid = temp['Close'].rolling(window=20).mean()
        bb_std = temp['Close'].rolling(window=20).std()
        bb_upper = bb_mid + (bb_std * 2)
        bb_lower = bb_mid - (bb_std * 2)
        bb_width = bb_upper - bb_lower
        temp['BB_Position'] = (temp['Close'] - bb_lower) / bb_width
        temp['BB_Width'] = bb_width
        
        # Volatility
        temp['Volatility'] = temp['Close'].rolling(window=20).std()
        
        # Changes
        temp['Price_Change'] = temp['Close'].pct_change()
        temp['High_Low_Ratio'] = temp['High'] / temp['Low']
        
        # Volume Ratio
        vol_sma = temp['Volume'].rolling(window=20).mean()
        temp['Volume_Ratio'] = temp['Volume'] / vol_sma
        
        # State Features List (20)
        state_features = [
            'Open', 'High', 'Low', 'Close', 'Volume',
            'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
            'EMA_12', 'EMA_26', 'MACD', 'MACD_Signal', 'RSI',
            'BB_Position', 'BB_Width', 'Volatility',
            'Price_Change', 'High_Low_Ratio', 'Volume_Ratio'
        ]
        
        # --- 30 Lagged Features (6 cols * 5 lags) ---
        lags = [1, 2, 3, 5, 10]
        lag_cols = ['Close', 'Volume', 'Price_Change', 'RSI', 'MACD', 'Volatility']
        
        for col in lag_cols:
            for lag in lags:
                col_name = f'{col}_lag_{lag}'
                temp[col_name] = temp[col].shift(lag)
                state_features.append(col_name)
        
        # Clean and Select
        temp = temp.dropna(subset=state_features)
        return temp[state_features]
