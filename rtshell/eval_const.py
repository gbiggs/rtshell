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


###############################################################################
## Module class - stores a dynamically imported module.

class Module(object):
    def __init__(self, name, *args, **kwargs):
        super(Module, self).__init__()
        self._name = name
        self._mod = None
        self._load_mod()

    def __str__(self):
        return '{0}: {1}'.format(self._name, self._mod)

    @property
    def name(self):
        '''The name of the module, as it would be called in source.'''
        return self._name

    @property
    def mod(self):
        '''The module object.'''
        return self._mod

    def _load_mod(self):
        '''Loads the module object.'''
        f = None
        try:
            f, p, d = imp.find_module(self._name)
            self._mod = imp.load_module(self._name, f, p, d)
        finally:
            if f:
                f.close()


###############################################################################
## Evaluator class - keeps track of loaded extra modules.

class Evaluator(object):
    def __init__(self, *args, **kwargs):
        super(Evaluator, self).__init__()
        self._mods = []

    def evaluate(self, const_expr):
        repl_const_expr = self.repl_mod_name(replace_time(const_expr))
        if not repl_const_expr:
            raise rts_exceptions.EmptyConstExprError
        const = eval(repl_const_expr)
        return const

    def load_mods(self, mods):
        '''Load a list of modules.

        @param mods The module names, a list of strings or a single
                    comma-separated string of names.

        '''
        if type(mods) == list:
            self._mods += [Module(m) for m in mods]
        elif type(mods) == str:
            self._mods += [Module(m) for m in mods.split(',') if m]
        else:
            raise TypeError

    def load_mods_and_poas(self, mods):
        '''Load a set of modules and their POA modules.

        @param mods The module names, as a comma-separated string.

        '''
        for m in mods.split(','):
            if not m:
                continue
            self._mods.append(Module(m))
            try:
                self._mods.append(Module(m + '__POA'))
            except ImportError:
                print >>sys.stderr, '{0}: Failed to import module {1}'.format(\
                        sys.argv[0], m + '__POA')
                pass

    @property
    def loaded_mod_names(self):
        return [str(m) for m in self._mods]

    def _repl_mod_name(self, string):
        '''Replace the name of a module.

        Replaces a reference to a module in a string with its reference in
        the modules array.

        @param string The constant string.
        @param mods A list of Module objects.

        '''
        for m in self._mods:
            if m.name in string:
                string = string.replace(m.name,
                        'self._mods[{0}].mod'.format(mods.index(m)))
        return string

    def _replace_time(self, const):
        '''Replaces any occurances with {time} with the system time.'''
        now = time.time()
        sys_time = RTC.Time(int(now), int((now - int(now)) * 1e9))
        return const.format(time=sys_time)

