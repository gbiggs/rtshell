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

Objects for managing dynamically-loaded modules and evaluating strings.

'''


import imp
import inspect
import OpenRTM_aist
import RTC
import time

import rts_exceptions


###############################################################################
## Module class - stores a dynamically imported module.

class Module(object):
    def __init__(self, name, mod=None, *args, **kwargs):
        super(Module, self).__init__()
        self._name = name
        self._mod = mod

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


class AutoModule(Module):
    def __init__(self, name, *args, **kwargs):
        super(AutoModule, self).__init__(name, *args, **kwargs)
        self._load_mod()


###############################################################################
## ModuleMgr class - keeps track of loaded extra modules and provides
## evaluation of Python expressions

class ModuleMgr(object):
    def __init__(self, *args, **kwargs):
        super(ModuleMgr, self).__init__()
        self._mods = [Module('RTC', mod=RTC)]

    def evaluate(self, const_expr):
        repl_const_expr = self._repl_mod_name(self._replace_time(const_expr))
        print repl_const_expr
        if not repl_const_expr:
            raise rts_exceptions.EmptyConstExprError
        const = eval(repl_const_expr)
        return const

    def find_class(self, name):
        '''Find a class constructor in one of the modules.

        The first matching class's constructor will be returned.

        @param name The name of the class to search for.

        '''
        for m in self._mods:
            types = [member for member in inspect.getmembers(m.mod,
                    inspect.isclass) if member[0] == name]
            if len(types) == 0:
                continue
            elif len(types) != 1:
                raise rts_exceptions.AmbiguousTypeError(type_name)
            else:
                # Check for the POA module
                if m.name != 'RTC':
                    if not [other_m for other_m in self._mods \
                            if other_m.name == m.name + '__POA']:
                        raise rts_exceptions.MissingPOAError(m.name)
                return types[0][1]
        raise rts_exceptions.TypeNotFoundError(name)

    def load_mods(self, mods):
        '''Load a list of modules.

        @param mods The module names, as a list of strings.

        '''
        self._mods += [AutoModule(m) for m in mods]

    def load_mods_and_poas(self, mods):
        '''Load a set of modules and their POA modules.

        @param mods The module names, as a list of strings.

        '''
        for m in mods:
            self._mods.append(AutoModule(m))
            try:
                self._mods.append(AutoModule(m + '__POA'))
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
                        'self._mods[{0}].mod'.format(self._mods.index(m)))
        return string

    def _replace_time(self, const):
        '''Replaces any occurances with {time} with the system time.'''
        now = time.time()
        sys_time = RTC.Time(int(now), int((now - int(now)) * 1e9))
        return const.format(time=sys_time)

