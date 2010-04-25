# -*- Python -*- # -*- coding: utf-8 -*-

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
from os import sep as pathsep
from rtctree.component import Component
from rtctree.path import parse_path
from rtsprofile.message_sending import Condition, Preceding, WaitTime
import threading

from rtsshell.exceptions import PrecedingTimeoutError


###############################################################################
## Action executor objects

class ActionExecutor(threading.Thread):
    '''An object for managing execution of an action.

    This object is capable of executing an action immediately when it is
    called, or delaying execution until a set of conditions is reached. Which
    should occur is chosen automatically. If execution needs to be delayed, a
    new thread will be started to manage it. This thread will sleep until all
    pre-conditions for the action are met. Any number of condition objects can
    be added.

    Callbacks can be added to be executed after executing the action.

    '''
    def __init__(self, action=None, *args, **kwargs):
        super(ActionExecutor, self).__init__(*args, **kwargs)
        self._action = action
        self._callbacks = []
        self._conditions = []
        self._cancelled = False
        self._cancel_lock = threading.Lock()
        self._flag = threading.Event()
        self._completed = False
        self._completed_lock = threading.Lock()

    def __str__(self):
        result = ''
        if self._conditions:
            result += '[{0}'.format(self._conditions[0])
            for c in self._conditions[1:]:
                result += ', {0}'.format(c)
            result += '] '
        return result + str(self._action)

    def __call__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        if self.immediate:
            self._execute_action()
        else:
            self._start_non_immediates()
            self.start()

    def add_callback(self, callback):
        '''Add a new callback to be executed after the action.'''
        self._callbacks.append(callback)

    def add_condition(self, condition):
        '''Add a new condition on the action's execution.'''
        self._conditions.append(condition)

    def cancel(self):
        '''Cancel this action.'''
        with self._cancel_lock:
            self._cancelled = True

    @property
    def action(self):
        '''The action object that will be executed.'''
        return self._action

    @action.setter
    def action(self, action):
        self._action = action

    @property
    def complete(self):
        '''Has this action completed yet?'''
        with self._completed_lock:
            return self._completed

    @property
    def immediate(self):
        '''Tests if this executor can execute immediately.

        If this executor has any conditions that are not immediate, the
        executor itself is not immediate.

        '''
        if not self._conditions:
            return True
        return reduce(lambda x, y: x.satisfied or y.satisfied,
                      self._conditions)

    @property
    def sort_order(self):
        '''The integer order for this action in plans.

        Generally, all actions will have a sequence number. For those that
        don't, this property will be negative. Actions should be executed in
        the order of their sequence number, from smaller to bigger.

        '''
        if not self._conditions:
            return -1
        return min([c.sequence for c in self._conditions])

    def run(self):
        cons_satisfied = False
        if not self._conditions:
            # All conditions have been met
            self.cons_satisfied = True
        while not cons_satisfied:
            for c in self._conditions:
                if c.error:
                    raise c.error
            self._flag.wait()
            self._flag.clear()
            with self._cancel_lock:
                if self._cancelled:
                    self._cancel_conditions()
                    return
            self._reduce_conds()
            if not self._conditions:
                # All conditions have been met
                self.cons_satisfied = True
        self._execute_action()
        with self._completed_lock:
            self._completed = True

    def _do_callbacks(self):
        for c in self._callbacks:
            c(*self._args, **self._kwargs)

    def _execute_action(self):
        print 'Executing action', self._action
        self._action(*self._args, **self._kwargs)
        self._do_callbacks()

    def _reduce_conds(self):
        result = []
        for c in self._conditions:
            if c.satisfied:
                c.join()
            else:
                result.append(c)
                continue
        self._conditions = result

    def _set(self):
        self._flag.set()

    def _start_conds(self):
        for c in self._conditions:
            if not c.immediate:
                c.set_args(*self._args, **self.__kwargs)
                c.start()


