#!/usr/bin/env python2
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2015
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the GNU Lesser General Public License version 3.
http://www.gnu.org/licenses/lgpl-3.0.en.html

Objects for managing dynamically-loaded modules and evaluating strings.

'''

from __future__ import print_function

import imp
import inspect
import OpenRTM_aist
import os.path
import re
import RTC
import sys
import time

from rtshell import rts_exceptions


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
        mod_list = self._name.split('.')
        self._mod = self._recursive_load(mod_list[0], mod_list[1:], None)

    def _recursive_load(self, head, rest, top_path):
        '''Recurse through a dotted module path, loading each module.'''
        f = None
        try:
            f, p, d = imp.find_module(head, top_path)
            mod = imp.load_module(head, f, p, d)
        finally:
            if f:
                f.close()
        if not rest:
            return mod
        else:
            return self._recursive_load(rest[0], rest[1:], mod.__path__)


class AutoModule(Module):
    def __init__(self, name, *args, **kwargs):
        super(AutoModule, self).__init__(name, *args, **kwargs)
        self._load_mod()


###############################################################################
## ModuleMgr class - keeps track of loaded extra modules and provides
## evaluation of Python expressions

class ModuleMgr(object):
    def __init__(self, verbose=False, paths=[], *args, **kwargs):
        super(ModuleMgr, self).__init__()
        self._mods = {'RTC': Module('RTC', mod=RTC)}
        self._verb = verbose
        self._add_paths(paths)

    def _add_paths(self, paths=[]):
        for p in paths:
            if self._verb:
                print('Adding {0} to PYTHONPATH'.format(p), file=sys.stderr)
            sys.path.insert(0, p)

    def evaluate(self, expr):
        self._auto_import(expr)
        repl_expr = self._repl_mod_name(_replace_time(expr))
        if not repl_expr:
            raise rts_exceptions.EmptyConstExprError
        if self._verb:
            print >>sys.stderr, 'Evaluating expression {0}'.format(repl_expr)
        const = eval(repl_expr)
        return const

    def find_class(self, name):
        '''Find a class constructor in one of the modules.

        The first matching class's constructor will be returned.

        @param name The name of the class to search for.

        '''
        # Replace / in the name with . to create a Python path
        name = name.replace('/', '.')
        self._auto_import(name)
        # Strip the name down to the class
        name = _find_object_name(name)
        for m in list(self._mods.values()):
            if m.name == 'RTC':
                # Search RTC last to allow user types to override RTC types
                continue
            types = [member for member in inspect.getmembers(m.mod,
                    inspect.isclass) if member[0] == name or "IDL:"+list(self._mods.keys())[0]+"/"+member[0]+":1.0" == name]
            if len(types) == 0:
                continue
            elif len(types) != 1:
                raise rts_exceptions.AmbiguousTypeError(type_name)
            else:
                # Check for the POA module
                if m.name != 'RTC':
                    if not [other_m for other_m in list(self._mods.values()) \
                            if other_m.name == m.name + '__POA']:
                        raise rts_exceptions.MissingPOAError(m.name)
                if self._verb:
                    print >>sys.stderr, 'Found type {0} in module {1}'.format(
                            name, m.name)
                return types[0][1]
        # If got to here, the type was not found in any other module, so search
        # the RTC module
        m = self._mods['RTC']
        types = [member for member in inspect.getmembers(m.mod,
                inspect.isclass) if member[0] == name]
        if len(types) != 0:
            if len(types) != 1:
                raise rts_exceptions.AmbiguousTypeError(type_name)
            if self._verb:
                print >>sys.stderr, 'Found type {0} in module {1}'.format(
                        name, m.name)
            return types[0][1]
        raise rts_exceptions.TypeNotFoundError(name)

    def load_mod(self, mod):
        '''Load a module.'''
        m = AutoModule(mod)
        self._mods[mod] = m

    def load_mods(self, mods):
        '''Load a list of modules.

        @param mods The module names, as a list of strings.

        '''
        [self.load_mod(m) for m in mods]

    def load_mods_and_poas(self, mods):
        '''Load a set of modules and their POA modules.

        @param mods The module names, as a list of strings.

        '''
        for m in mods:
            self.load_mod(m)
            try:
                self.load_mod(m + '__POA')
            except ImportError:
                print('{0}: Failed to import POA module {1}'.format(\
                        os.path.basename(sys.argv[0]), m + '__POA'),
                        file=sys.stderr)
                pass

    @property
    def loaded_mod_names(self):
        return list(self._mods.keys())

    def _auto_import(self, expr):
        '''Tries to import all module names found in an expression.

        A failure to import a module will cause a warning, not an error.

        '''
        names = [m for m in _find_module_names(expr) if m not in self._mods]
        if self._verb:
            print >>sys.stderr, 'Automatically importing modules {0}'.format(
                    names)
        for n in names:
            try:
                self.load_mod(n)
            except ImportError:
                print >>sys.stderr, \
                        '{0}: Warning: failed to import module {1}'.format(
                                os.path.basename(sys.argv[0]), n)
                continue
            try:
                self.load_mod(n + '__POA')
            except ImportError:
                print >>sys.stderr, \
                        '{0}: Warning: failed to import POA module {1}'.format(
                                os.path.basename(sys.argv[0]), n + '__POA')
                continue

    def _repl_mod_name(self, expr):
        '''Replace the name of a module.

        Replaces a reference to a module in a string with its reference in
        the modules array.

        '''
        for m in self._mods:
            if m in expr:
                expr = expr.replace(m, 'self._mods["{0}"].mod'.format(m))
        return expr


###############################################################################
## Internal support functions

def _replace_time(expr):
    '''Replaces any occurances with {time} with the system time.'''
    now = time.time()
    sys_time = RTC.Time(int(now), int((now - int(now)) * 1e9))
    return expr.format(time=sys_time)


def _find_module_names(expr):
    '''Finds all potential module names in an expression.'''
    return [x[:-1] for x in re.findall(r'(?P<mod>[a-zA-Z][\w.]*\.)+[a-zA-Z]',
        expr)]


def _find_object_name(expr):
    '''Finds the object at the end of a module...module.object line.'''
    return expr[expr.rfind('.') + 1:]

