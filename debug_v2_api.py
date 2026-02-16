import asyncio
import os
import json
from datetime import datetime
from src.agents.event_calendar import EventCalendar
from src.data.storage import get_storage

async def debug_v2():
    calendar = EventCalendar()
    storage = get_storage()
    await storage.initialize()
    
    # Test for Feb 16, 2026
    start = "2026-02-16"
    end = "2026-02-18"
    
    print(f"Testing v2 for {start} to {end}...")
    res = await calendar.get_calendar_v2(start_date=start, end_date=end, storage=storage, lang="ko")
    
    events = res.get('events', [])
    print(f"Total events found: {len(events)}")
    
    for e in events:
        print(f"[{e['date']} {e['time']}] {e['country']} - {e['title']} (Type: {e['type']})")

if __name__ == "__main__":
    asyncio.run(debug_v2())
