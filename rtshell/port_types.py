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


import re
import rtctree.path

import comp_mgmt
import fmt
import rts_exceptions


###############################################################################
## Class for managing port specifications.

class PortSpec(object):
    def __init__(self, name, type, target, input=True, formatter=None, *args,
            **kwargs):
        super(PortSpec, self).__init__()
        self._name = name
        self._type = type
        self._target = target
        self._input = input
        self._formatter = formatter

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

    @property
    def formatter(self):
        '''Get the port's formatter function.'''
        return self._formatter


###############################################################################
## Functions for building port specifications.

def make_port_specs(ports, modmgr, tree):
    '''Create a list of PortSpec objects matching the ports given.

    The ports are searched for in the given RTCTree, and PortSpec objects are
    created matching them. The component holding each port is found, then the
    port object matching the given port name is found. A PortSpec is given
    matching its data type and with the reverse direction. If the target port
    is an InPort, a PortSpec for an OutPort will be created, and vice versa.

    @param ports The paths to the target ports. Each must be a tuple of
                 (path, port, name, formatter) where path is a list of path
                 components in the format used by rtctree.
    @param modmgr The ModuleMgr object to use to evaluate the format
                  expression.
    @param tree An RTCTree to search for the ports in.

    '''
    result = []
    index = 0
    for (rtc, port, name, form) in ports:
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
        port_cons = modmgr.find_class(port_obj.properties['dataport.data_type'])
        if form:
            # Look up the formatter in one of the user-provided modules
            formatter = fmt.import_formatter(form, modmgr)
        else:
            formatter = None
        result.append(PortSpec(name, port_cons, (rtc, port), input=input,
            formatter=formatter))
        index += 1
    return result


def parse_targets(targets):
    '''Parse target ports, as specified on the command line.

    Parses target ports specified onto the command line into a tuple of
    (path, port, name), where path is in the rtctree format.

    @param targets A list of target ports, as strings. Each string should
                   be in the format "path:port.name#formatter", e.g.
                   "/localhost/blurg.host_cxt/comp0.rtc:input.stuff#print_stuff".
                   The name component is optional; if it is not present, neither should
                   the '.' character be. The formatter component is optional;
                   if it is not present, neither should the '#' character be. A
                   name is not required to use a formatter.

    '''
    regex = re.compile(r'^(?P<path>[:\w/.]+?)(?:\.(?P<name>\w+))?(?:#(?P<form>[\w.]+))?$')
    result = []
    for t in targets:
        m = regex.match(t)
        if not m:
            raise rts_exceptions.BadPortSpecError(t)
        raw_path, name, formatter = m.groups()
        path, port = rtctree.path.parse_path(raw_path)
        if not port or not path[-1]:
            raise rts_exceptions.BadPortSpecError(t)
        result.append((path, port, name, formatter))
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

