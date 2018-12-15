'''
A simple class to provide oneshot and repeat timers.
M.Blakeney, Nov 2018.
'''
import sched, time, datetime
from functools import singledispatch, partial

# Dispatch timer based on type
@singledispatch
def _invoke(timev, oneshot, sched, *args):
    'Invoke after default int/float secs'
    return sched.enter(timev, *args)

@_invoke.register(datetime.timedelta)
def _(timev, oneshot, sched, *args):
    'Invoke after datetime.timedelta()'
    return sched.enter(timev.total_seconds(), *args)

@_invoke.register(datetime.datetime)
def _(timev, oneshot, sched, *args):
    'Invoke at datetime.datetime()'
    if not oneshot:
        raise TypeError('Can not repeat a datetime.datetime()')

    return sched.enterabs(timev.timestamp(), *args)

@_invoke.register(datetime.date)
def _(timev, oneshot, sched, *args):
    'Invoke at datetime.date()'
    if not oneshot:
        raise TypeError('Can not repeat a datetime.date()')

    datev = datetime.datetime.combine(timev, datetime.time())
    return sched.enterabs(datev.timestamp(), *args)

@_invoke.register(datetime.time)
def _(timev, oneshot, sched, *args):
    'Invoke at next datetime.time() compared to current time'
    now = datetime.datetime.now()
    nextd = now.date()
    if timev < now.time():
        nextd += datetime.timedelta(days=1)
    time = datetime.datetime.combine(nextd, timev)
    return sched.enterabs(time.timestamp(), *args)

class _Timer():
    'Internal class to manage a single instance of a timer'
    def __init__(self, oneshot, sched, time, prio, func):
        self.oneshot = oneshot
        self.sched = sched
        self.time = time
        self.prio = prio
        self.func = func
        self.active = True
        self.sched._count += 1
        self._schedule()

    def _schedule(self):
        'Kick off timer and keep ID (for possible cancel)'
        self.eventid = _invoke(self.time, self.oneshot, self.sched._sched,
                self.prio, self._cb)

    def _cb(self):
        'Internal callback to invoke user function and reschedule repeat timer'
        self.eventid = None
        self.func()
        if self.active:
            if self.oneshot:
                self.active = False
                self.sched._count -= 1
            else:
                self._schedule()

    def cancel(self):
        'Cancel this timer'
        if self.active:
            self.active = False
            self.sched._count -= 1
            if self.eventid:
                self.sched._sched.cancel(self.eventid)
        else:
            raise ValueError('Already cancelled')

class Scheduler():
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
        return _Timer(True, self, time, priority, func)

    def repeat(self, period, priority, func, *args, **kwargs):
        'Set repeat timer'
        func = partial(func, *args, **kwargs)
        return _Timer(False, self, period, priority, func)

    def cancel(self, timer):
        'Cancel oneshot or repeat timer'
        return timer.cancel()

    def count(self):
        'Return count of active timers'
        return self._count

    def run(self, blocking=True):
        'Run all scheduled timers'
        return self._sched.run(blocking)
