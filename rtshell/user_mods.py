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

Functions and classes for managing run-time-loaded modules.

'''


import imp
import inspect

import eval_const
import rts_exceptions


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


class PreloadedModule(Module):
    def __init__(self, name, mod, *args, **kwargs):
        super(PreloadedModule, self).__init__(name, *args, **kwargs)
        self._mod = mod

    def _load_mod(self):
        pass


def load_mods(mods):
    '''Load a list of modules.

    @param mods The module names, a list of strings or a single
                comma-separated string of names.

    '''
    if type(mods) == list:
        return [Module(m) for m in mods]
    elif type(mods) == str:
        return [Module(m) for m in mods.split(',') if m]
    else:
        raise TypeError


def load_mods_and_poas(mods):
    '''Load a set of modules and their POA modules.

    @param mods The module names, as a comma-separated string.

    '''
    result = []
    for m in mods.split(','):
        if not m:
            continue
        mod = Module(m)
        result.append(mod)
        try:
            mod_poa = Module(m + '__POA')
            result.append(mod_poa)
        except ImportError:
            pass
    return result


def import_formatter(form, mods):
    '''Import a formatter.

    This function attempts to evaluate an expression specifying a function
    object that can be used to format a piece of data. The imported function
    must receive one positional argument, which is the data to format.

    '''
    form_rpl = eval_const.replace_mod_name(form, mods)
    try:
        form_fun = eval(form_rpl)
    except Exception, e:
        raise rts_exceptions.ImportFormatterError(e)
    # Check if the formatter is a function
    if type(form_fun) != type(import_formatter):
        raise rts_exceptions.BadFormatterError(form)
    args, varargs, varkw, defaults = inspect.getargspec(form_fun)
    if len(args) != 1 or varargs or varkw or defaults:
        raise BadFormatterError(form)
    return form_fun

