import asyncio
import os
from src.utils.notifications import get_notifier
from src.agents.event_calendar import EventCalendar
from dotenv import load_dotenv

load_dotenv()

async def test_discord_rich_alerts():
    print("🚀 Discord Rich Alert Test Started...")
    notifier = get_notifier()
    calendar = EventCalendar()
    
    # 1. 데일리 브리핑 테스트
    print("Testing Daily Briefing Embed...")
    test_events = [
        {"time": "22:30", "country": "US", "title": "소비자물가지수 (CPI)", "importance": "critical"},
        {"time": "22:30", "country": "US", "title": "소매판매", "importance": "high"},
        {"time": "23:00", "country": "US", "title": "미시간대 소비자심리지수", "importance": "medium"}
    ]
    
    fields = []
    for e in test_events:
        imp_icon = "🔴" if e['importance'] == 'critical' else "🟠" if e['importance'] == 'high' else "🟡"
        fields.append({
            "name": f"{imp_icon} {e['time']} [{e['country']}]",
            "value": e['title'],
            "inline": False
        })
    
    await notifier.send_message(
        content="🌞 **테스트 데일리 브리핑**\n오늘의 주요 경제 지표들을 확인하세요.",
        title="📢 [TEST] 오늘의 시장 체크포인트",
        color=3447003,
        fields=fields,
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/2693/2693507.png"
    )
    
    # 2. AI 리포트 속보 테스트
    print("Testing AI Post-Event Report Embed...")
    sample_event = {
        "title": "미국 생산자물가지수 (PPI)",
        "country": "US",
        "actual": "0.5%",
        "forecast": "0.3%",
        "previous": "0.2%",
        "importance": "high"
    }
    
    # AI 리포트 생성 시뮬레이션
    ai_report = "📊 **PPI 예상 상회 분석**\n- 물가 압력이 여전히 높음을 시사하며, 이는 연준의 금리 인하 기대감을 후퇴시킬 수 있습니다.\n- **나스닥**: 단기 조정 압력 예상\n- **달러**: 강세 전환 가능성"
    
    fields = [
        {"name": "이전값", "value": sample_event['previous'], "inline": True},
        {"name": "예상치", "value": sample_event['forecast'], "inline": True},
        {"name": "실제치", "value": f"**{sample_event['actual']}**", "inline": True},
        {"name": "💡 AI 마켓 인사이트", "value": ai_report, "inline": False}
    ]
    
    await notifier.send_message(
        content=f"⚡ **{sample_event['country']}** 지표 발표 속보 (테스트)",
        title=f"🚨 [TEST] 경제 지표 속보: {sample_event['title']}",
        color=15105570,
        fields=fields,
        thumbnail_url="https://cdn-icons-png.flaticon.com/512/1042/1042680.png"
    )
    
    print("✅ Test messages sent. Please check your Discord channel.")
    await notifier.close()

if __name__ == "__main__":
    asyncio.run(test_discord_rich_alerts())
