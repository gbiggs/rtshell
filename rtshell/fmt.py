#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Built-in formatters for rtprint.

'''

import inspect
import rts_exceptions


###############################################################################
## Python source formatter

def rawpy(data):
    return data.__repr__()


###############################################################################
## Formatter importer

def import_formatter(form, modmgr):
    '''Import a formatter.

    This function attempts to evaluate an expression specifying a function
    object that can be used to format a piece of data. The imported function
    must receive one positional argument, which is the data to format.

    @param form The formatter expression.
    @param modmgr The module manager to use to evaluate @ref form.

    '''
    # Special case for internal formatters: replace 'rtshell' with 'fmt'
    form_rpl = form
    if form.startswith('rtshell.'):
        form_rpl = 'fmt.' + form[8:]
    try:
        form_fun = modmgr.evaluate(form_rpl)
    except Exception, e:
        raise rts_exceptions.ImportFormatterError(e)
    # Check if the formatter is a function
    if type(form_fun) != type(import_formatter):
        raise rts_exceptions.BadFormatterError(form)
    args, varargs, varkw, defaults = inspect.getargspec(form_fun)
    if len(args) != 1 or varargs or varkw or defaults:
        raise BadFormatterError(form)
    return form_fun

