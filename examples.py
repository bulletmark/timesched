#!/usr/bin/python3
'Very simple examples'
import timesched
from datetime import datetime, time

# Job function to be called for each timer
def job(jobid):
    print('Job {} called at {}'.format(jobid, datetime.now()))

# Create a scheduler
s = timesched.Scheduler()

# Execute job() once in 5 secs time
s.oneshot(5, 0, job, 1)

# Execute job() every 2 secs
s.repeat(2, 0, job, 2)

# Execute job() at 10:30am every work day (not weekends)
s.repeat_on_days('MTWTFss', time(10, 30), 0, job, 3)

# Run scheduler, will block until no timers left running
s.run()
