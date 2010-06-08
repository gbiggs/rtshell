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

File: exceptions.py

Exceptions that may occur.

'''

__version__ = '$Revision: $'
# $Source$


class RtsShellError(Exception):
    '''Base error for all errors that may occur.'''


class RequiredActionFailedError(RtsShellError):
    '''Error raised when an action that must succeed fails.'''
    def __str__(self):
        return 'Required action failed: ' + \
                super(RequiredActionFailedError, self).__str__()


class NoSuchOptionError(RtsShellError):
    '''The requested option has not been set.'''
    def __str__(self):
        return 'No such option: ' + \
                super(NoSuchOptionError, self).__str__()


class PrecedingTimeoutError(RtsShellError):
    '''The time limit on a preceding condition being met has elapsed.'''
    def __str__(self):
        return 'Preceding condition timed out: ' + \
                super(PrecedingTimeoutError, self).__str__()


# vim: tw=79

