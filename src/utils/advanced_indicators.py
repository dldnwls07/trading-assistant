"""
고급 기술적 지표 계산 모듈 - 전문 트레이더용 30개 이상 지표
"""
import pandas as pd
import numpy as np

class AdvancedIndicators:
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """모든 지표 계산"""
        calc = df.copy()
        
        # === 이동평균선 (SMA) ===
        for period in [5, 10, 20, 50, 60, 100, 120, 200]:
            calc[f'sma_{period}'] = calc['Close'].rolling(window=period).mean()
        
        # === 지수이동평균 (EMA) ===
        for period in [9, 12, 20, 26, 50, 200]:
            calc[f'ema_{period}'] = calc['Close'].ewm(span=period, adjust=False).mean()
        
        # === 볼린저 밴드 ===
        sma20 = calc['Close'].rolling(20).mean()
        std20 = calc['Close'].rolling(20).std()
        calc['bb_upper'] = sma20 + (std20 * 2)
        calc['bb_middle'] = sma20
        calc['bb_lower'] = sma20 - (std20 * 2)
        calc['bb_width'] = (calc['bb_upper'] - calc['bb_lower']) / calc['bb_middle'] * 100
        
        # === 켈트너 채널 ===
        ema20 = calc['Close'].ewm(span=20, adjust=False).mean()
        atr = AdvancedIndicators._atr(calc, 20)
        calc['kc_upper'] = ema20 + (atr * 2)
        calc['kc_middle'] = ema20
        calc['kc_lower'] = ema20 - (atr * 2)
        
        # === 동코안 채널 ===
        calc['dc_upper'] = calc['High'].rolling(20).max()
        calc['dc_lower'] = calc['Low'].rolling(20).min()
        calc['dc_middle'] = (calc['dc_upper'] + calc['dc_lower']) / 2
        
        # === 일목균형표 ===
        calc['ichimoku_tenkan'] = (calc['High'].rolling(9).max() + calc['Low'].rolling(9).min()) / 2
        calc['ichimoku_kijun'] = (calc['High'].rolling(26).max() + calc['Low'].rolling(26).min()) / 2
        calc['ichimoku_senkou_a'] = ((calc['ichimoku_tenkan'] + calc['ichimoku_kijun']) / 2).shift(26)
        calc['ichimoku_senkou_b'] = ((calc['High'].rolling(52).max() + calc['Low'].rolling(52).min()) / 2).shift(26)
        
        # === RSI ===
        calc['rsi'] = AdvancedIndicators._rsi(calc, 14)
        calc['rsi_9'] = AdvancedIndicators._rsi(calc, 9)
        calc['rsi_25'] = AdvancedIndicators._rsi(calc, 25)
        
        # === MACD ===
        exp12 = calc['Close'].ewm(span=12, adjust=False).mean()
        exp26 = calc['Close'].ewm(span=26, adjust=False).mean()
        calc['MACD'] = exp12 - exp26
        calc['Signal'] = calc['MACD'].ewm(span=9, adjust=False).mean()
        calc['Hist'] = calc['MACD'] - calc['Signal']
        
        # === 스토캐스틱 ===
        low14 = calc['Low'].rolling(14).min()
        high14 = calc['High'].rolling(14).max()
        calc['stoch_k'] = 100 * ((calc['Close'] - low14) / (high14 - low14))
        calc['stoch_d'] = calc['stoch_k'].rolling(3).mean()
        
        # === CCI ===
        tp = (calc['High'] + calc['Low'] + calc['Close']) / 3
        sma_tp = tp.rolling(20).mean()
        mad = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
        calc['cci'] = (tp - sma_tp) / (0.015 * mad)
        
        # === Williams %R ===
        high14 = calc['High'].rolling(14).max()
        low14 = calc['Low'].rolling(14).min()
        calc['williams_r'] = -100 * ((high14 - calc['Close']) / (high14 - low14))
        
        # === ADX ===
        calc['atr'] = AdvancedIndicators._atr(calc, 14)
        high_diff = calc['High'].diff()
        low_diff = -calc['Low'].diff()
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        plus_di = 100 * (plus_dm.rolling(14).mean() / calc['atr'])
        minus_di = 100 * (minus_dm.rolling(14).mean() / calc['atr'])
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        calc['adx'] = dx.rolling(14).mean()
        calc['plus_di'] = plus_di
        calc['minus_di'] = minus_di
        
        # === OBV ===
        calc['obv'] = (np.sign(calc['Close'].diff()) * calc['Volume']).fillna(0).cumsum()
        
        # === MFI ===
        tp = (calc['High'] + calc['Low'] + calc['Close']) / 3
        mf = tp * calc['Volume']
        pos_mf = mf.where(tp > tp.shift(), 0).rolling(14).sum()
        neg_mf = mf.where(tp < tp.shift(), 0).rolling(14).sum()
        calc['mfi'] = 100 - (100 / (1 + pos_mf / neg_mf))
        
        # === VWAP ===
        tp = (calc['High'] + calc['Low'] + calc['Close']) / 3
        calc['vwap'] = (tp * calc['Volume']).cumsum() / calc['Volume'].cumsum()
        
        # === CMF ===
        mfm = ((calc['Close'] - calc['Low']) - (calc['High'] - calc['Close'])) / (calc['High'] - calc['Low'])
        mfv = mfm * calc['Volume']
        calc['cmf'] = mfv.rolling(20).sum() / calc['Volume'].rolling(20).sum()
        
        # === ROC ===
        calc['roc'] = ((calc['Close'] - calc['Close'].shift(12)) / calc['Close'].shift(12)) * 100
        
        # === Momentum ===
        calc['momentum'] = calc['Close'] - calc['Close'].shift(10)
        
        # === Aroon ===
        calc['aroon_up'] = calc['High'].rolling(25).apply(lambda x: x.argmax()) / 25 * 100
        calc['aroon_down'] = calc['Low'].rolling(25).apply(lambda x: x.argmin()) / 25 * 100
        calc['aroon_osc'] = calc['aroon_up'] - calc['aroon_down']
        
        # === TSI (True Strength Index) ===
        momentum = calc['Close'].diff()
        ema25_momentum = momentum.ewm(span=25, adjust=False).mean()
        ema13_ema25 = ema25_momentum.ewm(span=13, adjust=False).mean()
        ema25_abs = momentum.abs().ewm(span=25, adjust=False).mean()
        ema13_ema25_abs = ema25_abs.ewm(span=13, adjust=False).mean()
        calc['tsi'] = 100 * (ema13_ema25 / ema13_ema25_abs)
        
        # === Ultimate Oscillator ===
        calc['uo'] = AdvancedIndicators._ultimate_oscillator(calc)
        
        return calc
    
    @staticmethod
    def _rsi(df: pd.DataFrame, period: int) -> pd.Series:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def _atr(df: pd.DataFrame, period: int) -> pd.Series:
        hl = df['High'] - df['Low']
        hc = np.abs(df['High'] - df['Close'].shift())
        lc = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    
    @staticmethod
    def _ultimate_oscillator(df: pd.DataFrame) -> pd.Series:
        bp = df['Close'] - df[['Low', 'Close']].shift().min(axis=1)
        tr = df[['High', 'Close']].shift().max(axis=1) - df[['Low', 'Close']].shift().min(axis=1)
        avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
        return 100 * ((4 * avg7) + (2 * avg14) + avg28) / 7
