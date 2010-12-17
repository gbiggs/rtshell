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

Implementation of the command to connect two ports.

'''


import optparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions
import rtshell


def connect_ports(source_cmd_path, source_full_path,
                  dest_cmd_path, dest_full_path,
                  options, tree=None):
    source_path, source_port = rtctree.path.parse_path(source_full_path)
    if not source_port:
        raise rts_exceptions.NoSourcePortError
    if not source_path[-1]:
        raise rts_exceptions.NoSuchObjectError(source_cmd_path)

    dest_path, dest_port = rtctree.path.parse_path(dest_full_path)
    if not dest_port:
        raise rts_exceptions.NoDestPortError
    if not dest_path[-1]:
        raise rts_exceptions.NoSuchObjectError(dest_cmd_path)

    if not tree:
        tree = rtctree.tree.create_rtctree(paths=[source_path, dest_path],
                filter=[source_path, dest_path])

    if not tree.has_path(source_path):
        raise rts_exceptions.NoSuchObjectError(source_cmd_path)
    if not tree.has_path(dest_path):
        raise rts_exceptions.NoSuchObjectError(dest_cmd_path)

    source_comp = tree.get_node(source_path)
    if not source_comp:
        raise rts_exceptions.NoSuchObjectError(source_cmd_path)
    if not source_comp.is_component:
        raise rts_exceptions.NotAComponentError(source_cmd_path)
    source_port_obj = source_comp.get_port_by_name(source_port)
    if not source_port_obj:
        raise rts_exceptions.PortNotFoundError(source_path, source_port)
    dest_comp = tree.get_node(dest_path)
    if not dest_comp:
        raise rts_exceptions.NoSuchObjectError(dest_cmd_path)
    if not dest_comp.is_component:
        raise rts_exceptions.NotAComponentError(dest_cmd_path)
    dest_port_obj = dest_comp.get_port_by_name(dest_port)
    if not dest_port_obj:
        raise rts_exceptions.PortNotFoundError(dest_path, dest_port)

    conn_name = options.name if options.name else None
    source_port_obj.connect(dest_port_obj, name=conn_name, id=options.id,
                            props=options.properties)


def main(argv=None, tree=None):
    def property_callback(option, opt, option_value, parser):
        if option_value.count('=') != 1:
            raise optparse.OptionValueError('Bad property format: {0}'.format(
                option_value))
        key, equals, value = option_value.partition('=')
        if not getattr(parser.values, option.dest):
            setattr(parser.values, option.dest, {})
        if key in getattr(parser.values, option.dest):
            print >>sys.stderr, '{0}: Warning: duplicate property: {1}'.format(
                    sys.argv[0], option_value)
        getattr(parser.values, option.dest)[key] = value

    usage = '''Usage: %prog [options] <source path> <destination path>
Connect two ports.

''' + rtshell.RTSH_PATH_USAGE + '''

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
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-i', '--id', dest='id', action='store', type='string',
            default='', help='ID of the connection. [Default: %default]')
    parser.add_option('-n', '--name', dest='name', action='store',
            type='string', default=None,
            help='Name of the connection. [Default: %default]')
    parser.add_option('-p', '--property', dest='properties', action='callback',
            callback=property_callback, type='string',
            help='Connection properties.')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not getattr(options, 'properties'):
        setattr(options, 'properties', {})

    if len(args) != 2:
        print >>sys.stderr, usage
        return 1
    else:
        source_path = args[0]
        dest_path = args[1]
    source_full_path = path.cmd_path_to_full_path(source_path)
    dest_full_path = path.cmd_path_to_full_path(dest_path)

    try:
        connect_ports(source_path, source_full_path, dest_path, dest_full_path,
                options, tree=tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

