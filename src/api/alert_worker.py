import asyncio
import logging
import schedule
import time
from datetime import datetime
from src.data.storage import get_storage
from src.data.collector import MarketDataCollector
from src.utils.notifications import send_alert
from src.agents.event_calendar import EventCalendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alert-worker")

storage = get_storage()
collector = MarketDataCollector()
calendar = EventCalendar()

def check_alerts():
    """가격 및 이벤트 알림 체크 루틴"""
    logger.info(f"Checking alerts at {datetime.now()}")
    
    # 1. 활성 알림 가져오기
    active_alerts = storage.get_active_alerts()
    if not active_alerts:
        return

    for alert in active_alerts:
        try:
            # 주식 가격 알림 처리
            if alert.alert_type.startswith("price_"):
                df = collector.get_ohlcv(alert.ticker, period="1d", interval="1m")
                if df is not None and not df.empty:
                    current_price = df['Close'].iloc[-1]
                    is_above = "above" in alert.alert_type
                    
                    triggered = False
                    if is_above and current_price >= alert.target_value:
                        triggered = True
                        msg = f"**{alert.ticker}** 가격이 목표가 **{alert.target_value}**를 돌파했습니다!\n현재가: {current_price}\n메모: {alert.note}"
                    elif not is_above and current_price <= alert.target_value:
                        triggered = True
                        msg = f"**{alert.ticker}** 가격이 목표가 **{alert.target_value}** 아래로 하락했습니다!\n현재가: {current_price}\n메모: {alert.note}"
                    
                    if triggered:
                        send_alert(msg, title=f"📈 가격 도달 알림: {alert.ticker}")
                        storage.trigger_alert(alert.id)
                        logger.info(f"Alert triggered for {alert.ticker}")

        except Exception as e:
            logger.error(f"Error checking alert {alert.id}: {e}")

def check_economic_events():
    """오늘의 주요 경제 지표 알림 (매일 아침 실행)"""
    today = datetime.now().strftime("%Y-%m-%d")
    cal_data = calendar.get_calendar(start_date=today, end_date=today)
    high_impact = [e for e in cal_data['events'] if e['importance'] in ['critical', 'high']]
    
    if high_impact:
        msg = "📅 **오늘의 주요 경제 일정**\n\n"
        for e in high_impact:
            msg += f"• **{e['time']}** [{e['country']}] {e['title']} ({e['importance']})\n"
        
        send_alert(msg, title="📢 경제 캘린더 알림")

if __name__ == "__main__":
    logger.info("Alert Worker Started...")
    
    # 1분마다 가격 체크
    schedule.every(1).minutes.do(check_alerts)
    
    # 매일 오전 8시 30분에 경제 일정 브리핑
    schedule.every().day.at("08:30").do(check_economic_events)
    
    # 시작 시 즉시 한 번 체크
    check_alerts()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
