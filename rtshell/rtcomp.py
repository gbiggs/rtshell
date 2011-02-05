#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2011
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of the compose-components command.

'''


import optparse
import os
import rtctree.exceptions
import rtctree.path
import rtctree.tree
import rtctree.utils
import sys
import traceback

import path
import rtmgr
import rts_exceptions
import rtshell


def get_paths(comps, ports):
    comp_paths = []
    port_paths = []
    for c in comps:
        fp = path.cmd_path_to_full_path(c)
        c_path, c_port = rtctree.path.parse_path(fp)
        if c_port:
            raise rts_exceptions.NotAComponentError(c)
        comp_paths.append((fp, c_path))
    for p in ports:
        fp = path.cmd_path_to_full_path(p)
        p_path, p_port = rtctree.path.parse_path(fp)
        if not p_port:
            raise rts_exceptions.NotAPortError((p_path, p_port))
        cp = fp[:fp.rfind(':')]
        if (cp, p_path) not in comp_paths:
            comp_paths.append((cp, p_path))
        port_paths.append((cp, p_path, p_port))
    return comp_paths, port_paths


def get_comp_objs(paths, tree):
    cs = {}
    for fp, pp in paths:
        c = tree.get_node(pp)
        if not c:
            raise rts_exceptions.NoSuchObjectError(pp)
        if not c.is_component:
            raise rts_exceptions.NotAComponentError(pp)
        cs[fp] = c
    return cs


def get_port_objs(paths, comps, tree):
    ps = []
    for cp, path, port_name in paths:
        c = comps[cp]
        p = c.get_port_by_name(port_name)
        if not p:
            raise rts_exceptions.PortNotFoundError(cp, port_name)
        ps.append(p)
    return ps


def make_comp_opts(comps):
    res = ''
    for k in comps:
        res += '{0},'.format(comps[k].instance_name)
    # Remove the trailing comma
    return res[:-1]


def make_port_opts(ports):
    res = ''
    for p in ports:
        res += '{0}.{1},'.format(p.owner.instance_name, p.name)
    # Remove the trailing comma
    return res[:-1]


def get_mgr(cmd_path, full_path, comps, tree):
    def has_comp(mgr, inst_name):
        for c in mgr.components:
            if c.instance_name == inst_name:
                return True
        return False

    tree_, mgr = rtmgr.get_manager(cmd_path, full_path, tree)
    if not mgr:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    # Check that each component is in this manager
    for k in comps:
        if not has_comp(mgr, comps[k].instance_name):
            raise rts_exceptions.NotInManagerError(comps[k].instance_name)
    return mgr


def make_composite(mgr_path, mgr_full_path, comps, ports, options, tree=None):
    # Parse all paths
    comp_paths, port_paths = get_paths(comps, ports)
    # Make a tree
    if not tree:
        mgr_parse_path, port = rtctree.path.parse_path(mgr_full_path)
        paths = [y for x, y in comp_paths]
        tree = rtctree.tree.RTCTree(paths=paths,
                filter=paths + [mgr_parse_path])
    # Find all components
    comp_objs = get_comp_objs(comp_paths, tree)
    # Find all ports
    port_objs = get_port_objs(port_paths, comp_objs, tree)
    # Build the component options
    comp_opts = make_comp_opts(comp_objs)
    port_opts = make_port_opts(port_objs)
    # Find the manager (making sure there's only one)
    mgr = get_mgr(mgr_path, mgr_full_path, comp_objs, tree)
    # Call the manager to create the composite component
    mgr.create_component('{0}?&instance_name={1}&conf.default.members={2}&conf.default.exported_ports={3}{4}'.format(options.type,
        options.name, comp_opts, port_opts, options.options))


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <Manager>
Compose multiple components into a single component.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--comp', dest='comps', action='append',
            type='string', default=[], help='Component to include in the '\
            'composite component without exporting any ports. Specify this '\
            'option multiple times to add multiple components.')
    parser.add_option('-n', '--name', dest='name', action='store',
            type='string', default='CompositeRTC',
            help='Instance name of the new component. [Default: %default]')
    parser.add_option('-o', '--options', dest='options', action='store',
            type='string', default='', help='Extra options to pass to the '\
            'component on creation. Must begin with an "&"')
    parser.add_option('-p', '--port', dest='ports', action='append',
            type='string', default=[], help='Port to export from the '\
            'composite component. All components with exported ports are '\
            'automatically included in the composite component.')
    parser.add_option('-t', '--type', dest='type', action='store',
            type='string', default='PeriodicECSharedComposite',
            help='Type of composite component to create. [Default: %default]')
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

    if len(args) != 1:
        print >>sys.stderr, '{0}: No manager specified.'.format(sys.argv[0])
        return 1
    full_path = path.cmd_path_to_full_path(args[0])

    try:
        make_composite(args[0], full_path, options.comps,
                options.ports, options, tree=tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1
    return 0


# vim: tw=79

