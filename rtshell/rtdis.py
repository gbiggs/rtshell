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

File: rtdis

Implementation of the command to disconnect ports.

'''

__version__ = '$Revision: $'
# $Source$


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, get_num_columns_and_rows, \
                          get_terminal_size
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import ENV_VAR, cmd_path_to_full_path


def disconnect_all(cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if not path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Not a directory: {1}'.format(sys.argv[0],
                                                               cmd_path)
        return 1

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return 1

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], cmd_path)
        return 1

    if port:
        # Disconnect a single port
        port_obj = object.get_port_by_name(port)
        if not port_obj:
            print >>sys.stderr, '{0}: Cannot access {1}: No such \
    port'.format(sys.argv[0], cmd_path)
            return 1
        port_obj.disconnect_all()
    else:
        # Disconnect all ports
        object.disconnect_all()
        pass

    return 0


def disconnect_ports(source_cmd_path, source_full_path,
                  dest_cmd_path, dest_full_path,
                  options, tree=None):
    source_path, source_port = parse_path(source_full_path)
    if not source_port:
        # Need a port to disconnect
        print >>sys.stderr, '{0}: No source port specified'.format(sys.argv[0])
        return 1
    if not source_path[-1]:
        # Trailing slashes are bad
        print >>sys.stderr, '{0}: Bad source path'.format(sys.argv[0])
        return 1

    dest_path, dest_port = parse_path(dest_full_path)
    if not dest_port:
        # Need a port to disconnect
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

    source_comp = tree.get_node(source_path)
    if not source_comp:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], source_cmd_path)
        return 1
    if not source_comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], source_cmd_path)
        return 1
    source_port_obj = source_comp.get_port_by_name(source_port)
    if not source_port_obj:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], source_cmd_path)
        return 1
    dest_comp = tree.get_node(dest_path)
    if not dest_comp:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], dest_cmd_path)
        return 1
    if not dest_comp.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object'.format(sys.argv[0], dest_cmd_path)
        return 1
    dest_port_obj = dest_comp.get_port_by_name(dest_port)
    if not dest_port_obj:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
port'.format(sys.argv[0], dest_cmd_path)
        return 1

    conn = source_port_obj.get_connection_by_dest(dest_port_obj)
    if not conn:
        print >>sys.stderr, '{0}: No connection between {1} and \
{2}'.format(sys.argv[0], source_cmd_path, dest_cmd_path)
        return 1

    conn.disconnect()

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <source path> [destination path]
Disconnect two ports, or all connections from a component or port.

''' + RTSH_PATH_USAGE + '''

Ports are specified at the end of each path, preceeded by a colon (:).'''
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if len(args) == 1:
        # Disconnect all
        cmd_path = args[0]
        return disconnect_all(cmd_path, cmd_path_to_full_path(cmd_path),
                              options, tree)
    elif len(args) == 2:
        # Disconnect a pair of ports
        source_path = args[0]
        dest_path = args[1]
        source_full_path = cmd_path_to_full_path(source_path)
        dest_full_path = cmd_path_to_full_path(dest_path)
        return disconnect_ports(source_path, source_full_path,
                             dest_path, dest_full_path,
                             options, tree)
    else:
        print >>sys.stderr, usage
        return 1

    return 1



# vim: tw=79