class BasicCondition(object):
    '''A simple condition specifying just a sequence ordering.

    This condition is immediate.

    All other condition types should inherit from this type.

    '''
    def __init__(self, executor=None, sequence=-1, desc='', *args, **kwargs):
        super(BasicCondition, self).__init__()
        self._executor = executor
        self._sequence = sequence
        self._desc = desc
        self._error = None
        self._err_lock = threading.Lock()
        self._satisfied = True
        self._sat_lock = threading.Lock()

    def __str__(self):
        return 'Order {0}'.format(self._sequence)

    def cancel(self):
        return

    def set_args(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def wait_for_exit(self):
        '''Wait for this condition's thread to exit.'''
        # Nothing to join in an immediate condition
        return

    @property
    def error(self):
        '''Any error that has occurred in this condition.'''
        with self._err_lock:
            return self._error

    @property
    def immediate(self):
        '''Will this condition be satisfied immediately?'''
        return True

    @property
    def satisfied(self):
        '''Is this condition satisfied?'''
        with self._sat_lock:
            return self._satisfied

    @property
    def sequence(self):
        '''The sequence order of this condition.'''
        return self._sequence


class SleepCondition(BasicCondition):
    '''A condition that waits for a period of time before being satisfied.

    This condition is delayed.

    This condition is essentially a sleep. It starts a threaded timer, which
    sleeps for the given period of time before waking up and setting the
    condition to satisfied.

    '''
    def __init__(self, wait_time=0, *args, **kwargs):
        super(SleepCondition, self).__init__(wait_time=wait_time, *args, **kwargs)
        self._wait_time = wait_time
        self._immediate = False
        self._satisfied = False
        self._timer = None

    def cancel(self):
        self._timer.cancel()

    def satisfy(self):
        with self._sat_lock:
            self._satisfied = True
        self._executor.set()

    def start(self):
        self._timer = threading.Timer(self._wait_time, self.satisfy)
        self._timer.start()


class DelayedCondition(BasicCondition, threading.Thread):
    '''Base class for delayed conditions.

    Inheriting condition objects should implement the @ref check method,
    returning True or False appropriately.

    Delayed conditions start a separate thread, which they use to perform their
    condition check at an appropriate time. They use the reference to their
    owner to signal it that the condition has been met. If their condition is
    not met within an optional timeout, @ref PrecedingTimeoutError is raised.

    Once a delayed condition is satisfied, you should ensure its thread has
    completed by calling @ref wait_for_exit.

    '''
    def __init__(self, timeout=0, *args, **kwargs):
        super(DelayedCondition, self).__init__(timeout=timeout, *args, **kwargs)
        self._immediate = False
        self._satisfied = False
        self._cancelled = False
        self._cancel_lock = threading.Lock()
        self._timeout = timeout

    def __str__(self):
        return self._desc

    def cancel(self):
        with self._cancel_lock:
            self._cancelled = True

    def wait_for_exit(self):
        self.join()

    def run(self):
        while True:
            try:
                satisfied = self._check()
            except Exception, e:
                with self._err_lock:
                    self._error = e
                    break
            with self._cancel_lock:
                if self._cancelled:
                    return
            with self._sat_lock:
                self._satisfied = satisfied
            if satisfied:
                # Signal the owner
                self._executor.set()
                break
            self._adjust_timeout()
            if self._timeout <= 0.0:
                raise PrecedingTimeoutError

    def _adjust_timeout(self):
        diff = time.time() - self._start_time
        self._timeout = self._timeout - diff


class EventCondition(DelayedCondition):
    '''A condition that waits for an event.

    This condition is delayed.

    This condition waits on a @ref threading.Event object. It uses a separate
    thread to perform the wait; it will sleep until its event is set. When the
    event is set, it wakes up and notifies its executor, then exits. If the
    event is not set within an optional timeout, @ref PrecedingTimeoutError is
    raised.

    '''
    def __init__(self, *args, **kwargs):
        super(EventCondition, self).__init__(*args, **kwargs)
        self._event = threading.Event()

    def cancel(self):
        self._event.set()
        super(EventCondition, self).cancel()

    def set(self):
        self._event.set()

    def _check(self):
        self._event.wait(self._timeout)
        if self._event.is_set():
            return True
        return False


class MonitorCondition(DelayedCondition):
    '''A condition that monitors a state.

    This condition is delayed.

    This condition continuously monitors the state of a callback function. When
    the callback's return value matches a provided target value, the condition
    is satisfied. If this does not occur within an optional timeout, @ref
    PrecedingTimeoutError is raised. The callback will be called at the
    frequency specified, in Hertz.

    The callback will be passed all the arguments that get passed to @ref
    set_args. It should accept any arguments it needs, as well as *args and
    **kwargs.

    '''
    def __init__(self, callback=None, target=None, freq=100, *args, **kwargs):
        super(MonitorCondition, self).__init__(callback=callback,
                target=target, freq=freq, *args, **kwargs)
        self._callback = callback
        self._target = target
        self._sleep_time = 1.0 / freq

    def _check(self):
        if self._callback(*self._args, **self._kwargs) == self._target:
            return True


###############################################################################
## Plan object

def _make_check_comp_state_cb(rtsprofile, target_comp):
    def cb(rtctree=rtctree, *args, **kwargs):
        comp = rtsprofile.find_comp_by_target(target_comp)
        path = pathsep + source_comp.path_uri
        comp = rtctree.get_node(parse_path(path)[0])
        return comp.state
    return cb

def _make_action_cb(target_ec):
    def cb():
        target_ec.set()
    return cb

class Plan(object):
    '''A plan for changing the state of an RT System.

    A plan has two sets of actions to perform. The first is stored in a sorted
    list; it is all actions that are to be executed immediately.  The second
    set is stored in a separate list, also sorted. This set contains actions
    that will be executed at a later point in time, based on some condition.
    Many of these will execute on their own threads.

    To execute the plan, call it. A plan can be cancelled during execution with
    the @ref cancel method. As immediate actions will all be executed before
    @ref execute returns, this is mainly useful for stopping the delayed
    actions after an error occurs.

    '''
    def __init__(self, *args, **kwargs):
        super(Plan, self).__init__(*args, **kwargs)
        self._immediates = []
        self._laters = []
        self._complete_flag = threading.Event()

    def __str__(self):
        result = ''
        for a in self._immediates:
            result += '{0}\n'.format(a)
        for a in self._laters:
            result += '{0}\n'.format(a)
        return result[:-1]

    def cancel(self):
        '''Cancel execution of this plan.'''

    def execute(self, *args, **kwargs):
        '''Execute this plan.'''
        for a in self._immediates:
            a(*args, **kwargs)
        for a in self._laters:
            a(*args, **kwargs)
        while self._laters:
            self._complete_flag.wait()
            with self._cancelled_lock:
                if self._cancelled:
                    for a in self._laters:
                        a.cancel()
                    return
            if self._complete_flag.is_set():
                self._laters = [a for a in self._laters if not a.complete]
                self._complete_flag.clear()

    def make(self, rtsprofile, actions):
        '''Make a plan from a list of actions and an RTSProfile.'''
        all = {}
        # First build a dictionary indexed by target for each action
        for a in actions:
            all[(a.ec_id, a.comp_id, a.instance_name)] = \
                    ActionExecutor(action=a)
        # For each action, find all its conditions and add them to the action's
        # executor.
        for a in actions:
            # First add an executor for each action to a temporary dictionary
            conds = self._get_action_conditions(rtsprofile, a)
            if not conds:
                continue
            for c in conds:
                target = (c.target_component.id,
                          c.target_component.component_id,
                          c.target_component.instance_name)
                action = all[target]
                if c.__class__ == Condition:
                    # Just a sequencing value
                    action.add_condition(BasicCondition(executor=action,
                            sequence=c.sequence))
                elif c.__class__ == WaitTime:
                    # An action to be executed after a certain amount of time
                    action.add_condition(SleepCondition(executor=action,
                        wait_time=c.wait_time * 1000, sequence=c.sequence))
                elif c.__class__ == Preceding:
                    # An action that waits for a previous action to
                    # occur/complete.
                    if c.sending_timing == 'PRE':
                        # Wait for action to occur
                        for p in c.preceding_components:
                            ec = EventCondition(executor=action,
                                    sequence=c.sequence)
                            action.add_condition(ec)
                            target_p = (p.id, p.component_id, p.instance_name)
                            all[target_p].add_callback(_make_action_cb(ec))
                            if all[target_p].action.optional:
                                print >>sys.stderr, 'Warning: action depends \
on previous action, which is optional. This may cause a deadlock if the \
previous action\'s component is not present.'
                    else:
                        # Wait for action to complete
                        for p in c.preceding_components:
                            mc = MonitorCondition(executor=action,
                                    sequence=c.sequence,
                                    callback=_make_check_comp_state_cb(rtsprofile, p),
                                    target=component.ACTIVE)
                            action.add_condition(mc)
                            target_p = (p.id, p.component_id, p.instance_name)
                            if all[target_p].action.optional:
                                print >>sys.stderr, 'Warning: action depends \
on an optional action. This may cause a deadlock if the previous action\'s \
component is not present.'
        for k, a in all.items():
            if a.immediate:
                self._immediates.append(a)
            else:
                self._laters.append(a)
        self._immediates.sort(key=attrgetter('sort_order'))
        self._laters.sort(key=attrgetter('sort_order'))

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

    def _signal_complete(self):
        self._complete_flag.set()


# vim: tw=79

