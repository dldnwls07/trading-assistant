from src.agents.event_calendar import EventCalendar
import asyncio
from datetime import datetime

async def verify():
    cal = EventCalendar()
    # Mock storage to avoid DB errors during simple test
    data = cal.get_calendar_v2(start_date="2026-02-16", end_date="2026-02-19")
    events = data['events']
    
    print(f"Total events found: {len(events)}")
    for e in events:
        print(f"[{e['date']} {e.get('time', '??:??')}] {e['country']} - {e['title']} ({e['type']})")

if __name__ == "__main__":
    asyncio.run(verify())
