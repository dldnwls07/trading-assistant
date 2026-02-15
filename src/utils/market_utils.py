import pytz
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

def is_market_open(ticker: str) -> bool:
    """
    특정 주식 티커의 시장 개장 여부 확인
    - 한국(.KS, .KQ): 09:00 - 15:30 (KST)
    - 미국(그 외): 09:30 - 16:00 (EST/EDT)
    """
    now_utc = datetime.now(pytz.utc)
    
    # 한국 주식 판별
    is_korean = ticker.endswith(('.KS', '.KQ'))
    
    if is_korean:
        # KST (Asia/Seoul)
        kst = pytz.timezone('Asia/Seoul')
        now_local = now_utc.astimezone(kst)
        market_start = time(9, 0)
        market_end = time(15, 30)
    else:
        # 미국 시장 (Eastern Time)
        et = pytz.timezone('US/Eastern')
        now_local = now_utc.astimezone(et)
        market_start = time(9, 30)
        market_end = time(16, 0)
    
    # 주말 체크 (토:5, 일:6)
    if now_local.weekday() >= 5:
        return False
        
    current_time = now_local.time()
    
    is_open = market_start <= current_time <= market_end
    
    # 로그 출력 (장 마감 상태일 때만 출력하여 노이즈 감소)
    if not is_open:
        logger.info(f"Market Closed for {ticker}: {now_local.strftime('%Y-%m-%d %H:%M:%S')} ({now_local.tzname()})")
        
    return is_open

def get_market_time(ticker: str) -> str:
    """티커에 해당하는 현재 시장 시간 반환"""
    now_utc = datetime.now(pytz.utc)
    is_korean = ticker.endswith(('.KS', '.KQ'))
    tz_name = 'Asia/Seoul' if is_korean else 'US/Eastern'
    tz = pytz.timezone(tz_name)
    now_local = now_utc.astimezone(tz)
    return now_local.strftime('%Y-%m-%d %H:%M:%S')
