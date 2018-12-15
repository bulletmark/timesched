## TIMESCHED

The `timesched` Python module provides a simple time event scheduler. It
is implemented upon the standard Python
[`sched`](https://docs.python.org/3/library/sched.html) module and is
used in a similar way, but provides a nicer and more modern and
convenient programming interface. It requires only
Python 3.4 or later, and the standard library. The latest version of
this document and code is available at https://github.com/bulletmark/timesched.

```python
class timesched.Scheduler(timefunc=time.time, delayfunc=time.sleep)
```

Refer to the class description for Python
[sched.scheduler](https://docs.python.org/3/library/sched.html#sched.scheduler)
which is used in the [internal
implementation](#differences-to-sched-module) of this class.

_Scheduler_ instances have the following methods.

#### Create one-shot timer

```python
oneshot(time, priority, func, *args, **kwargs)
```
- _time_: expiry time relative to now, or absolute time. Type can be one of:
   - `int` at given relative seconds after now,
   - `datetime.timedelta()` at given relative `timedelta()` after now,
   - `datetime.time()` at given `time()` after now,
   - `datetime.datetime()` at given absolute `datetime()`,
   - `datetime.date()` at given absolute `date()`,
- _priority_: int value, lower value is higher priority. Refer
  [description](https://docs.python.org/3/library/sched.html#sched.scheduler.enterabs).
- _func_ and _args_ and _kwargs_: user function and arguments to call
  when timer is invoked.

Returns a _timer_ ID which can be used to cancel the timer using
[`cancel(timer)`](#cancel-timer).

#### Create repeating timer

```python
repeat(period, priority, func, *args, **kwargs)
```
- _period_: period for timer. Type can be one of:
   - `int` at each given seconds after now,
   - `datetime.timedelta()` at each given `timedelta()` after now,
   - `datetime.time()` at given `time()` each day after now. E.g. at
     10:30 every day for simple daily "cron-like" functionality.
- _priority_: int value, lower value is higher priority. Refer
  [description](https://docs.python.org/3/library/sched.html#sched.scheduler.enterabs).
- _func_ and _args_ and _kwargs_: user function and arguments to call
  when timer is invoked.

Returns a _timer_ ID which can be used to cancel the timer using
[`cancel(timer)`](#cancel-timer).

Note that for _int_ and _timedelta()_ periods, the specified period is
the delay between the end of the callback function and when it is called
again so the actual period will slowly "creep" by the run time of the
callback. Many applications are not concerned about this distinction but if
necessary you can instead invoke a _oneshot()_ absolute timer between
each call.

#### Return count of active timers

```python
count()
```

Returns the count of timers currently active. A timer is considered
active while it is pending and until it's callback function has
completed, unless it is explicitly cancelled.

#### Cancel timer

```python
cancel(timer)
```

Remove the timer with `timer` ID. If the timer is not currently active,
this method will raise a ValueError.

#### Run scheduler

```python
run(blocking=True)
```

Invokes the base `scheduler.run()`. Refer full
description at [Python sched
module](https://docs.python.org/3/library/sched.html#sched.scheduler.run).

## EXAMPLES

```python
#!/usr/bin/python3
from datetime import datetime, timedelta, date, time
import timesched

# Create a scheduler
s = timesched.Scheduler()

def callback(typ, arg):
    print('{} {} {}, active={}'.format(str(datetime.now())[:19], typ,
        arg, s.count()))

now = datetime.now()
callback('started', 'now')

# Set one shot timer to run 10 secs from now, passing int value
arg = 10
s.oneshot(arg, 0, callback, 'oneshot', arg)

# Set one shot timer to run 1 min from now, passing timedelta() value
arg = timedelta(minutes=1)
s.oneshot(arg, 0, callback, 'oneshot', arg)

# Set one shot timer to run at absolute time, passing datetime() value
arg = now + timedelta(minutes=1)
s.oneshot(arg, 0, callback, 'oneshot', arg)

# Set one shot timer to run at absolute time today, passing time() value
arg = (now + timedelta(minutes=1)).time()
s.oneshot(arg, 0, callback, 'oneshot', arg)

# Set repeat timer to run every 10 secs, passing int value
arg = 10
s.repeat(arg, 0, callback, 'repeat', arg)

# Set repeat timer to run every 1 min, passing timedelta() value
arg = timedelta(minutes=1)
s.repeat(arg, 0, callback, 'repeat', arg)

# Set repeat timer to run every day at given time, passing time() value
arg = (now + timedelta(minutes=1)).time()
s.repeat(arg, 0, callback, 'repeat', arg)

# Run scheduler, will block until no timers left running
s.run()
```

## DIFFERENCES TO STANDARD SCHED MODULE

The `timesched` module is internally implemented using the standard
Python [`sched`](https://docs.python.org/3/library/sched.html) module
but differs in the following ways. Note that the `sched` implementation,
methods, and attributes are not directly exposed in the public interface.

- Provides `oneshot()` and `repeat()` methods to conveniently accept
  standard
  [`datetime.datetime()`](https://docs.python.org/3/library/datetime.html#datetime-objects),
  [`datetime.date()`](https://docs.python.org/3/library/datetime.html#date-objects),
  [`datetime.time()`](https://docs.python.org/3/library/datetime.html#time-objects),
  [`datetime.timedelta()`](https://docs.python.org/3/library/datetime.html#timedelta-objects),
  and integer time arguments, based automatically on the type of the
  passed time argument.
- Provides a convenient way to schedule a timer at a given time each
  day to give simple daily "cron-like" functionality, e.g.
  `s.repeat(datetime.time(hour=10, minute=30), f)` to periodically
  activate a timer at 10:30 every day.
- The `repeat()` method sets itself up to be automatically invoked again
  at the next repeat interval, unlike `sched` which only provides a
  `oneshot()` equivalent method [`enter()` or `enterabs()`] so the user
  does not need to explicitly set up the next timer.
- Consistent with modern Python, allows user to plainly specify `*args`
  and `**kwargs` directly in timer setup call rather than in a tuple as
  legacy `sched` requires.
- Does not provide the
  [`enter()`](https://docs.python.org/3/library/sched.html#sched.scheduler.enter)
  or
  [`enterabs()`](https://docs.python.org/3/library/sched.html#sched.scheduler.enterabs)
  methods. Use the superior `oneshot()` or `repeat()` methods instead.
- Provides a more specific `count()` method instead of
  [`empty()`](https://docs.python.org/3/library/sched.html#sched.scheduler.empty).
- Does not provide the
  [`queue`](https://docs.python.org/3/library/sched.html#sched.scheduler.queue)
  attribute.
- Uses `time.time` instead of `time.monotonic` as the default `timefunc`
  for the internal
  [scheduler](https://docs.python.org/3/library/sched.html#sched.scheduler).
  This is to be compatible with
  [`datetime.datetime.timestamp()`](https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp) which is used internally.

## INSTALLATION

`timesched` is [available on PyPI](https://pypi.org/project/timesched/)
so install the usual way, e.g:

```bash
pip install timesched
```

Or explicitly from [github](https://github.com/bulletmark/timesched):

```bash
git clone https://github.com/bulletmark/timesched.git
cd timesched
sudo make install
```

<!-- vim: se ai syn=markdown: -->
