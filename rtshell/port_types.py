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

Classes and functions for managing port types.

'''


import inspect
import re
import rtctree.path

import comp_mgmt
import rts_exceptions


###############################################################################
## Class for managing port specifications.

class PortSpec(object):
    def __init__(self, name, type, target, input=True, *args, **kwargs):
        super(PortSpec, self).__init__()
        self._name = name
        self._type = type
        self._target = target
        self._input = input

    def __str__(self):
        if self.input:
            port_dir = '>'
        else:
            port_dir = '<'
        return '{0}{1}{2}'.format(rtctree.path.format_path(self.target),
                port_dir, self.name)

    @property
    def name(self):
        '''The name of the port.'''
        return self._name

    @property
    def type(self):
        '''The port's data type constructor function.'''
        return self._type

    @property
    def target(self):
        '''The target port of this port, as (path, port_name).'''
        return self._target

    @property
    def input(self):
        '''If the port is an input port or not.'''
        return self._input

    @property
    def output(self):
        '''If the port is an output port or not.'''
        return not self._input


###############################################################################
## Functions for building port specifications.

def find_port_cons(class_name, mods):
    '''Search for a class in a list of modules and return its constructor.

    The first matching class's constructor is returned.

    @param type_name The name of the class to search for.
    @mods A list of user_mod.Module objects.

    '''
    for m in mods:
        types = [member for member in inspect.getmembers(m.mod, 
            inspect.isclass) if member[0] == class_name]
        if len(types) == 0:
            continue
        elif len(types) != 1:
            raise rts_exceptions.AmbiguousTypeError(type_name)
        else:
            return types[0][1]
    raise rts_exceptions.TypeNotFoundError(class_name)


def make_port_specs(ports, mods, tree):
    '''Create a list of PortSpec objects matching the ports given.

    The ports are searched for in the given RTCTree, and PortSpec objects are
    created matching them. The component holding each port is found, then the
    port object matching the given port name is found. A PortSpec is given
    matching its data type and with the reverse direction. If the target port
    is an InPort, a PortSpec for an OutPort will be created, and vice versa.

    @param ports The paths to the target ports. Each must be a tuple of
                 (path, port, name) where path is a list of path components in
                 the format used by rtctree.
    @param tree An RTCTree to search for the ports in.

    '''
    result = []
    index = 0
    for (rtc, port, name) in ports:
        port_obj = comp_mgmt.find_port(rtc, port, tree)
        if port_obj.porttype == 'DataInPort':
            input = False
        elif port_obj.porttype == 'DataOutPort':
            input = True
        else:
            raise rts_exceptions.BadPortTypeError(rtc, port)
        if name is None:
            if input:
                name = 'input{0}'.format(index)
            else:
                name = 'output{0}'.format(index)
        port_cons = find_port_cons(port_obj.properties['dataport.data_type'],
                mods)
        result.append(PortSpec(name, port_cons, (rtc, port), input))
        index += 1
    return result


def parse_targets(targets):
    '''Parse target ports, as specified on the command line.

    Parses target ports specified onto the command line into a tuple of
    (path, port, name), where path is in the rtctree format.

    @param targets A list of target ports, as strings. Each string should
                   be in the format "path:port>name", e.g.
                   "/localhost/blurg.host_cxt/comp0.rtc:input>stuff". The name
                   component is optional; if it is not present, neither should
                   the '>' character be.

    '''
    regex = re.compile(r'(?P<path>[:\w/.]+)(?:>(?P<name>\w+))?')
    result = []
    for t in targets:
        m = regex.match(t)
        if not m:
            raise rts_exceptions.BadPortSpecError(t)
        raw_path, name = m.groups()
        path, port = rtctree.path.parse_path(raw_path)
        if not port or not path[-1]:
            raise rts_exceptions.BadPortSpecError(t)
        result.append((path, port, name))
    return result


def require_all_input(port_specs):
    '''Checks that all ports in the specification are inputs.

    Raises a @ref PortNotInputError exception if any ports are output.

    @param port_specs A list of @ref PortSpec objects.

    '''
    for p in port_specs:
        if not p.input:
            raise rts_exceptions.PortNotInputError(p.name)


def require_all_output(port_specs):
    '''Checks that all ports in the specification are outputs.

    Raises a @ref PortNotOutputError exception if any ports are output.

    @param port_specs A list of @ref PortSpec objects.

    '''
    for p in port_specs:
        if not p.output:
            raise rts_exceptions.PortNotOutputError(p.name)

