#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtcshell

Copyright (C) 2009-2010
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

File: rtcon

Implementation of the command to connect two ports.

'''

__version__ = '$Revision: $'
# $Source$


from optparse import OptionParser, OptionError, OptionValueError
import os
from rtctree.exceptions import RtcTreeError, FailedToConnectError, \
                               IncompatibleDataPortConnectionPropsError, \
                               WrongPortTypeError, \
                               MismatchedInterfacesError, \
                               MismatchedPolarityError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, get_num_columns_and_rows, \
                          get_terminal_size
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def connect_ports(source_cmd_path, source_full_path,
                  dest_cmd_path, dest_full_path,
                  options, tree=None):
    source_path, source_port = parse_path(source_full_path)
    if not source_port:
        # Need a port to connect to
        print >>sys.stderr, '{0}: No source port specified'.format(sys.argv[0])
        return 1
    if not source_path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Bad source path'.format(sys.argv[0])
        return 1

    dest_path, dest_port = parse_path(dest_full_path)
    if not dest_port:
        # Need a port to connect to
        print >>sys.stderr, '{0}: No destination port \
specified'.format(sys.argv[0])
        return 1
    if not dest_path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Bad destination path'.format(sys.argv[0])
        return 1

    if not tree:
        tree = create_rtctree(paths=[source_path, dest_path])
    if not tree:
        return 1

    if not tree.has_path(source_path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], source_cmd_path)
        return 1
    if not tree.has_path(dest_path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], dest_cmd_path)
        return 1

    source_comp = tree.get_node(source_path)
    if not source_comp or not source_comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], source_cmd_path)
        return 1
    source_port_obj = source_comp.get_port_by_name(source_port)
    if not source_port_obj:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], source_cmd_path)
        return 1
    dest_comp = tree.get_node(dest_path)
    if not dest_comp or not dest_comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], dest_cmd_path)
        return 1
    dest_port_obj = dest_comp.get_port_by_name(dest_port)
    if not dest_port_obj:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], dest_cmd_path)
        return 1

    conn_name = options.name if options.name else None
    try:
        source_port_obj.connect(dest_port_obj, name=conn_name, id=options.id,
                                props=options.properties)
    except IncompatibleDataPortConnectionPropsError:
        print >>sys.stderr, '{0}: An incompatible data port property or \
property value was given.'.format(sys.argv[0])
        return 1
    except WrongPortTypeError:
        print >>sys.stderr, '{0}: Mismatched port types.'.format(sys.argv[0])
        return 1
    except MismatchedPolarityError:
        print >>sys.stderr, '{0}: Service port polarities do not \
match.'.format(sys.argv[0])
        return 1
    except MismatchedInterfacesError:
        print >>sys.stderr, '{0}: Service port interfaces do not \
match.'.format(sys.argv[0])
        return 1
    except FailedToConnectError:
        print >>sys.stderr, '{0}: Failed to connect.'.format(sys.argv[0])
        return 1
    return 0


def main(argv=None, tree=None):
    def property_callback(option, opt, option_value, parser):
        if option_value.count('=') != 1:
            raise OptionValueError('Bad property format: {0}'.format(option_value))
        key, equals, value = option_value.partition('=')
        if not getattr(parser.values, option.dest):
            setattr(parser.values, option.dest, {})
        if key in getattr(parser.values, option.dest):
            print >>sys.stderr, \
                '{0}: Warning: duplicate property: {1}'.format(sys.argv[0],
                                                               option_value)
        getattr(parser.values, option.dest)[key] = value

    usage = '''Usage: %prog [options] <source path> <destination path>
Connect two ports.

''' + RTSH_PATH_USAGE + '''

Ports are specified at the end of each path, preceeded by a colon (:).

Specify port properties in the format 'property=value'. For example, to set the
flow type of the port, you would use '--property dataport.dataflow_type=pull'.

For data ports, the valid properties include:
dataport.data_type
dataport.dataflow_type
dataport.interface_type
dateport.subscription_type

For service ports, the valid properties include:
port.port_type

Other properties may also be valid, depending on your OpenRTM
implementation.'''
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('-i', '--id', dest='id', action='store', type='string',
            default='', help='ID of the connection. [Default: %default]')
    parser.add_option('-n', '--name', dest='name', action='store',
            type='string', default=None,
            help='Name of the connection. [Default: %default]')
    parser.add_option('-p', '--property', dest='properties', action='callback',
            callback=property_callback, type='string',
            help=\
'''Connection properties. ''')

    if argv:
        sys.argv = argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if not getattr(options, 'properties'):
        setattr(options, 'properties', {})

    if len(args) != 2:
        print >>sys.stderr, usage
        return 1
    else:
        source_path = args[0]
        dest_path = args[1]
    source_full_path = cmd_path_to_full_path(source_path)
    dest_full_path = cmd_path_to_full_path(dest_path)

    return connect_ports(source_path, source_full_path,
                         dest_path, dest_full_path,
                         options, tree)


# vim: tw=79

