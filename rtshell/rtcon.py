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

Implementation of the command to connect two ports.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def connect_ports(paths, options, tree=None):
    '''connect_ports

    This should raise exception:

    >>> connect_ports([
    ...   ('Std0.rtc', '/localhost/local.host_cxt/Std0.rtc'),
    ...   ('Output0.rtc:out', '/localhost/local.host_cxt/Output0.rtc:out')
    ... ], {})
    Traceback (most recent call last):
    ...
    NoSourcePortError: No source port specified.

    >>> connect_ports([
    ...   ('Std0.rtc:in', '/localhost/local.host_cxt/Std0.rtc:in'),
    ...   ('Output0.rtc', '/localhost/local.host_cxt/Output0.rtc')
    ... ], {})
    Traceback (most recent call last):
    ...
    NoDestPortError: No destination port specified.
    '''
    cmd_paths, fps = list(zip(*paths))
    pathports = [rtctree.path.parse_path(fp) for fp in fps]
    for ii, p in enumerate(pathports):
        if not p[1]:
            if ii == 0:
                raise rts_exceptions.NoSourcePortError(cmd_paths[ii])
            else:
                raise rts_exceptions.NoDestPortError(cmd_paths[ii])
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

    conn_name = options.name if options.name else None

    if options.no_dups:
        for p in port_objs:
            if p.get_connection_by_name(conn_name):
                raise rts_exceptions.DuplicateConnectionNameError(conn_name,
                                                                  p.name)
            if options.id:
                if p.get_connection_by_id(options.id):
                    raise rts_exceptions.DuplicateConnectionIDError(options.id)
        if port_objs[0].get_connections_by_dests(port_objs[1:]):
            raise rts_exceptions.DuplicateConnectionError(cmd_paths)

    port_objs[0].connect(port_objs[1:], name=conn_name, id=options.id,
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
            print('{0}: Warning: duplicate property: {1}'.format(sys.argv[0],
                option_value), file=sys.stderr)
        getattr(parser.values, option.dest)[key] = value

    usage = '''Usage: %prog [options] <path 1> <path 2> [<path 3> ...]
Connect two or more ports.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-d', '--no-duplicates', dest='no_dups',
            action='store_true', help='Prevent duplicate connections')
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
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    if not getattr(options, 'properties'):
        setattr(options, 'properties', {})

    if not args:
        # If no paths given then can't do anything.
        print('{0}: No ports specified.'.format(os.path.basename(sys.argv[0])),
                file=sys.stderr)
        return 1
    paths = [(p, path.cmd_path_to_full_path(p)) for p in args]

    try:
        connect_ports(paths, options, tree=tree)
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
