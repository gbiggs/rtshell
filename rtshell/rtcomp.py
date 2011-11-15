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
import SDOPackage
import SDOPackage__POA
import sys
import traceback

import path
import rtmgr
import rts_exceptions
import rtshell


def parse_member_paths(source_paths):
    paths = []
    for p in source_paths:
        ports = []
        split = p.split(':')
        if len(split) == 2:
            p = split[0]
            ports = split[1].split(',')
        elif len(split) > 2:
            raise rtctree.exceptions.BadPathError(p)
        fp = path.cmd_path_to_full_path(p)
        c_path, ignored = rtctree.path.parse_path(fp)
        paths.append((p, c_path, ports))
    return paths


def get_comp_objs(paths, tree):
    objs = {}
    for fp, cp, ports in paths:
        obj = tree.get_node(cp)
        if not obj:
            raise rts_exceptions.NoSuchObjectError(fp)
        if not obj.is_component:
            raise rts_exceptions.NotAComponentError(fp)
        objs[fp] = (obj, ports)
    return objs


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
    mgr.create_component('{0}?&instance_name={1}&conf.default.members={2}&'
        'conf.default.exported_ports={3}{4}'.format(options.type,
        options.name, comp_opts, port_opts, options.options))


def create_composition(mgr, name, options, comp_type):
    if not options.startswith('&'):
        options = '&' + options
    mgr.create_component('{0}?&instance_name={1}{2}'.format(comp_type, name,
        options))
    return mgr.get_node([mgr.name, name + '.rtc'])


def add_to_composition(comp, paths, tree):
    objs = get_comp_objs(paths, tree)
    for k in objs:
        pass


def rem_from_composition(comp, paths, tree):
    paths = parse_member_paths(paths)
    objs = paths


def comp_is_empty(comp):
    return False


def manage_composition(tgt_raw_path, tgt_full_path, options, tree=None):
    # Parse paths of components to add/remove
    add_paths = parse_member_paths(options.add)
    rem_paths = parse_member_paths(options.remove)

    # The target, either a manager or a component
    tgt_path, tgt_suffix = rtctree.path.parse_path(tgt_full_path)

    # Make a tree
    if not tree:
        paths = [tgt_path] + [y for x, y, z in add_paths + rem_paths]
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)
    tgt_obj = tree.get_node(tgt_path)
    if not tgt_obj:
        raise rts_exceptions.NoSuchObjectError(tgt_raw_path)
    if tgt_obj.is_manager:
        # Create composition
        if not tgt_suffix:
            tgt_suffix = 'CompositeRTC'
        comp = create_composition(tgt_obj, tgt_suffix, options.options,
                options.type)
    elif tgt_obj.is_component:
        # Edit composition - there should be no suffix
        if tgt_suffix:
            raise rts_exceptions.NotAComponentError(tgt_raw_path)
        comp = tgt_obj
    else:
        raise rts_exceptions.NotAComponentOrManagerError(tgt_raw_path)
    print dir(comp.object)
    if add_paths:
        add_to_composition(comp, add_paths, tree)
    if rem_paths:
        rem_from_composition(comp, rem_paths, tree)
    if comp_is_empty(comp):
        destroy_composition(comp)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <manager:name|composite component path>
Manage composite components.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-a', '--add', dest='add', action='append',
            type='string', default=[], help='A component to include in the '
            'composition. Specify a comma-separated list of ports to export '
            'after the component name, separated by a colon.')
    parser.add_option('-o', '--options', dest='options', action='store',
            type='string', default='', help='Extra options to pass to the '\
            'component on creation. Must begin with an "&"')
    parser.add_option('-r', '--remove', dest='remove', action='append',
            type='string', default=[], help='A component to remove from the '
            'composition. All exported ports belonging to the component will '
            'be removed.')
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
        print >>sys.stderr, '{0}: No manager or existing composite component '\
            'specified.'.format(sys.argv[0])
        return 1
    full_path = path.cmd_path_to_full_path(args[0])

    try:
        manage_composition(args[0], full_path, options, tree=tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
        return 1
    return 0


# vim: tw=79

