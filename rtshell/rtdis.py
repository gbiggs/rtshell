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

Implementation of the command to disconnect ports.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def disconnect_all(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if not path[-1]:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

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


def disconnect_ports(paths, options, tree=None):
    cmd_paths, fps = list(zip(*paths))
    pathports = [rtctree.path.parse_path(fp) for fp in fps]
    for ii, p in enumerate(pathports):
        if not p[1]:
            raise rts_exceptions.NotAPortError(cmd_paths[ii])
        if not p[0][-1]:
            raise rts_exceptions.NotAPortError(cmd_paths[ii])
    paths, ports = list(zip(*pathports))

    if not tree:
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)

    port_objs = []
    for ii, p in enumerate(pathports):
        obj = tree.get_node(p[0])
        if not obj:
            raise rts_exceptions.NoSuchObjectError(cmd_paths[ii])
        if obj.is_zombie:
            raise rts_exceptions.ZombieObjectError(cmd_paths[ii])
        if not obj.is_component:
            raise rts_exceptions.NotAComponentError(cmd_paths[ii])
        port_obj = obj.get_port_by_name(p[1])
        if not port_obj:
            raise rts_exceptions.PortNotFoundError(p[0], p[1])
        port_objs.append(port_obj)
    if len(port_objs) < 2:
        raise rts_exceptions.NoDestPortError

    if options.id:
        all_conns = port_objs[0].get_connections_by_dests(port_objs[1:])
        conns = []
        for c in all_conns:
            if c.id == options.id:
                conns.append(c)
    else:
        conns = port_objs[0].get_connections_by_dests(port_objs[1:])

    if not conns:
        if options.id:
            raise rts_exceptions.ConnectionIDNotFoundError(options.id,
                    cmd_paths[0])
        else:
            raise rts_exceptions.MultiConnectionNotFoundError
    for c in conns:
        c.disconnect()


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <source path> [destination path]
Remove connections.'''
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
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    try:
        if len(args) == 1:
            # Disconnect all
            cmd_path = args[0]
            disconnect_all(cmd_path, path.cmd_path_to_full_path(cmd_path),
                                  options, tree)
        elif len(args) > 1:
            # Disconnect a set of ports
            paths = [(p, path.cmd_path_to_full_path(p)) for p in args]
            disconnect_ports(paths, options, tree)
        else:
            print(usage, file=sys.stderr)
            return 1
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), e),
                file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

