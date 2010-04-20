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

from rtsshell.actions import ConditionedAction


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

