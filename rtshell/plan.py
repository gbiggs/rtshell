# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtsshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: plan.py

Creation and execution of state change plans.

'''

__version__ = '$Revision: $'
# $Source$


from operator import attrgetter
from rtsprofile.message_sending import Condition, Preceding, WaitTime
import threading

from rtsshell.actions import ConditionedAction
from rtsshell.exceptions import PrecedingTimeoutError


###############################################################################
## Action executor objects

class ActionExecutor(object):
    '''Executes an action immediately when its execute method is called.'''
    def __init__(self, action=None, *args, **kwargs):
        super(ActionExecutor, self).__init__()
        self._action = action

    def execute(self, *args):
        self._action(*args)

    @property
    def action(self):
        '''The action object that will be executed.'''
        return self._action


class OrderedActionExecutor(ActionExecutor):
    '''Executes an action immediately. Has a sequence value for ordering.

    A sequence value of less than zero indicates no preferred order other than
    before all sequence values greater than or equal to zero.

    '''
    def __init__(self, sequence=-1, *args, **kwargs):
        super(OrderedActionExecutor, self).__init__(sequence=sequence, *args,
                                                    **kwargs)
        self._sequence = sequence

    @property
    def sequence(self):
        '''The position in the order in which to execute the action.'''
        return self._sequence


class SleepyActionExecutor(ActionExecutor):
    '''Executes an action after a specified period of time.

    The threading.Timer class is used to provide the sleep capability. When
    execute() is called, a Timer instance is created that will, when it wakes,
    execute the action.

    Call cancel() to cancel the wait prematurely. This will only have an effect
    after execute() has been called.

    '''
    def __init__(self, action=None, wait_time=0, *args, **kwargs):
        '''Constructor.

        @param action The action to execute.
        @param wait_time The time to wait before execution, in milliseconds.

        '''
        super(SleepyActionExecutor, self).__init__(action=action,
                wait_time=wait_time, *args, **kwargs)
        self._timer = None
        self._wait_time = wait_time

    def cancel(self):
        if self._timer:
            self._timer.cancel()

    def execute(self, *args):
        self._timer = threading.Timer(self._wait_time, self._action, args=args)
        self._timer.start()


class ThreadedActionExecutor(ActionExecutor, threading.Thread):
    '''Executes an action in a separate thread of control.

    When this class's execute method is called, the action will be executed in a
    new thread.

    '''
    def __init__(self, action=None, *args, **kwargs):
        super(ThreadedActionExecutor, self).__init__(action=action, *args, **kwargs)

    def execute(self, *args):
        self._args = args
        super(ThreadedActionExecutor, self).start()

    def run(self):
        self._action(*self._args)


class EventActionExecutor(ThreadedActionExecutor):
    '''Executes an action in a separate thread of control after an event.

    When this class's execute method is called, a new thread is started. That
    thread will wait on a @ref threading.Event object. The event can be
    signaled through the set method. A count can be specified at construction
    time; this is the number of times the event must be signaled before the
    action will be executed.  On the occasion that an event trigger causes the
    count to reach zero, and thus the action to be executed.

    If the optional timeout occurs before the event is triggered a sufficient
    number of times, @ref PrecedingTimeoutError will be raised.

    '''
    def __init__(self, action=None, timeout=0, count=1, *args, **kwargs):
        super(EventActionExecutor, self).__init__(action=action,
                timeout=timeout, count=count, *args, **kwargs)
        self._timeout = float(timeout) / 1000.0
        self._cancelled = False
        self._count = count
        self._flag = threading.Event()
        self._start_time = time.time()
        self._set_lock = threading.Lock()
        self._cancel_lock = threading.Lock()

    def cancel(self):
        with self._cancel_lock:
            self._cancelled = True

    def execute(self, *args):
        self._args = args
        self.start()

    def run(self):
        self._set_lock.acquire()
        while count > 0:
            # Release the mutex before waiting to prevent deadlocks
            self._set_lock.release()
            self._adjust_timeout()
            self._flag.wait(self._timeout)
            with self._cancel_lock:
                if self._cancelled:
                    return
            # Check the timeout
            self._adjust_timeout()
            if self._timeout <= 0.0:
                raise PrecedingTimeoutError
            # Grab the mutex so we can check count and possibly sleep again
            # without someone else mucking with it via set()
            self._set_lock.acquire()
        # Release here just in case someone is calling set() (even though they
        # shouldn't by now), avoiding deadlocks
        self._set_lock.release()
        self._action(*self._args)

    def set(self):
        self._set_lock.acquire()
        self._count -= 1
        self._flag.set()
        self._set_lock.release()

    def _adjust_timeout(self):
        diff = time.time() - self._start_time
        self._timeout = self._timeout - diff


class MonitoringActionExecutor(ActionExecutor):
    '''Executes an action when a function call returns True.

    This class uses a provided function object. It regularly calls the function
    object, at a rate specified. When the function object call returns True,
    the action is executed. If the function object does not return True to a
    call within an optional timeout, @ref PrecedingTimeoutError will be raised.

    The default rate is 100Hz.

    '''
    def __init__(self, action=None, timeout=0, freq=0, func=None, *args,
                 **kwargs):
        '''Constructor.

        @param action The action to execute.
        @param timeout The timeout for the function object to return True (ms).
        @param freq The frequency to check the function object (Hz).
        @param func The function object to call to exectute the check.

        '''
        super(MonitoringActionExecutor, self).__init__(action=action,
                timeout=timeout, freq=freq, func=func, *args, **kwargs)
        self._timeout = float(timeout) / 1000.0
        self._wait_time = 1.0 / freq
        self._condition = func
        self._cancelled = False
        self._start_time = time.time()
        self._cancel_lock = threading.Lock()

    def cancel(self):
        with self._cancel_lock:
            self._cancelled = True

    def execute(self, *args):
        # Use a timer to sleep for the required period of time
        self._timer = threading.Timer(self._wait_time, self._perform_check,
                                      args=args)
        self._timer.start()

    def _perform_check(self, *args):
        with self._cancel_lock:
            if self._cancelled:
                return
        if self._condition():
            # Check passed, execute the action
            self._action(*args)
        else:
            # Check failed, check the timeout
            self._adjust_timeout()
            if self._timeout <= 0.0:
                raise PrecedingTimeoutError
            # Wait again
            self._timer.start()

    def _adjust_timeout(self):
        diff = time.time() - self._start_time
        self._timeout = self._timeout - diff


###############################################################################
## Plan object

class Plan(object):
    '''A plan for changing the state of an RT System.

    A plan has two sets of actions to perform. The first is stored in a sorted
    list; it is all actions that are to be executed immediately.  The second
    set is stored in a dictionary, indexed by target, i.e. a tuple of
    (component instance name, component ID, execution context ID). This set
    contains actions that will be executed at a later point in time, based on
    some condition. Many of these will execute on their own threads.

    To execute the plan, run the @ref execute method. A plan can be cancelled
    during execution with the @ref cancel method. As immediate actions will all
    be executed before @ref execute returns, this is mainly useful for stopping
    the delayed actions after an error occurs.

    '''
    def __init__(self, *args, **kwargs):
        super(Plan, self).__init__(*args, **kwargs)
        self._immediates = []
        self._laters = {}

    def __str__(self):
        return str(self._immediates)

    def execute(self):
        return

    def make(self, rtsprofile, actions):
        for a in actions:
            conds = self._get_action_conditions(rtsprofile, a)
            if not conds:
                # Append an immediate executor for this action
                self._immediates.append(OrderedActionExecutor(action=a))
            for c in conds:
                target = (c.target_component.instance_name,
                          c.target_component.component_id,
                          c.target_component.id)
                # Figure out if this action needs to be immediate or delayed
                if c.__class__ == Condition:
                    # An immediate action
                    self._immediates.append(OrderedActionExecutor(action=a,
                                            sequence=c.sequence))
                elif c.__class__ == WaitTime:
                    # An action to be executed after a certain amount of time
                    pass
                elif c.__class__ == Preceding:
                    # An action that waits for a previous action to
                    # occur/complete.
                    pass
                else:
                    # An unknown action type
                    pass
        # Sort the immediates list
        self._immediates.sort(key=attrgetter('sequence'))

    def _get_action_conditions(self, rtsprofile, action):
        # Get the corresponding conditions for an action, if any.
        result = []
        if rtsprofile.activation.targets:
            for c in rtsprofile.activation.targets:
                target = c.target_component
                if target.id == action.ec_id and \
                   target.component_id == action.comp_id and \
                   target.instance_name == action.instance_name:
                    result.append(c)
        return result


# vim: tw=79

