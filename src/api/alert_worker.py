import asyncio
import logging
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

async def check_alerts():
    """가격 및 이벤트 알림 체크 루틴 (비동기)"""
    logger.info(f"Checking alerts at {datetime.now()}")
    
    try:
        # DB 초기화 확인 (비동기)
        await storage.initialize()
        
        active_alerts = await storage.get_active_alerts()
        if not active_alerts:
            return

        for alert in active_alerts:
            try:
                if alert.alert_type.startswith("price_"):
                    # collector.get_ohlcv가 비동기로 전환되었으므로 await 적용
                    df = await collector.get_ohlcv(alert.ticker, period="1d", interval="1m")
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
                            await send_alert(msg, title=f"📈 가격 도달 알림: {alert.ticker}")
                            await storage.trigger_alert(alert.id)
                            logger.info(f"Alert triggered for {alert.ticker}")

            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {e}")
                
    except Exception as e:
        logger.error(f"Alert worker main loop error: {e}")

async def main_loop():
    logger.info("Async Alert Worker Started...")
    
    # 마지막 지표 브리핑 날짜
    last_briefing_date = None
    
    while True:
        await check_alerts()
        
        # 매일 오전 8시 30분 경제 일정 브리핑 (간이 구현)
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        if now.hour == 8 and now.minute >= 30 and last_briefing_date != today:
            cal_data = calendar.get_calendar(start_date=today, end_date=today)
            high_impact = [e for e in cal_data['events'] if e['importance'] in ['critical', 'high']]
            
            if high_impact:
                msg = "📅 **오늘의 주요 경제 일정**\n\n"
                for e in high_impact:
                    msg += f"• **{e['time']}** [{e['country']}] {e['title']} ({e['importance']})\n"
                await send_alert(msg, title="📢 경제 캘린더 알림")
            
            last_briefing_date = today
            
        await asyncio.sleep(60) # 1분 대기

if __name__ == "__main__":
    asyncio.run(main_loop())
