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

Exceptions that may occur.

'''


import rtctree.path


class RtShellError(Exception):
    '''Base error for all errors that may occur.'''
    pass


class CallFailedError(Exception):
    '''An interface call failed.'''
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return 'Interface call failed: {0}'.format(self._msg)


class RequiredActionFailedError(RtShellError):
    '''Error raised when an action that must succeed fails.'''
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return 'Required action failed: {0}'.format(self._msg)


class PrecedingTimeoutError(RtShellError):
    '''The time limit on a preceding condition being met has elapsed.'''
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return 'Preceding condition timed out: {0}'.format(self._msg)


class PlanExecutionError(RtShellError):
    '''An error occurred executing a plan.'''
    def __init__(self, error):
        self._error = error

    def __str__(self):
        return 'Error executing plan:\n{0}'.format(self._error)


class EmptyConstExprError(RtShellError):
    '''A constant expression that should be evaluated is empty.'''
    def __str__(self):
        return 'Empty constant expression '


class AmbiguousTypeError(RtShellError):
    '''A data type is ambiguous.'''
    def __init__(self, type):
        self._type = type

    def __str__(self):
        return 'Ambiguous port type: {0}'.format(self._type)


class TypeNotFoundError(RtShellError):
    '''A data type was not found.'''
    def __init__(self, type):
        self._type = type

    def __str__(self):
        return 'Type not found: {0}'.format(self._type)


class BadPortSpecError(RtShellError):
    '''A port specification is badly formatted.'''
    def __init__(self, ps):
        self._ps = ps

    def __str__(self):
        return 'Bad port specification: {0}'.format(self._ps)


class SameNameDiffSpecError(RtShellError):
    '''A port spec has a different property from another with the same name.'''
    def __init__(self, ps):
        self._ps = ps

    def __str__(self):
        return 'Port specification with same name has different properties: '\
                '{0}'.format(self._ps)


class NoSuchObjectError(RtShellError):
    '''The given path does not point to the necessary object.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'No such object: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'No such object: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'No such object: {0}'.format(self._path)


class NotAComponentOrManagerError(RtShellError):
    '''A given path is not a component nor a manager.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a component or manager: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a component or manager: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a component or manager: {0}'.format(self._path)


class NotAComponentError(RtShellError):
    '''A given path is not a component.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a component: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a component: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a component: {0}'.format(self._path)


class NotACompositeComponentError(RtShellError):
    '''A given path is not a composite component.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a composite component: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a composite component: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a composite component: {0}'.format(self._path)


class NotAPortError(RtShellError):
    '''A given path is not a port.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a port: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a port: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a port: {0}'.format(self._path)


class ParentNotADirectoryError(RtShellError):
    '''A given path's parent is not a directory.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Parent not a directory: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Parent not a directory: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Parent not a directory: {0}'.format(self._path)


class NotADirectoryError(RtShellError):
    '''A given path is not a directory.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a directory: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a directory: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a directory: {0}'.format(self._path)


class NotAPortError(RtShellError):
    '''A given path is not a port.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a port: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a port: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a port: {0}'.format(self._path)


class NotAManagerError(RtShellError):
    '''A given path is not a manager.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a manager: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a manager: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a manager: {0}'.format(self._path)


class NotInManagerError(RtShellError):
    '''A component name does not exist in a manager.'''
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return '{0} is not in the manager.'.format(self._name)


class UndeletableObjectError(RtShellError):
    '''Some objects cannot be deleted.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Undeletable object: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Undeletable object: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Undeletable object: {0}'.format(self._path)


class NotZombieObjectError(RtShellError):
    '''A given path does not point to a zombie.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Not a zombie object: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Not a zombie object: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Not a zombie object: {0}'.format(self._path)


class ZombieObjectError(RtShellError):
    '''A given path points to a zombie.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Zombie object: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Zombie object: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Zombie object: {0}'.format(self._path)


class UnknownObjectError(RtShellError):
    '''A given path points to an unknown object.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'Unknown object: {0}'.format(
                    rtctree.path.format_path(self._path))
        elif type(self._path) == list:
            return 'Unknown object: {0}'.format(
                    rtctree.path.format_path((self._path, None)))
        else:
            return 'Unknown object: {0}'.format(self._path)


class NoDestPortError(RtShellError):
    '''A required destination port was not specified.'''
    def __str__(self):
        return 'No destination port specified.'


class NoSourcePortError(RtShellError):
    '''A required source port was not specified.'''
    def __str__(self):
        return 'No source port specified.'


class CannotDoToPortError(RtShellError):
    '''The action cannot be performed on a port.'''
    def __init__(self, action):
        self._action = action

    def __str__(self):
        return 'Cannot {0} ports.'.format(self._action)


class PortNotFoundError(RtShellError):
    '''The port was not found on the component.'''
    def __init__(self, rtc, port):
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Port not found: {0}'.format(
                rtctree.path.format_path((self._rtc, self._port)))


class ConnectionNotFoundError(RtShellError):
    '''A connection between two ports was not found.'''
    def __init__(self, path1, path2):
        self._path1 = path1
        self._path2 = path2

    def __str__(self):
        if type(self._path1) == tuple:
            path1_str = rtctree.path.format_path(self._path1)
        elif type(self._path1) == list:
            path1_str = rtctree.path.format_path((self._path1, None))
        else:
            path1_str = self._path1
        if type(self._path2) == tuple:
            path2_str = rtctree.path.format_path(self._path2)
        elif type(self._path2) == list:
            path2_str = rtctree.path.format_path((self._path2, None))
        else:
            path2_str = self._path2
        return 'No connection from {0} to {1}'.format(path1_str, path2_str)


