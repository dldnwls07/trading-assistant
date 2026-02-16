import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
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

from src.utils.notifications import get_notifier

# ... (기존 변수들)

async def main_loop():
    logger.info("Async Alert Worker Started...")
    notifier = get_notifier()
    
    # 마지막 지표 브리핑 날짜
    last_briefing_date = None
    last_weekly_date = None
    
    # 알림 중복 방지를 위한 추적 (최근 지표 위주)
    last_notified_event_ids = set()
    
    while True:
        await check_alerts()
        
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # [1] 매일 오전 9시 정각 데일리 브리핑
        if now.hour == 9 and now.minute == 0 and last_briefing_date != today:
            try:
                cal_data = await calendar.get_calendar_v2(start_date=today, end_date=today, storage=storage)
                events = cal_data.get('events', [])
                
                if events:
                    fields = []
                    for e in events[:20]: # 너무 많으면 자름
                        imp_icon = "🔴" if e['importance'] == 'critical' else "🟠" if e['importance'] == 'high' else "🟡"
                        fields.append({
                            "name": f"{imp_icon} {e['time']} [{e['country']}]",
                            "value": e['title'],
                            "inline": False
                        })
                    
                    await notifier.send_message(
                        content=f"🌞 **{today}** 시장이 주목하는 주요 일정들입니다.",
                        title="📢 오늘의 시장 체크포인트",
                        color=3447003, # Blue
                        fields=fields,
                        thumbnail_url="https://cdn-icons-png.flaticon.com/512/2693/2693507.png"
                    )
                last_briefing_date = today
            except Exception as e:
                logger.error(f"Daily briefing error: {e}")

        # [2] 매주 월요일 오전 9시 주간 브리핑
        if now.weekday() == 0 and now.hour == 9 and now.minute == 0 and last_weekly_date != today:
            next_week = (now + timedelta(days=7)).strftime("%Y-%m-%d")
            try:
                cal_data = await calendar.get_calendar_v2(start_date=today, end_date=next_week, storage=storage)
                events = [e for e in cal_data.get('events', []) if e['importance'] in ['critical', 'high']]
                
                if events:
                    fields = []
                    curr_d = ""
                    for e in events[:15]:
                        if curr_d != e['date']:
                            curr_d = e['date']
                            fields.append({"name": f"📅 {curr_d}", "value": "---", "inline": False})
                        fields.append({"name": f"`{e['time']}` {e['country']}", "value": e['title'], "inline": True})
                    
                    await notifier.send_message(
                        content="🗓️ 이번 주 시장을 움직일 핵심 마켓 일정 프리뷰입니다.",
                        title="📊 위클리 마켓 인텔리전스",
                        color=15844367, # Gold
                        fields=fields
                    )
            except Exception as e:
                logger.error(f"Weekly briefing error: {e}")
            last_weekly_date = today

        # [3] 매월 1일 오전 9시 월간 전망 브리핑
        if now.day == 1 and now.hour == 9 and now.minute == 0 and last_briefing_date != (today + "_month"):
            try:
                outlook = calendar.get_monthly_outlook(today)
                fields = [
                    {"name": "📌 핵심 테마", "value": "\n".join([f"• {t}" for t in outlook['key_themes']]), "inline": False},
                    {"name": "🎯 대응 전략", "value": "\n".join([f"• {s}" for s in outlook['strategy']]), "inline": False}
                ]
                if outlook['critical_dates']:
                    fields.append({"name": "⚠️ 주의 날짜", "value": "\n".join([f"• {d['date']}: {d['event']}" for d in outlook['critical_dates']]), "inline": False})
                
                await notifier.send_message(
                    content=outlook['summary'],
                    title=f"🌟 {outlook['title']}",
                    color=10181046, # Purple
                    fields=fields,
                    thumbnail_url="https://cdn-icons-png.flaticon.com/512/3652/3652191.png"
                )
                last_briefing_date = today + "_month"
            except Exception as e:
                logger.error(f"Monthly outlook error: {e}")

        # [4] 실시간 지표 결과 모니터링 (매 1분 체크로 변경하여 신속성 확보)
        try:
            # 최근 2시간 이내의 지표 중 결과가 나온 것 확인
            start_check = (now - timedelta(hours=2)).strftime("%Y-%m-%d")
            cal_data = await calendar.get_calendar_v2(start_date=start_check, end_date=today, storage=storage)
            current_events = cal_data.get('events', [])
            
            for e in current_events:
                # 결과값이 있고 아직 알림 전인 경우
                if e.get('actual') and e['actual'] != '-' and e['id'] not in last_notified_event_ids:
                    # AI 사후 분석 리포트 생성
                    ai_report = await calendar.generate_post_event_report(e)
                    
                    fields = [
                        {"name": "이전값", "value": e.get('previous', '-'), "inline": True},
                        {"name": "예상치", "value": e.get('forecast', '-'), "inline": True},
                        {"name": "실제치", "value": f"**{e['actual']}**", "inline": True},
                        {"name": "💡 AI 마켓 인사이트", "value": ai_report, "inline": False}
                    ]
                    
                    # 중요도에 따른 색상 설정
                    color = 15158332 if e['importance'] == 'critical' else 15105570 if e['importance'] == 'high' else 3066993
                    
                    await notifier.send_message(
                        content=f"⚡ **{e['country']}** 지표 발표 속보입니다.",
                        title=f"🚨 경제 지표 속보: {e['title']}",
                        color=color,
                        fields=fields,
                        thumbnail_url="https://cdn-icons-png.flaticon.com/512/1042/1042680.png"
                    )
                    last_notified_event_ids.add(e['id'])
                    
                    # 너무 쌓이지 않게 관리
                    if len(last_notified_event_ids) > 100:
                        last_notified_event_ids = set(list(last_notified_event_ids)[-50:])
        except Exception as e:
            logger.error(f"Result monitoring error: {e}")
            
        await asyncio.sleep(60) # 1분 대기

if __name__ == "__main__":
    asyncio.run(main_loop())
