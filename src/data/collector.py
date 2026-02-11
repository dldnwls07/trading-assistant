import yfinance as yf
import pandas as pd
import logging
import time as time_module # 변수 이름 충돌 방지
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from .storage import DataStorage

# Setup logger
logger = logging.getLogger(__name__)

class MarketDataCollector:
    """
    Collects market data using yfinance.
    Adheres to the "Advisory Only" principle by providing data for analysis, not execution.
    """
    
    def __init__(self, data_dir: str = "./data", use_db: bool = True):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = DataStorage() if use_db else None
        
    def get_smart_data(self, ticker: str) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Smart Analysis를 위한 멀티 타임프레임 데이터(일봉 + 1시간봉)를 한 번에 수집
        """
        results = {
            "daily": self.get_ohlcv(ticker, period="1y", interval="1d"),
            "hourly": self.get_ohlcv(ticker, period="60d", interval="60m")
        }
        return results

    def get_realtime_data(self, ticker: str) -> Dict[str, Any]:
        """
        실시간 시세 데이터 조회 (Naver/Yahoo)
        한국 주식: Naver Polling API
        미국 주식: yfinance
        """
        clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
        is_korean = clean_ticker.isdigit() and len(clean_ticker) == 6
        
        realtime_data = {
            "current_price": None,
            "change": 0,
            "change_rate": 0,
            "volume": 0,
            "market_status": "CLOSE",
            "timestamp": datetime.now().isoformat()
        }

        if is_korean:
            try:
                # Naver Polling API
                url = f"https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{clean_ticker}"
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(url, headers=headers, timeout=5)
                
                if res.status_code == 200:
                    data = res.json()
                    item = data['result']['areas'][0]['datas'][0]
                    
                    realtime_data.update({
                        "current_price": float(item.get('nv', 0)), # 현재가
                        "change": float(item.get('cv', 0)),      # 전일비
                        "change_rate": float(item.get('cr', 0)), # 등락률
                        "volume": int(item.get('aq', 0)),        # 거래량
                        "market_status": item.get('ms', 'CLOSE') # 장상태
                    })
                    return realtime_data
            except Exception as e:
                logger.error(f"Naver realtime fetch error: {e}")
        
        # Fallback / Global stocks (Yahoo)
        try:
            stock = yf.Ticker(ticker)
            # Try fast_info first (newer yfinance)
            if hasattr(stock, 'fast_info'):
                info = stock.fast_info
                realtime_data.update({
                    "current_price": info.last_price,
                    "previous_close": info.previous_close,
                    "volume": info.last_volume
                })
                # Calculate change manually if needed
                if info.previous_close:
                    change = info.last_price - info.previous_close
                    rate = (change / info.previous_close) * 100
                    realtime_data['change'] = change
                    realtime_data['change_rate'] = rate
            else:
                # Legacy info
                info = stock.info
                realtime_data.update({
                    "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
                    "change": info.get('regularMarketChange'),
                    "change_rate": info.get('regularMarketChangePercent'),
                    "volume": info.get('regularMarketVolume')
                })
        except Exception as e:
            logger.error(f"Yahoo realtime fetch error: {e}")
            
        return realtime_data

    def get_ohlcv(self, ticker: str, period: str = "1y", interval: str = "1d", retries: int = 3) -> Optional[pd.DataFrame]:
        """
        OHLCV 데이터를 수집하며, 실패 시 재시도 로직을 포함함.
        한국 주식은 FinanceDataReader(네이버), 미국 주식은 yfinance 사용.
        """
        import FinanceDataReader as fdr
        
        # 한국 종목 판별 (6자리 숫자)
        clean_ticker = ticker.replace('.KS', '').replace('.KQ', '')
        is_korean = clean_ticker.isdigit() and len(clean_ticker) == 6
        
        for attempt in range(retries):
            try:
                logger.info(f"Fetching {interval} data for {ticker} (Attempt {attempt+1}/{retries})...")
                
                if is_korean and interval in ['1d', '1wk', '1mo']:
                    # [한국 주식] FinanceDataReader 사용 (일봉 이상만 지원)
                    # 기간 설정 (period -> start date 변환)
                    end_date = datetime.now()
                    if period == '1y': start_date = end_date - timedelta(days=365)
                    elif period == '60d': start_date = end_date - timedelta(days=60)
                    else: start_date = end_date - timedelta(days=365) # 기본 1년
                    
                    df = fdr.DataReader(clean_ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                    
                else:
                    # [미국 주식] 또는 [분봉 데이터]는 yfinance 사용
                    stock = yf.Ticker(ticker)
                    df = stock.history(period=period, interval=interval)
                
                # [방어코드] 반환값 검증 (빈 데이터 시 재시도)
                if df is None or df.empty:
                    # 한국 주식 분봉 요청 실패 시 -> 일봉 데이터라도 반환 시도 (User Experience)
                    if is_korean and interval not in ['1d', '1wk', '1mo'] and attempt == retries - 1:
                        logger.warning(f"Intraday data failed for {ticker}, falling back to daily.")
                        return self.get_ohlcv(ticker, period="1y", interval="1d", retries=1)
                        
                    if attempt < retries - 1:
                        time_module.sleep(1)
                        continue
                    logger.warning(f"No data found for {ticker}")
                    return None
                    
                # Clean data & Standardize Columns
                if is_korean and interval in ['1d', '1wk', '1mo']:
                    # fdr은 인덱스가 Date이므로 reset
                    df.reset_index(inplace=True)
                    # 컬럼명 통일 (Change 등을 제외하고 필수 컬럼만)
                    pass 
                else:
                    # yfinance
                    df.index.name = 'Date'
                    df.reset_index(inplace=True)
                
                # 날짜 타입 변환 및 포맷팅
                if 'Date' in df.columns:
                    try:
                        df['Date'] = pd.to_datetime(df['Date'])
                        
                        # [실시간 데이터 패치] - 오늘 날짜 데이터가 없으면 실시간 가격 추가
                        if is_korean and interval == '1d':
                            last_date = df['Date'].iloc[-1].date()
                            today = datetime.now().date()
                            
                            # 마지막 데이터가 오늘이 아니면 실시간 조회 시도... (단, 장중이거나 장마감 직후)
                            if last_date < today or (datetime.now().hour >= 9 and datetime.now().hour < 16):
                                # 첫 시도에만 패치
                                if attempt == 0:
                                    rt = self.get_realtime_data(ticker)
                                    if rt and rt.get('current_price'):
                                        # 이미 오늘 날짜가 있으면 업데이트, 없으면 추가
                                        # 간단하게: 오늘 날짜가 있으면 drop하고 새로 추가?
                                        # 아니면 그냥 마지막 row 확인.
                                        
                                        # 여기선 간단히: 오늘 날짜가 마지막 row 날짜와 같으면 pass (이미 있을 수 있음)
                                        # 다르다면 append
                                        if last_date != today:
                                            new_row = pd.DataFrame([{
                                                'Date': pd.Timestamp(today),
                                                'Open': rt['current_price'], # 시가 정보 부족 시 현재가 대체
                                                'High': rt['current_price'],
                                                'Low': rt['current_price'],
                                                'Close': rt['current_price'],
                                                'Volume': rt['volume'],
                                                'Change': rt['change_rate'] / 100 if rt.get('change_rate') else 0
                                            }])
                                            if not new_row.empty:
                                                df = pd.concat([df, new_row], ignore_index=True)

                        if interval in ["1d", "1wk", "1mo"]:
                            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                        else:
                            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')
                    except Exception as e:
                        logger.warning(f"Date formatting/patching error: {e}")
                
                # DB 저장
                if self.db:
                    try:
                        self.db.save_price_history(ticker, df)
                    except Exception as e:
                        logger.error(f"DB save error for {ticker}: {e}")
                
                # [패치] FastAPI JSON 직렬화 오류 방지 (numpy.int64 -> int/float)
                if not df.empty:
                    # 인덱스가 Date인 경우 리셋 (FinanceDataReader 대응)
                    if isinstance(df.index, pd.DatetimeIndex):
                         df.reset_index(inplace=True)
                         if 'Date' not in df.columns: # 인덱스 이름이 없을 경우
                             df.rename(columns={'index': 'Date'}, inplace=True)

                    df = df.astype(object) 
                    for col in df.columns:
                        if col == 'Date': continue
                        # 강제로 숫자로 변환 (실패 시 NaN)
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                            
                return df
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt+1}: {e}")
                if attempt < retries - 1:
                    time_module.sleep(1)
                else:
                    return None
        return None
