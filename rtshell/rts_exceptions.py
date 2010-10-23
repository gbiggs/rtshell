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

Exceptions that may occur.

'''


import rtctree.path


class RtShellError(Exception):
    '''Base error for all errors that may occur.'''
    def __init__(self, *args, **kwargs):
        super(RtShellError, self).__init__(self, *args, **kwargs)


class RequiredActionFailedError(RtShellError):
    '''Error raised when an action that must succeed fails.'''
    def __init__(self, *args, **kwargs):
        super(RequiredActionFailedError, self).__init__(self, *args, **kwargs)

    def __str__(self):
        return 'Required action failed: ' + \
                super(RequiredActionFailedError, self).__str__()


class NoSuchOptionError(RtShellError):
    '''The requested option has not been set.'''
    def __init__(self, *args, **kwargs):
        super(NoSuchOptionError, self).__init__(self, *args, **kwargs)

    def __str__(self):
        return 'No such option: ' + \
                super(NoSuchOptionError, self).__str__()


class PrecedingTimeoutError(RtShellError):
    '''The time limit on a preceding condition being met has elapsed.'''
    def __init__(self, *args, **kwargs):
        super(PrecedingTimeoutError, self).__init__(self, *args, **kwargs)

    def __str__(self):
        return 'Preceding condition timed out: ' + \
                super(PrecedingTimeoutError, self).__str__()


class EmptyConstExprError(RtShellError):
    '''A constant expression that should be evaluated is empty.'''
    def __init__(self, *args, **kwargs):
        super(EmptyConstExprError, self).__init__(self, *args, **kwargs)

    def __str__(self):
        return 'Empty constant expression '


class AmbiguousTypeError(RtShellError):
    '''A data type is ambiguous.'''
    def __init__(self, type, *args, **kwargs):
        super(AmbiguousTypeError, self).__init__(self, *args, **kwargs)
        self._type = type

    def __str__(self):
        return 'Ambiguous port type: {0}'.format(self._type)


class TypeNotFoundError(RtShellError):
    '''A data type was not found.'''
    def __init__(self, type, *args, **kwargs):
        super(TypeNotFoundError, self).__init__(self, *args, **kwargs)
        self._type = type

    def __str__(self):
        return 'Type not found: {0}'.format(self._type)


class BadPortSpecError(RtShellError):
    '''A port specification is badly formatted.'''
    def __init__(self, ps, *args, **kwargs):
        super(BadPortSpecError, self).__init__(self, *args, **kwargs)
        self._ps = ps

    def __str__(self):
        return 'Bad port specification: {0}'.format(self._ps)


class NoObjectAtPathError(RtShellError):
    '''There is no object at the given path.'''
    def __init__(self, path, *args, **kwargs):
        super(NoObjectAtPathError, self).__init__(self, *args, **kwargs)
        self._path = path

    def __str__(self):
        return 'No object at path: {0}'.format(\
                rtctree.path.format_path((self._path, None)))


class NotAComponentError(RtShellError):
    '''A given path is not a component.'''
    def __init__(self, path, *args, **kwargs):
        super(NotAComponentError, self).__init__(self, *args, **kwargs)
        self._path = path

    def __str__(self):
        return 'Path is not a component: {0}'.format(\
                rtctree.path.format_path((self._path, None)))


class PortNotFoundError(RtShellError):
    '''The port was not found on the component.'''
    def __init__(self, rtc, port, *args, **kwargs):
        super(PortNotFoundError, self).__init__(self, *args, **kwargs)
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Port not found: {0}'.format(\
                rtctree.path.format_path((self._rtc, self._port)))


class BadPortTypeError(RtShellError):
    '''The port type is not defined.'''
    def __init__(self, rtc, port, *args, **kwargs):
        super(BadPortTypeError, self).__init__(self, *args, **kwargs)
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Incorrect port type: {0}'.format(\
                rtctree.path.format_path((self._rtc, self._port)))


class MissingCompError(RtShellError):
    '''An expected component is missing.'''
    def __init__(self, path, *args, **kwargs):
        super(MissingCompError, self).__init__(self, *args, **kwargs)
        self._path = path

    def __str__(self):
        return 'Expected component missing: {0}'.format(self._path)


class ConnectFailedError(RtShellError):
    '''An error occured connecting two ports.'''
    def __init__(self, rtc, port, *args, **kwargs):
        super(ConnectFailedError, self).__init__(self, *args, **kwargs)
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Failed to connect port: {0}'.format(\
                rtctree.path.format_path((self._rtc, self._port)))


class ActivateError(RtShellError):
    '''An error occured activating a component.'''
    def __init__(self, comp, *args, **kwargs):
        super(ActivateError, self).__init__(self, *args, **kwargs)
        self._comp = comp

    def __str__(self):
        return 'Error activating component: {0}'.format(self._comp)


class DeactivateError(RtShellError):
    '''An error occured deactivating a component.'''
    def __init__(self, comp, *args, **kwargs):
        super(DeactivateError, self).__init__(self, *args, **kwargs)
        self._comp = comp

    def __str__(self):
        return 'Error deactivating component: {0}'.format(self._comp)


class PortNotInputError(RtShellError):
    '''A port is not an input that should be.'''
    def __init__(self, name, *args, **kwargs):
        super(PortNotInputError, self).__init__(self, *args, **kwargs)
        self._name = name

    def __str__(self):
        return 'Port is not input: {0}'.format(self._name)


class PortNotOutputError(RtShellError):
    '''A port is not an output that should be.'''
    def __init__(self, name, *args, **kwargs):
        super(PortNotOutputError, self).__init__(self, *args, **kwargs)
        self._name = name

    def __str__(self):
        return 'Port is not output: {0}'.format(self._name)


class ImportFormatterError(RtShellError):
    '''An error occured importing a formatting function.'''
    def __init__(self, exc, *args, **kwargs):
        super(ImportFormatterError, self).__init__(self, *args, **kwargs)
        self._exc = exc

    def __str__(self):
        return 'Error importing formatter: {0}'.format(self._exc)


class BadFormatterError(RtShellError):
    '''The imported formatter is bad (most likely not a function).'''
    def __init__(self, fun, *args, **kwargs):
        super(BadFormatterError, self).__init__(self, *args, **kwargs)
        self._fun = fun

    def __str__(self):
        return 'Bad formatter: {0}'.format(self._fun)


class MissingPOAError(RtShellError):
    '''A data type from a module was used without a matching POA loaded.'''
    def __init__(self, mod, *args, **kwargs):
        super(MissingPOAError, self).__init__(self, *args, **kwargs)
        self._mod = mod

    def __str__(self):
        return 'Missing POA module: {0}'.format(self._mod)


# vim: tw=79

