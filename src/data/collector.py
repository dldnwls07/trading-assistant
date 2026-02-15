import asyncio
import logging
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.config import settings
from .storage import get_storage

logger = logging.getLogger(__name__)

class MarketDataCollector:
    """
    시장 데이터 수집 및 표준화 엔진
    - yfinance, FinanceDataReader, Naver Finance 통합
    - 모든 소스의 데이터를 동일한 규격(OHLCV)으로 변환
    - 데이터 분석을 위한 비상업적 참고용 데이터 제공
    """
    
    REQUIRED_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    
    def __init__(self, use_db: bool = True):
        self.db = get_storage() if use_db else None
        
    def _standardize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        [Data Factory] 모든 데이터 프레임의 컬럼명을 표준 규격으로 통일
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # 1. 인덱스 리셋 (Date 컬럼 확보)
        if not isinstance(df.index, pd.RangeIndex):
            df = df.reset_index()
            
        # 2. 대소문자 무관 컬럼 매핑
        col_map = {c.lower(): c for c in df.columns}
        rename_dict = {}
        
        target_v_map = {
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume',
            'adj close': 'Adj Close',
            'adj_close': 'Adj Close'
        }
        
        for low_name, target in target_v_map.items():
            if low_name in col_map:
                rename_dict[col_map[low_name]] = target
            elif low_name.replace(' ', '') in col_map: # 'adjclose' 처리
                rename_dict[col_map[low_name.replace(' ', '')]] = target
        
        df = df.rename(columns=rename_dict)
        
        # 3. 필수 컬럼 보완
        if 'Adj Close' not in df.columns and 'Close' in df.columns:
            df['Adj Close'] = df['Close']
            
        # 4. 타입 및 데이터 정제
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            
        for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 5. 불필요한 컬럼 제거 및 순서 정렬
        present_cols = [c for c in ['Date'] + self.REQUIRED_COLUMNS if c in df.columns]
        return df[present_cols].copy()

    async def get_ohlcv(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        표준화된 OHLCV 데이터 수집 (yfinance -> FDR Fallback)
        """
        import FinanceDataReader as fdr
        
        # 한국 주식 판별
        clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
        is_korean = clean_ticker.isdigit() and len(clean_ticker) == 6
        
        try:
            logger.info(f"🔍 Fetching {interval} data for {ticker}...")
            
            # 1. 수집 로직 실행 (Thread pool)
            df = await asyncio.to_thread(self._fetch_raw_data, ticker, is_korean, period, interval)
            
            if df is None or df.empty:
                # 한국 주식 분봉 실패 시 일봉으로 우회 시도
                if is_korean and interval not in ['1d', '1wk', '1mo']:
                    logger.warning(f"Intraday failed for {ticker}, falling back to daily.")
                    return await self.get_ohlcv(ticker, period="1y", interval="1d")
                return None
            
            # 2. 표준화 (Data Factory)
            df = self._standardize_df(df)
            
            # 3. 실시간 패치 (한국 주식 일봉)
            if is_korean and interval == '1d' and not df.empty:
                df = await self._patch_realtime_korean(ticker, df)
            
            # 4. 날짜 포맷팅 (시계열 분석 완료 후 문자열 변환)
            if not df.empty:
                if interval in ["1d", "1wk", "1mo"]:
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                else:
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
            
            # 5. DB 저장
            if self.db and not df.empty:
                await self.db.save_price_history(ticker, df)
                
            return df

        except Exception as e:
            logger.error(f"❌ Collector error for {ticker}: {e}")
            return None

    def _fetch_raw_data(self, ticker: str, is_korean: bool, period: str, interval: str) -> Optional[pd.DataFrame]:
        """로우 데이터 수집 동기 로직 (외부 라이브러리 호출)"""
        import FinanceDataReader as fdr
        
        if is_korean and interval in ['1d', '1wk', '1mo']:
            # 한국 주식 - FDR 우선
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365) if period == '1y' else end_date - timedelta(days=60)
            df = fdr.DataReader(ticker.replace('.KS', '').replace('.KQ', ''), start_date, end_date)
            return df

        # yfinance 시도
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

        # 해외 주식 FDR Fallback
        if not is_korean and interval in ['1d', '1wk', '1mo']:
            try:
                fdr_ticker = f"NASDAQ:{ticker}" if ":" not in ticker else ticker
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                return fdr.DataReader(fdr_ticker, start_date, end_date)
            except Exception:
                return None
        
        return None

    async def _patch_realtime_korean(self, ticker: str, df: pd.DataFrame) -> pd.DataFrame:
        """한국 주식 장중 데이터 실시간 패치"""
        try:
            last_date = df['Date'].iloc[-1].date()
            today = datetime.now().date()
            now = datetime.now()
            
            if last_date < today and (9 <= now.hour <= 16):
                rt = await self.get_realtime_data(ticker)
                if rt and rt.get('current_price'):
                    new_row = pd.DataFrame([{
                        'Date': pd.Timestamp(today),
                        'Open': rt['current_price'],
                        'High': rt['current_price'],
                        'Low': rt['current_price'],
                        'Close': rt['current_price'],
                        'Volume': rt['volume'],
                        'Adj Close': rt['current_price']
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
        except Exception as e:
            logger.warning(f"Realtime patch failed: {e}")
        return df

    async def get_realtime_data(self, ticker: str) -> Dict[str, Any]:
        """실시간 시세 데이터 (Naver/Yahoo)"""
        clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
        is_korean = clean_ticker.isdigit() and len(clean_ticker) == 6
        
        res_template = {
            "current_price": None, "change": 0, "change_rate": 0,
            "volume": 0, "market_status": "CLOSE", "timestamp": datetime.now().isoformat()
        }

        if is_korean:
            try:
                url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{clean_ticker}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
                if res.status_code == 200:
                    item = res.json()['result']['areas'][0]['datas'][0]
                    res_template.update({
                        "current_price": float(item.get('nv', 0)),
                        "change": float(item.get('cv', 0)),
                        "change_rate": float(item.get('cr', 0)),
                        "volume": int(item.get('aq', 0)),
                        "market_status": item.get('ms', 'CLOSE')
                    })
                    return res_template
            except: pass

        try:
            stock = yf.Ticker(ticker)
            info = await asyncio.to_thread(lambda: stock.fast_info)
            res_template.update({
                "current_price": info.last_price,
                "volume": info.last_volume,
                "change": info.last_price - info.previous_close if hasattr(info, 'previous_close') else 0
            })
        except: pass
            
        return res_template
