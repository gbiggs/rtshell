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

Classes and functions for managing port types.

'''


import re
import rtctree.path

from rtshell import comp_mgmt
from rtshell import fmt
from rtshell import rts_exceptions


###############################################################################
## Class for managing port specifications.

class PortSpec(object):
    def __init__(self, name, type, target, input=True, formatter=None,
            type_name='', raw='', *args, **kwargs):
        super(PortSpec, self).__init__()
        self._formatter = formatter
        self._input = input
        self._name = name
        self._raw_specs = [raw]
        self._targets = [target]
        self._type = type
        self._type_name = type_name

    def __str__(self):
        if self._formatter:
            fmt_str = '#{0}'.format(self._formatter)
        else:
            fmt_str = ''
        result = ''
        for t in self._targets:
            result += '{0}.{1}{2},'.format(rtctree.path.format_path(t),
                    self._name, fmt_str)
        return result[:-1]

    @property
    def formatter(self):
        '''Get the port's formatter function.'''
        return self._formatter

    @property
    def input(self):
        '''If the port is an input port or not.'''
        return self._input

    @property
    def name(self):
        '''The name of the port.'''
        return self._name

    @property
    def output(self):
        '''If the port is an output port or not.'''
        return not self._input

    @property
    def raw(self):
        '''The raw port specifications that created this PortSpec.'''
        return self._raw_specs

    @property
    def targets(self):
        '''The target ports of this port, as [(path, port_name), ...].'''
        return self._targets

    @property
    def type(self):
        '''The port's data type constructor function.'''
        return self._type

    @property
    def type_name(self):
        '''The port's data type name.'''
        return self._type_name

    def add_target(self, target, raw=''):
        '''Add an additional target for this port.'''
        self._targets.append(target)
        self._raw_specs.append(raw)


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
    result = {}
    index = 0
    for (rtc, port, name, form, raw) in ports:
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
            index += 1
        data_type = port_obj.properties['dataport.data_type']
        # Strip the IDL header and version if present
        if data_type.startswith('IDL:'):
            data_type = data_type[4:]
        colon = data_type.rfind(':')
        if colon != -1:
            data_type = data_type[:colon]
        port_cons = modmgr.find_class(data_type)
        if form:
            # Look up the formatter in one of the user-provided modules
            formatter = fmt.import_formatter(form, modmgr)
        else:
            formatter = None
        if name in result:
            # Already have a port with this name so add a target
            if (input != result[name].input or
                    port_cons != result[name].type or
                    formatter != result[name].formatter):
                raise rts_exceptions.SameNameDiffSpecError(raw)
            result[name].add_target((rtc, port), raw=raw)
        else:
            result[name] = (PortSpec(name, port_cons, (rtc, port), input=input,
                formatter=formatter,
                type_name=port_obj.properties['dataport.data_type'], raw=raw))
    return list(result.values())


def parse_targets(targets):
    '''Parse target ports, as specified on the command line.

    Parses target ports specified onto the command line into a tuple of
    (path, port, name, formatter, target), where path is in the rtctree
    format.

    @param targets A list of target ports, as strings. Each string should
                   be in the format "path:port.name#formatter", e.g.
                   "/localhost/blurg.host_cxt/comp0.rtc:input.stuff#print_stuff".
                   The name component is optional; if it is not present,
                   neither should the '.' character be. The formatter
                   component is optional; if it is not present, neither
                   should the '#' character be. A name is not required
                   to use a formatter.

    '''
    regex = re.compile(r'^(?P<path>[:\-\w/.\(\)]+?)(?:\.(?P<name>\w+))?(?:#(?P<form>[\w.]+))?$')
    result = []
    for t in targets:
        m = regex.match(t)
        if not m:
            raise rts_exceptions.BadPortSpecError(t)
        raw_path, name, formatter = m.groups()
        path, port = rtctree.path.parse_path(raw_path)
        if not port or not path[-1]:
            raise rts_exceptions.BadPortSpecError(t)
        result.append((path, port, name, formatter, t))
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

