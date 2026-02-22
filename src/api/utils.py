import logging
import re
import pandas as pd
import numpy as np
import yfinance as yf
from fastapi import HTTPException
from src.data.loader import krx_loader

logger = logging.getLogger(__name__)

def validate_ticker(ticker: str):
    """Sanitize and validate ticker input"""
    if not ticker or len(ticker) > 20:
        raise HTTPException(status_code=400, detail="Invalid ticker length")
    # Alphanumeric + . for KRX tickers + ^ for indices + = for currencies
    if not re.match(r"^[A-Za-z0-9\.\^\=]+$", ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    return ticker.upper()

def get_final_ticker(ticker: str) -> str:
    """종목명이나 숫자를 yfinance 티커(symbol)로 변환"""
    # 1. 이미 규격에 맞는 티커인 경우 바로 반환
    if ticker.endswith(('.KS', '.KQ')) or (ticker.isupper() and len(ticker) <= 5):
        return ticker

    # 2. 숫자로만 된 6자리 코드라면 .KS 자동 부여
    if ticker.isdigit() and len(ticker) == 6:
        return f"{ticker}.KS"

    # 3. 하드 매핑 체크
    korean_map = {
        "삼성전자": "005930.KS", "삼성전자우": "005935.KS",
        "sk하이닉스": "000660.KS", "하이닉스": "000660.KS",
        "에코프로": "086520.KQ", "에코프로비엠": "247540.KQ",
        "카카오": "035720.KS", "네이버": "035420.KS",
        "현대차": "005380.KS", "기아": "000270.KS",
        "셀트리온": "068270.KS", "포스코홀딩스": "005490.KS",
        "lg에너지솔루션": "373220.KS", "삼성sdi": "006400.KS"
    }
    if ticker in korean_map:
        return korean_map[ticker]

    # 4. 검색 API 시도
    try:
        is_korean = any(ord('가') <= ord(char) <= ord('힣') for char in ticker)
        search = yf.Search(ticker, max_results=5)
        quotes = search.quotes
        if quotes:
            if is_korean:
                for res in quotes:
                    sym = res.get('symbol', '')
                    if sym.endswith(('.KS', '.KQ')):
                        return sym
            return quotes[0].get('symbol', ticker)
    except Exception as e:
        logger.error(f"Ticker mapping error for {ticker}: {e}")
    
    return ticker

def safe_serialize(data):
    """JSON 직렬화 불가능한 객체(NaN, Timestamp, Numpy 등) 처리"""
    if isinstance(data, dict):
        return {k: safe_serialize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_serialize(v) for v in data]
    elif isinstance(data, (pd.Timestamp, pd.Period)):
        return str(data)
    elif pd.isna(data):  # NaN, NaT -> None
        return None
    elif isinstance(data, (pd.Series, pd.DataFrame)):
        return data.where(pd.notnull(data), None).to_dict() # NaN 처리 포함
    elif isinstance(data, (np.integer, np.int64)):
        return int(data)
    elif isinstance(data, (np.floating, np.float32, np.float64)):
        return float(data) if not np.isnan(data) else None
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.bool_, bool)):
        return bool(data)
    else:
        return data
