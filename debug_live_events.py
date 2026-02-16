from src.agents.event_calendar import EventCalendar
import json
from datetime import datetime

calendar = EventCalendar()
print(f"Checking Calendar for today: {datetime.now()}")

# Test: get_calendar for today (2026-02-16)
res = calendar.get_calendar(start_date="2026-02-16", lang="ko")
events = res['events']

print(f"\nFound {len(events)} events for the period.")
for e in events:
    if e['date'] == "2026-02-16":
        print(f"  [TODAY] {e['country']} - {e['title']} ({e['type']})")
    elif e['date'] == "2026-02-17":
         print(f"  [TOMORROW] {e['country']} - {e['title']} ({e['type']})")
