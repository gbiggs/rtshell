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

Implementation of the command to disconnect ports.

'''


import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions
import rtshell


def disconnect_all(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if not path[-1]:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if not tree:
        tree = rtctree.tree.create_rtctree(paths=path, filter=[path])

    object = tree.get_node(path)
    if not object:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if not object.is_component:
        raise rts_exceptions.NotAComponentError(cmd_path)

    if port:
        # Disconnect a single port
        port_obj = object.get_port_by_name(port)
        if not port_obj:
            raise rts_exceptions.PortNotFoundError(path, port)
        if options.id:
            conn = port_obj.get_connection_by_id(options.id)
            if not conn:
                raise rts_exceptions.ConnectionIDNotFoundError(options.id,
                        cmd_path)
            conn.disconnect()
        else:
            port_obj.disconnect_all()
    else:
        if options.id:
            # Hunt through the ports for the connection ID
            for p in object.ports:
                conn = p.get_connection_by_id(options.id)
                if not conn:
                    continue
                conn.disconnect()
                return
            raise rts_exceptions.ConnectionIDNotFoundError(options.id,
                    cmd_path)
        else:
            # Disconnect all ports
            object.disconnect_all()


def disconnect_ports(source_cmd_path, source_full_path,
                  dest_cmd_path, dest_full_path,
                  options, tree=None):
    source_path, source_port = rtctree.path.parse_path(source_full_path)
    if not source_port:
        raise rts_exceptions.NoSourcePortError

    dest_path, dest_port = rtctree.path.parse_path(dest_full_path)
    if not dest_port:
        raise rts_exceptions.NoDestPortError

    if not tree:
        tree = rtctree.tree.create_rtctree(paths=[source_path, dest_path],
                filter=[source_path, dest_path])

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

    if options.id:
        s_conn = source_port_obj.get_connection_by_id(options.id)
        d_conn = dest_port_obj.get_connection_by_id(options.id)
        if not s_conn:
            raise rts_exceptions.ConnectionIDNotFoundError(options.id,
                    source_cmd_path)
        elif not d_conn:
            raise rts_exceptions.ConnectionIDNotFoundError(options.id,
                    dest_cmd_path)
        conn = s_conn
    else:
        conn = source_port_obj.get_connection_by_dest(dest_port_obj)
        if not conn:
            raise rts_exceptions.ConnectionNotFoundError(source_cmd_path,
                    dest_cmd_path)

    conn.disconnect()


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <source path> [destination path]
Remove a connection between two ports, or all connections from a component or
port.

''' + rtshell.RTSH_PATH_USAGE + '''

Ports are specified at the end of each path, preceeded by a colon (:).'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-i', '--id', dest='id', action='store', type='string',
            default='', help='ID of the connection.')
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

    try:
        if len(args) == 1:
            # Disconnect all
            cmd_path = args[0]
            disconnect_all(cmd_path, path.cmd_path_to_full_path(cmd_path),
                                  options, tree)
        elif len(args) == 2:
            # Disconnect a pair of ports
            source_path = args[0]
            dest_path = args[1]
            source_full_path = path.cmd_path_to_full_path(source_path)
            dest_full_path = path.cmd_path_to_full_path(dest_path)
            disconnect_ports(source_path, source_full_path,
                                 dest_path, dest_full_path,
                                 options, tree)
        else:
            print >>sys.stderr, usage
            return 1
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0



# vim: tw=79

