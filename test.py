#!/usr/bin/python3
'Example code and small test suite.'
from datetime import datetime, timedelta
import timesched

# Create a scheduler
s = timesched.Scheduler()

def callback(typ, arg):
    print('{} {} {}, active={}'.format(str(datetime.now())[:19], typ,
        arg, s.count()))

now = datetime.now()
callback('started', 'now')

# Set one shot timer to run 10 secs from now, passing int value
secs = 10
s.oneshot(secs, 0, callback, 'oneshot', secs)

# Set one shot timer to run 1 min from now, passing timedelta() value
minute = timedelta(minutes=1)
s.oneshot(minute, 0, callback, 'oneshot', minute)

# Set one shot timer to run at absolute time, passing datetime() value
nextmin = now + minute
s.oneshot(nextmin, 0, callback, 'oneshot', nextmin)

# Set one shot timer to run at absolute time today, passing time() value
nexttime = nextmin.time()
s.oneshot(nexttime, 0, callback, 'oneshot', nexttime)

# Set repeat timer to run every 10 secs, passing int value
s.repeat(secs, 0, callback, 'repeat', secs)

# Set repeat timer to run every 1 min, passing timedelta() value
s.repeat(minute, 0, callback, 'repeat', minute)

# Set repeat timer to run every day at given time, passing time() value
s.repeat(nexttime, 0, callback, 'repeat', nexttime)

# Set repeat timer to run every weekday at given time, passing time() value
s.repeat_on_days([nextmin.weekday()], nexttime, 0, callback,
        'repeat_on_days', nexttime)
# Same this but run every day and use string for day of week
s.repeat_on_days('MTWTFSS', nexttime, 0, callback, 'repeat_on_days', nexttime)

# Create and then immediately cancel a couple of timers before they
# execute.
timer1 = s.oneshot(secs, 0, callback, 'oneshot', 'cancel')
timer2 = s.repeat(secs, 0, callback, 'repeat', 'cancel')
s.cancel(timer1)
s.cancel(timer2)

# Run scheduler, will block until no timers left running
s.run()
