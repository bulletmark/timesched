#!/usr/bin/python3
'Test code for testing day of week code'
from datetime import datetime, timedelta
import timesched

s = timesched.Scheduler()
now = datetime.now()
lastmin = now - timedelta(minutes=1)
nextmin = now + timedelta(minutes=1)

for t in range(7):
    for d in lastmin, nextmin:
        event = s.repeat_on_days([t], d.time(), 0, lambda: None)
        print(t, timesched.DAYS_STRING[t], str(d.time())[:8],
                str(datetime.fromtimestamp(event.eventid.time))[:10])