class MultiConnectionNotFoundError(RtShellError):
    '''A connection between ports was not found.'''
    def __str__(self):
        return 'No connection found involving the specified ports.'''


class ConnectionIDNotFoundError(RtShellError):
    '''The port was not found on the component.'''
    def __init__(self, id, path):
        self._id = id
        self._path = path

    def __str__(self):
        if type(self._path) == tuple:
            return 'No connection from {0} with ID {1}'.format(
                    rtctree.path.format_path(self._path), self._id)
        elif type(self._path) == list:
            return 'No connection from {0} with ID {1}'.format(
                    rtctree.path.format_path((self._path, None)), self._id)
        else:
            return 'No connection from {0} with ID {1}'.format(self._path,
                    self._id)


class DuplicateConnectionError(RtShellError):
    '''An identical connection already exists.'''
    def __init__(self, ports):
        self._ports = ports

    def __str__(self):
        return 'An identical connection already exists between ports {}'.format(
            self._ports)


class DuplicateConnectionIDError(RtShellError):
    '''A connection with that ID already exists.'''
    def __init__(self, conn_id):
        self._conn_id = conn_id

    def __str__(self):
        return 'A connection with ID {} already exists between the ' \
                'specified ports'.format(self._conn_id)


class DuplicateConnectionNameError(RtShellError):
    '''A connection with that name already exists.'''
    def __init__(self, conn_name, port_name):
        self._conn_name = conn_name
        self._port_name = port_name

    def __str__(self):
        return 'A connection with name {} already exists from the ' \
                'specified port {}'.format(self._conn_name, self._port_name)


class BadPortTypeError(RtShellError):
    '''The port type is not defined.'''
    def __init__(self, rtc, port):
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Incorrect port type: {0}'.format(
                rtctree.path.format_path((self._rtc, self._port)))


class MissingCompError(RtShellError):
    '''An expected component is missing.'''
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return 'Expected component missing: {0}'.format(self._path)


class ConnectFailedError(RtShellError):
    '''An error occured connecting two ports.'''
    def __init__(self, rtc, port):
        self._rtc = rtc
        self._port = port

    def __str__(self):
        return 'Failed to connect port: {0}'.format(
                rtctree.path.format_path((self._rtc, self._port)))


class ActivateError(RtShellError):
    '''An error occured activating a component.'''
    def __init__(self, comp):
        self._comp = comp

    def __str__(self):
        return 'Error activating component: {0}'.format(self._comp)


class DeactivateError(RtShellError):
    '''An error occured deactivating a component.'''
    def __init__(self, comp):
        self._comp = comp

    def __str__(self):
        return 'Error deactivating component: {0}'.format(self._comp)


class PortNotInputError(RtShellError):
    '''A port is not an input that should be.'''
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'Port is not input: {0}'.format(self._name)


class PortNotOutputError(RtShellError):
    '''A port is not an output that should be.'''
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'Port is not output: {0}'.format(self._name)


class ImportFormatterError(RtShellError):
    '''An error occured importing a formatting function.'''
    def __init__(self, exc):
        self._exc = exc

    def __str__(self):
        return 'Error importing formatter: {0}'.format(self._exc)


class BadFormatterError(RtShellError):
    '''The imported formatter is bad (most likely not a function).'''
    def __init__(self, fun):
        self._fun = fun

    def __str__(self):
        return 'Bad formatter: {0}'.format(self._fun)


class MissingPOAError(RtShellError):
    '''A data type from a module was used without a matching POA loaded.'''
    def __init__(self, mod):
        self._mod = mod

    def __str__(self):
        return 'Missing POA module: {0}'.format(self._mod)


class NoConfSetError(RtShellError):
    '''The specified configuration set does not exist.'''
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return 'No such configuration set: {0}'.format(self._name)


class BadStartPointError(RtShellError):
    '''A given start point for the log is outside the bounds.'''
    def __str__(self):
        return 'Start time/index out of bounds.'


class BadEndPointError(RtShellError):
    '''A given end point for the log is outside the bounds.'''
    def __str__(self):
        return 'End time/index out of bounds.'


class BadLogTypeError(RtShellError):
    '''An invalid logger type was chosen.'''
    def __init__(self, type):
        self._type = type

    def __str__(self):
        return 'Invalid logger type: {0}'.format(self._type)


class UnsupportedLogTypeError(RtShellError):
    '''The selected log type doesn't support the desired feature.'''
    def __init__(self, type, feature):
        self._type = type
        self._feature = feature

    def __str__(self):
        return 'Log type "{0}" does not support feature {1}.'.format(
                self._type, self._feature)


class NoLogFileNameError(RtShellError):
    '''An expected file name was not provided.'''
    def __str__(self):
        return 'No log file specified.'


class BadMgrAddressError(RtShellError):
    '''A bad corbaloc address was given.'''
    def __str__(self):
        return 'Invalid corbaloc URL.'


class FailedToNarrowError(RtShellError):
    '''Failed to narrow a CORBA object reference.'''
    def __str__(self):
        return 'Failed to narrow CORBA object reference.'


class CannotRemoveFromNewCompositionError(RtShellError):
    '''Cannot remove components/ports from a new composition.'''
    def __str__(self):
        return 'Cannot remove components/ports from a new composition.'


# vim: tw=79

