
import sys
import os
sys.path.append(os.getcwd())
from src.agents.event_calendar import EventCalendar
from datetime import datetime, timedelta

cal = EventCalendar()
# Use a wide range to ensure we catch monthly indicators
start = datetime.now()
end = start + timedelta(days=90)
res = cal.get_calendar(start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d"))

print(f"Total Events: {len(res['events'])}")
countries = set(e['country'] for e in res['events'])
types = set(e['type'] for e in res['events'])

print(f"Countries found: {countries}")
print(f"Types found: {types}")

# Sample some events
print("\nSample Global Events:")
for e in res['events']:
    if e['country'] in ['EU', 'JP', 'KR'] or e['type'] in ['Speech', 'Auction']:
        print(f"[{e['date']}] {e['country']} - {e['type']}: {e['title']}")
