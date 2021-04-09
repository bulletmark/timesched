'''
A simple class to provide oneshot and repeat timers.
M.Blakeney, Nov 2018.
'''
import sched
import time
import datetime
from functools import singledispatch, partial

# Optional day of week format string, default all days enabled
DAYS_STRING = 'MTWTFSS'

def parse_days(arg=None):
    'Utility function to convert "Date Of Week" string to list of ints'
    if arg is None:
        arg = DAYS_STRING

    if not isinstance(arg, str):
        return arg

    if arg.upper() != DAYS_STRING:
        raise ValueError('Day of week string must be case {} format'.format(
            DAYS_STRING))

    return [i for i, a in enumerate(arg) if a.isupper()]

# Dispatch timer based on type (first arg)
@singledispatch
def _invoke(timev, self):
    'Invoke after default int/float secs'
    return self.sched.enter(timev, self.prio, self.cb)

@_invoke.register(datetime.timedelta)
def _(timev, self):
    'Invoke after datetime.timedelta()'
    return self.sched.enter(timev.total_seconds(), self.prio, self.cb)

@_invoke.register(datetime.datetime)
def _(timev, self):
    'Invoke at datetime.datetime()'
    if not self.oneshot:
        raise TypeError('Can not repeat a datetime.datetime()')

    return self.sched.enterabs(timev.timestamp(), self.prio, self.cb)

@_invoke.register(datetime.date)
def _(timev, self):
    'Invoke at datetime.date()'
    if not self.oneshot:
        raise TypeError('Can not repeat a datetime.date()')

    datev = datetime.datetime.combine(timev, datetime.time())
    return self.sched.enterabs(datev.timestamp(), self.prio, self.cb)

@_invoke.register(datetime.time)
def _(timev, self):
    'Invoke at next datetime.time() compared to current time, and on given days'
    now = datetime.datetime.now()
    dow = now.weekday()
    days = 0
    if timev <= now.time():
        dow = ((dow + 1) % 7)
        days += 1

    for days in range(days, days + 7):
        if self.days[dow]:
            break
        dow = ((dow + 1) % 7)

    nextd = now + datetime.timedelta(days=days)
    time = datetime.datetime.combine(nextd.date(), timev)
    return self.sched.enterabs(time.timestamp(), self.prio, self.cb)

class _Timer:
    'Internal class to manage a single instance of a timer'
    def __init__(self, oneshot, sched, days, time, prio, func):
        self.oneshot = oneshot
        self.parent = sched
        self.sched = sched._sched
        daylist = set(parse_days(days))
        self.days = [(i in daylist) for i in range(7)]
        if not any(self.days):
            raise ValueError('Must specify at least one day, 0-6')
        self.time = time
        self.prio = prio
        self.func = func
        self.active = True
        self.parent._count += 1
        # Kick off timer and keep ID (for possible cancel)
        self.eventid = _invoke(time, self)

    def cb(self):
        'Internal callback to invoke user function and reschedule repeat timer'
        self.eventid = None
        self.func()
        if self.active:
            if self.oneshot:
                self.active = False
                self.parent._count -= 1
            else:
                # Set off periodic timer again
                self.eventid = _invoke(self.time, self)

    def cancel(self):
        'Cancel this timer'
        if not self.active:
            raise ValueError('Already cancelled')

        self.active = False
        self.parent._count -= 1
        if self.eventid:
            self.sched.cancel(self.eventid)

class Scheduler:
    'A simple scheduler class to provide oneshot and repeat timers'
    def __init__(self, timefunc=time.time, delayfunc=time.sleep):
        '''
        Create an instance of the scheduler. We are using the standard
        library sched module to do the real work.
        '''
        self._sched = sched.scheduler(timefunc, delayfunc)
        self._count = 0

    def oneshot(self, time, priority, func, *args, **kwargs):
        'Set oneshot timer'
        func = partial(func, *args, **kwargs)
        return _Timer(True, self, None, time, priority, func)

    def repeat(self, period, priority, func, *args, **kwargs):
        'Set repeat timer'
        func = partial(func, *args, **kwargs)
        return _Timer(False, self, None, period, priority, func)

    def oneshot_on_days(self, days, time, priority, func, *args, **kwargs):
        'Set oneshot timer to run on next day of given set of days'
        func = partial(func, *args, **kwargs)
        return _Timer(True, self, days, time, priority, func)

    def repeat_on_days(self, days, period, priority, func, *args, **kwargs):
        'Set repeat timer to run on given days'
        func = partial(func, *args, **kwargs)
        return _Timer(False, self, days, period, priority, func)

    def cancel(self, timer):
        'Cancel oneshot or repeat timer'
        return timer.cancel()

    def count(self):
        'Return count of active timers'
        return self._count

    def run(self, blocking=True):
        'Run all scheduled timers'
        return self._sched.run(blocking)
