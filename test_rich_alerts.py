import asyncio
import os
from src.utils.notifications import get_notifier
from src.agents.event_calendar import EventCalendar
from dotenv import load_dotenv

load_dotenv()

async def test_discord_rich_alerts():
    print("Discord Rich Alert Test Started...")
    notifier = get_notifier()
    calendar = EventCalendar()
    
    # 1. 데일리 브리핑 테스트
    print("Testing Daily Briefing Embed...")
    test_events = [
        {"time": "22:30", "country": "US", "title": "Consumer Price Index (CPI)", "importance": "critical"},
        {"time": "22:30", "country": "US", "title": "Retail Sales", "importance": "high"},
        {"time": "23:00", "country": "US", "title": "U of Mich Sentiment", "importance": "medium"}
    ]
    
    fields = []
    for e in test_events:
        imp_icon = ":red_circle:" if e['importance'] == 'critical' else ":orange_circle:" if e['importance'] == 'high' else ":yellow_circle:"
        fields.append({
            "name": f"{imp_icon} {e['time']} [{e['country']}]",
            "value": e['title'],
            "inline": False
        })
    
    await notifier.send_message(
        content="🌞 **Test Daily Briefing**\nCheck out today's key economic indicators.",
        title="📢 [TEST] Daily Market Checkpoint",
        color=3447003,
        fields=fields,
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/2693/2693507.png"
    )
    
    # 2. AI 리포트 속보 테스트 (Actual AI Call)
    print("Testing AI Post-Event Report Embed...")
    sample_event = {
        "title": "US Producer Price Index (PPI)",
        "country": "US",
        "actual": "0.5%",
        "forecast": "0.3%",
        "previous": "0.2%",
        "importance": "high"
    }
    
    # Use ACTUAL AI generation if possible, fallback to simulation if needed
    try:
        print("Generating AI report using Gemini...")
        ai_report = await calendar.generate_post_event_report(sample_event)
        print("AI Report generated successfully.")
    except Exception as e:
        print(f"AI Generation failed: {e}")
        ai_report = "📊 **PPI Analysis (Fallback)**\n- Inflation pressure remains high.\n- **Nasdaq**: Short-term bearish\n- **Dollar**: Bullish momentum"
    
    fields = [
        {"name": "Previous", "value": sample_event['previous'], "inline": True},
        {"name": "Forecast", "value": sample_event['forecast'], "inline": True},
        {"name": "Actual", "value": f"**{sample_event['actual']}**", "inline": True},
        {"name": "💡 AI Market Insight", "value": ai_report, "inline": False}
    ]
    
    await notifier.send_message(
        content=f"⚡ **{sample_event['country']}** Indicator Flash (Test)",
        title=f"🚨 [TEST] Economic Indicator Flash: {sample_event['title']}",
        color=15105570,
        fields=fields,
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/1042/1042680.png"
    )
    
    print("Test messages sent. Please check your Discord channel.")
    # await notifier.close() # Notifier might not have close method depending on implementation, checking is safer
    if hasattr(notifier, 'close'):
        await notifier.close()

if __name__ == "__main__":
    # Windows SelectorEventLoop policy fix for some environments
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_discord_rich_alerts())
