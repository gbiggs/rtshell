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

Implementation of the compose-components command.

'''


import optparse
import os
import rtctree.exceptions
import rtctree.path
import rtctree.tree
import rtctree.utils
import sys

import rtshell
import rtshell.path
import rtshell.rtmgr


def get_paths(comps, ports):
    comp_paths = []
    port_paths = []
    for c in comps:
        fp = rtshell.path.cmd_path_to_full_path(c)
        c_path, c_port = rtctree.path.parse_path(fp)
        if c_port:
            print >>sys.stderr, '{0}: Object is not a component: {1}'.format(
                    sys.argv[0], c)
            return 1
        comp_paths.append((fp, c_path))
    for p in ports:
        fp = rtshell.path.cmd_path_to_full_path(p)
        p_path, p_port = rtctree.path.parse_path(fp)
        if not p_port:
            print >>sys.stderr, '{0}: Object is not a port: {1}'.format(
                    sys.argv[0], p)
            return 1
        cp = fp[:fp.rfind(':')]
        if (cp, p_path) not in comp_paths:
            comp_paths.append((cp, p_path))
        port_paths.append((cp, fp, p_path, p_port))
    return comp_paths, port_paths


def get_comp_objs(paths, tree):
    cs = {}
    for fp, pp in paths:
        c = tree.get_node(pp)
        if not c:
            raise rts_exceptions.NoObjectAtPathError(fp)
        if not c.is_component:
            raise rts_exceptions.NotAComponentError(fp)
        cs[fp] = c
    return cs


def get_port_objs(paths, comps, tree):
    ps = []
    for cp, fp, path, port_name in paths:
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

    tree_, mgr = rtshell.rtmgr.get_manager(cmd_path, full_path, tree)
    if not mgr:
        return None
    # Check that each component is in this manager
    for k in comps:
        if not has_comp(mgr, comps[k].instance_name):
            print >>sys.stderr, '{0}: {1} is not in the manager.'.format(
                    sys.argv[0], comps[k].instance_name)
            return None
    return mgr


def make_composite(mgr_path, mgr_full_path, comps, ports, options, tree=None):
    # Parse all paths
    comp_paths, port_paths = get_paths(comps, ports)
    # Make a tree
    if not tree:
        mgr_parse_path, port = rtctree.path.parse_path(mgr_full_path)
        paths = [y for x, y in comp_paths]
        tree = rtctree.tree.create_rtctree(paths=paths,
                filter=paths + [mgr_parse_path])
    if not tree:
        return 1
    # Find all components
    comp_objs = get_comp_objs(comp_paths, tree)
    # Find all ports
    port_objs = get_port_objs(port_paths, comp_objs, tree)
    # Build the component options
    comp_opts = make_comp_opts(comp_objs)
    port_opts = make_port_opts(port_objs)
    # Find the manager (making sure there's only one)
    mgr = get_mgr(mgr_path, mgr_full_path, comp_objs, tree)
    if not mgr:
        return 1
    # Call the manager to create the composite component
    mgr.create_component('{0}?&instance_name={1}&conf.default.members={2}&conf.default.exported_ports={3}'.format(options.type,
        options.name, comp_opts, port_opts))
    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <Manager>
Compose multiple components into a single component.

''' + rtshell.RTSH_PATH_USAGE + '''

Ports are specified at the end of each path, preceeded by a colon (:).
'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-c', '--comp', dest='comps', action='append',
            type='string', default=[], help='Component to include in the '\
            'composite component without exporting any ports. Specify this '\
            'option multiple times to add multiple components.')
    parser.add_option('-n', '--name', dest='name', action='store',
            type='string', default='CompositeRTC',
            help='Instance name of the new component. [Default: %default]')
    parser.add_option('-p', '--port', dest='ports', action='append',
            type='string', default=[], help='Port to export from the '\
            'composite component. All components with exported ports are '\
            'automatically included in the composite component.')
    parser.add_option('-t', '--type', dest='type', action='store',
            type='string', default='PeriodicECSharedComposite',
            help='Type of composite component to create. [Default: %default]')

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
    full_path = rtshell.path.cmd_path_to_full_path(args[0])

    try:
        return make_composite(args[0], full_path, options.comps,
                options.ports, options, tree=tree)
    except rtctree.exceptions.RtcTreeError, e:
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1


# vim: tw=79

