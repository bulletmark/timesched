## TIMESCHED
[![PyPi](https://img.shields.io/pypi/v/timesched)](https://pypi.org/project/timesched/)
[![AUR](https://img.shields.io/aur/version/python-timesched)](https://aur.archlinux.org/packages/python-timesched/)

The `timesched` Python module provides a simple time event scheduler. It
is implemented upon the standard Python
[`sched`](https://docs.python.org/3/library/sched.html) module and is
used in a similar way, but provides a nicer and more modern and
convenient programming interface. Apart from normal oneshot and repeat
timers, it can run timers at a given time of day, and for the given days
of week, providing simple cron-like functionality. It requires only
Python 3.6 or later, and the standard library. The latest version of
this document and code is available at
https://github.com/bulletmark/timesched.

```python
class timesched.Scheduler(timefunc=time.time, delayfunc=time.sleep)
```

Refer to the class description for Python
[sched.scheduler](https://docs.python.org/3/library/sched.html#sched.scheduler)
which is used in the [internal
implementation](#differences-to-standard-sched-module) of this class.

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

#### Create one-shot timer on next given day

Call this with _time_ = `datetime.time()` to invoke a `oneshot()` at the
given _time_ on the next day from the set of given _days_ of the week.

```python
oneshot_on_days(days, time, priority, func, *args, **kwargs)
```

- _days_: A list/set/sequence/range of integers 0-6 where 0 = Monday to
  6 = Sunday. e.g. [0] means only invoke timer on a Monday, [0,6] = only
  invoke on Monday and Sunday, etc. Using `days=range(7)` is same as
  calling ordinary `oneshot()`.

  Alternately, you can specify _days_ as a string "MTWTFSS" where each
  char is upper case if the day is to be set, and lower case if not.
  E.g. "MTWTFss" is the working week Mon-Fri, "mtwTfss" is Thu only,
  etc. A utility function to explicitly parse this string into a set of
  integers is available as `timesched.parse_days(string_arg)` if you
  need.

Remaining parameters and return type are same as `oneshot()`.

#### Create repeating timer on given days

Call this with _time_ = `datetime.time()` to invoke a `repeat()` at the
given _period_ on each of the given _days_ of the week.

```python
repeat_on_days(days, period, priority, func, *args, **kwargs)
```

- _days_: parameter same as `oneshot_on_days()`.

Remaining parameters and return type are same as `repeat()`.

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
'Very simple examples'
import timesched
from datetime import datetime, time

# Job function to be called for each timer
def job(jobid):
    print(f'Job {jobid} called at {datetime.now()}')

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
  and also integer time arguments, based automatically on the type of the
  passed time argument.
- The `repeat()` method sets itself up to be automatically invoked again
  at the next repeat interval, unlike `sched` which only provides a
  `oneshot()` equivalent method [i.e. `enter()` or `enterabs()`] so the user
  does not need to explicitly set up the next timer.
- Provides a convenient way to schedule a timer at a given time each
  day to give simple daily "cron-like" functionality, e.g.
  `s.repeat(datetime.time(hour=10, minute=30), f)` to periodically
  activate a timer at 10:30 every day.
- Further to the above `repeat()` which can run at a given time every
  day, you can use `repeat_on_days()` to specify a given time on a set
  of given days, e.g. `s.repeat_on_days('MTWTFss',
  datetime.time(hour=10, minute=30), f)` to run the timer at 10:30 each
  workday only (Mon to Fri). Alternately `s.repeat_on_days(range(5),
  datetime.time(hour=10, minute=30), f)`
  gives the same result.
- Consistent with modern Python, allows user to plainly specify `*args`
  and `**kwargs` directly in timer setup call rather than in a tuple as
  legacy `sched` requires.
- Does not provide the
  [`enter()`](https://docs.python.org/3/library/sched.html#sched.scheduler.enter)
  or
  [`enterabs()`](https://docs.python.org/3/library/sched.html#sched.scheduler.enterabs)
  methods. Use the superior `oneshot()`, `repeat()`,
  `oneshot_on_days()`, or `repeat_on_days()` methods instead.
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

Arch Linux users can install [timesched from the
AUR](https://aur.archlinux.org/packages/python-timesched/).

`timesched` is [available on PyPI](https://pypi.org/project/timesched/)
so install the usual way, e.g:

```bash
pip3 install timesched
```

Or explicitly from [github](https://github.com/bulletmark/timesched):

```bash
git clone https://github.com/bulletmark/timesched.git
cd timesched
sudo pip3 install .
```

<!-- vim: se ai syn=markdown: -->
