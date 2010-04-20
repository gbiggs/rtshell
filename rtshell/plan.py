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
    def __init__(self, action, *args, **kwargs):
        super(ActionExecutor, self).__init__(action, *args, **kwargs)
        self._action = action

    def execute(self, *args):
        self._action(*args)


class SleepyActionExecutor(ActionExecutor):
    '''Executes an action after a specified period of time.

    The threading.Timer class is used to provide the sleep capability. When
    execute() is called, a Timer instance is created that will, when it wakes,
    execute the action.

    Call cancel() to cancel the wait prematurely. This will only have an effect
    after execute() has been called.

    '''
    def __init__(self, action, wait_time, *args, **kwargs):
        '''Constructor.

        @param action The action to execute.
        @param wait_time The time to wait before execution, in milliseconds.

        '''
        super(SleepyActionExecutor, self).__init__(action, wait_time,
                                                   *args, **kwargs)
        self._timer = None
        self._wait_time = wait_time

    def cancel(self):
        if self._timer:
            self._timer.cancel()

    def execute(self, *args):
        self._timer = threading.Timer(self._wait_time, self._action, args=*args)


class ThreadedActionExecutor(ActionExecutor, threading.Thread):
    '''Executes an action in a separate thread of control.

    When this class's execute method is called, the action will be executed in a
    new thread.

    '''
    def __init__(self, action, *args, **kwargs):
        super(ThreadedActionExecutor, self).__init__(action, *args, **kwargs)

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
    def __init__(self, action, timeout=0, count=1, *args, **kwargs):
        super(EventActionExecutor, self).__init__(action, timeout, count,
                                                  *args, **kwargs)
        self._timeout = float(timeout) / 1000.0
        self._cancelled = False
        self._count = count
        self._flag = threading.Event()
        self._start_time = time.time()
        self._set_lock = threading.Mutex()

    def cancel(self):

    def execute(self, *args):
        self._args = args
        super(EventActionExecutor, self).start()

    def run(self):
        self._set_lock.acquire()
        while count > 0:
            # Release the mutex before waiting to prevent deadlocks
            self._set_lock.release()
            self._adjust_timeout()
            self._flag.wait(self._timeout)
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




def get_action_condition(rtsprofile, action):
    '''Get the corresponding condition for an action, if any.'''
    if rtsprofile.activation.targets:
        for c in rtsprofile.activation.targets:
            target = c.target_component
            if target.id == action.ec_id and \
               target.component_id == action.comp_id and \
               target.instance_name == action.instance_name:
                return c
    return None


def condition_action(rtsprofile, action):
    '''Wrap an action with a condition.'''
    c = get_action_condition(rtsprofile, action)
    if not c:
        return ConditionedAction(action)
    result = ConditionedAction(action, c.sequence)
    if c.__class__ == WaitTime:
        # Add a wait time to the condition
        result.wait_time = c.wait_time
    elif c.__class__ == Preceding:
        # Add timeout, pre- or post-occurance and preceding targets
        result.timeout = c.timeout
    return result


def condition_actions(rtsprofile, actions):
    '''Wrap a list of actions with conditions.'''
    result = [condition_action(rtsprofile, a) for a in actions]
    result.sort(key=attrgetter('seq_id'))
    return result


def make_plan(rtsprofile, actions):
    '''Make a plan based on the conditions specified in an RTSProfile.'''
    return condition_actions(rtsprofile, actions)


def print_plan(plan):
    '''Pretty-print a plan for dry runs.'''
    for p in plan:
        print p


def execute_plan(rtctree, plan, rate=100):
    '''Execute a plan.

    This function executes a complete plan to change the state of an RT System.
    It does not exit until the plan has completed or a fatal error has occured.

    '''
    for a in plan:
        a(rtctree)


# vim: tw=79

