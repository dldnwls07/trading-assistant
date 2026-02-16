from src.agents.event_calendar import EventCalendar
import json
from datetime import datetime

calendar = EventCalendar()
print(f"Current Time: {datetime.now()}")

# Test 1: Default start date
res = calendar.get_calendar(lang="ko")
events = res['events']
print(f"\nTest 1 (Default Start): Found {len(events)} events")
for e in events:
    if "대통령" in e['title'] or "ADP" in e['title']:
        print(f"  FOUND: {e['date']} - {e['title']}")
    else:
        # Debug why it's not found
        pass

# Test 2: Explicit start date 2026-02-16
res_explicit = calendar.get_calendar(start_date="2026-02-16", lang="ko")
events_explicit = res_explicit['events']
print(f"\nTest 2 (Start 2026-02-16): Found {len(events_explicit)} events")
for e in events_explicit:
    if "대통령" in e['title'] or "ADP" in e['title']:
        print(f"  FOUND: {e['date']} - {e['title']}")
