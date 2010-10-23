#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Functions for evaluating constants provided as strings.

'''


import OpenRTM_aist
import RTC
import time

import rts_exceptions


def replace_mod_name(string, mods):
    '''Replace the name of a module.

    Replaces a reference to a module in a string with its reference in
    the modules array.

    @param string The constant string.
    @param mods A list of user_mods.Module objects.

    '''
    for m in mods:
        if m.name in string:
            string = string.replace(m.name, 'mods[{0}].mod'.format(mods.index(m)))
    return string


def replace_time(const):
    '''Replaces any occurances with {time} with the system time.'''
    now = time.time()
    sys_time = RTC.Time(int(now), int((now - int(now)) * 1e9))
    return const.format(time=sys_time)


def eval_const(const_expr, mods):
    repl_const_expr = replace_mod_name(replace_time(const_expr), mods)
    if not repl_const_expr:
        raise rts_exceptions.EmptyConstExprError
    const = eval(repl_const_expr)
    return const

