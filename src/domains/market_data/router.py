from fastapi import APIRouter, HTTPException
import logging
import pandas as pd
from typing import Optional
from datetime import datetime

from src.api.utils import validate_ticker, get_final_ticker, safe_serialize
from src.api.dependencies import collector
from src.data.loader import krx_loader

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/history/{ticker}")
async def get_history(ticker: str, interval: str = "1d"):
    """차트 시각화를 위한 OHLCV 데이터 반환"""
    try:
        validate_ticker(ticker)
        final_ticker = get_final_ticker(ticker)
        
        period_map = {
            "1m": "1d", "5m": "5d", "15m": "7d", "30m": "30d", "60m": "60d",
            "1h": "60d", "4h": "120d", "1d": "2y", "1wk": "max", "1mo": "max", "1y": "max" 
        }
        period = period_map.get(interval, "1y")
        actual_interval = "1h" if interval == "4h" else ("1mo" if interval == "1y" else interval)
        
        if final_ticker.endswith('.ks'): final_ticker = final_ticker[:-3] + '.KS'
        if final_ticker.endswith('.kq'): final_ticker = final_ticker[:-3] + '.KQ'

        df = await collector.get_ohlcv(final_ticker, period=period, interval=actual_interval)
        
        if (df is None or df.empty) and interval in ["1m", "5m", "15m", "30m", "60m"]:
            logger.info(f"Interval {interval} failed for {ticker}, falling back to daily.")
            df = await collector.get_ohlcv(final_ticker, period="1y", interval="1d")
            interval = "1d"

        if df is None or df.empty:
            return {"ticker": final_ticker, "data": []}
            
        if interval == "1y":
            logger.info(f"Applying 1Y resampling for {ticker}...")
            try:
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df = df.dropna(subset=['Date']) 
                    df.set_index('Date', inplace=True)
                
                if not isinstance(df.index, pd.DatetimeIndex):
                    try:
                        df.index = pd.to_datetime(df.index, errors='coerce')
                        df = df[df.index.notnull()] 
                    except:
                        pass
                
                if isinstance(df.index, pd.DatetimeIndex) and not df.empty:
                    agg_dict = {
                        'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
                    }
                    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
                    
                    resampled_df = None
                    for rule in ['YE', 'Y', 'A']:
                        try:
                            resampled_df = df.resample(rule, kind='timestamp').agg(agg_dict).dropna()
                            if not resampled_df.empty: break
                        except:
                            continue
                    
                    if resampled_df is not None and not resampled_df.empty:
                        df = resampled_df
            except Exception as e:
                logger.error(f"Resampling error completely failed: {e}")

        # 기술적 지표 계산
        from src.utils.advanced_indicators import AdvancedIndicators
        
        calc_df = df.copy()
        if 'Date' in calc_df.columns:
            calc_df.set_index(pd.to_datetime(calc_df['Date']), inplace=True)
        
        calc_df = AdvancedIndicators.calculate_all(calc_df)

        if not isinstance(calc_df.index, pd.DatetimeIndex):
            calc_df.index = pd.to_datetime(calc_df.index)
        
        calc_df = calc_df[calc_df.index.notnull()]
        calc_df.sort_index(inplace=True)
        
        history = []
        for idx, row in calc_df.iterrows():
            try:
                time_val = idx.strftime('%Y-%m-%d %H:%M:%S' if actual_interval != '1d' else '%Y-%m-%d')
            except:
                time_val = str(idx)

            data_point = {
                "time": time_val,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]),
            }
            
            all_indicators = [
                'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_60', 'sma_100', 'sma_120', 'sma_200',
                'ema_9', 'ema_12', 'ema_20', 'ema_26', 'ema_50', 'ema_200',
                'bb_upper', 'bb_middle', 'bb_lower', 'bb_width',
                'kc_upper', 'kc_middle', 'kc_lower', 'dc_upper', 'dc_middle', 'dc_lower',
                'ichimoku_tenkan', 'ichimoku_kijun', 'ichimoku_senkou_a', 'ichimoku_senkou_b',
                'rsi', 'rsi_9', 'rsi_25', 'MACD', 'Signal', 'Hist',
                'stoch_k', 'stoch_d', 'cci', 'williams_r',
                'adx', 'plus_di', 'minus_di', 'obv', 'mfi', 'vwap', 'cmf',
                'roc', 'momentum', 'aroon_up', 'aroon_down', 'aroon_osc', 'tsi', 'uo', 'atr'
            ]
            
            for indicator in all_indicators:
                if indicator in row.index:
                    val = row[indicator]
                    key = indicator.lower() if indicator in ['MACD', 'Signal', 'Hist'] else indicator
                    if indicator == 'Signal': key = 'macd_signal'
                    elif indicator == 'Hist': key = 'macd_hist'
                    elif indicator == 'MACD': key = 'macd'
                    data_point[key] = float(val) if pd.notna(val) else None
            
            history.append(data_point)
            
        return safe_serialize({"ticker": final_ticker, "interval": interval, "data": history})
    except Exception as e:
        logger.error(f"History error: {e}")
        raise e

@router.get("/search")
async def search_ticker(query: str):
    """티커 검색 (Autocomplete용) - KRX 우선 + Yfinance 보조"""
    try:
        import yfinance as yf
        if not query or len(query) < 1 or len(query) > 50:
            return {"query": query, "candidates": []}
            
        candidates = []
        is_korean_query = any(ord('가') <= ord(char) <= ord('힣') for char in query)
        is_krx_code = query.isdigit() and len(query) >= 3
        
        if is_korean_query or is_krx_code or (krx_loader and krx_loader.df is not None):
             if krx_loader and krx_loader.df is not None:
                krx_results = krx_loader.search(query, limit=10)
                candidates.extend(krx_results)
            
        if len(candidates) < 3 and not is_korean_query:
            try:
                search = yf.Search(query, max_results=8)
                yf_results = search.quotes
                
                for res in yf_results:
                    sym = res.get("symbol", "")
                    if any(c['symbol'] == sym for c in candidates):
                        continue
                        
                    is_kr = sym.endswith((".KS", ".KQ"))
                    candidates.append({
                        "symbol": sym,
                        "name": res.get("shortname") or res.get("longname") or sym,
                        "exchange": res.get("exchange"),
                        "is_korean": is_kr
                    })
            except Exception as e:
                logger.warning(f"yfinance search error: {e}")
        
        candidates.sort(key=lambda x: x['is_korean'], reverse=True)
        return {"query": query, "candidates": candidates[:15]}
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"query": query, "candidates": []}

@router.get("/api/exchange-rate")
async def get_exchange_rate():
    """실시간 USD/KRW 환율 조회"""
    try:
        df = await collector.get_ohlcv("USDKRW=X", period="1d", interval="1m")
        if df is not None and not df.empty:
            rate = float(df['Close'].iloc[-1])
            return {"rate": rate, "ticker": "USDKRW=X", "timestamp": datetime.now().isoformat()}
        return {"rate": 1350.0, "note": "Fallback rate"}
    except Exception as e:
        logger.error(f"Exchange rate error: {e}")
        return {"rate": 1350.0}
