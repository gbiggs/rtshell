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

Implementation of the compose-components command.

'''

from __future__ import print_function


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
from functools import reduce

from rtshell import path
from rtshell import rtmgr
from rtshell import rts_exceptions
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


def get_potential_comp_objs(paths, tree):
    objs = {}
    zombies = {}
    for fp, cp, ports in paths:
        obj = tree.get_node(cp)
        if not obj:
            zombies[fp] = (cp[0], ports)
        else:
            objs[fp] = (obj, ports)
    return objs, zombies


def create_composition(mgr, name, options, comp_type):
    if not options.startswith('&'):
        options = '&' + options
    mgr.create_component('{0}?&instance_name={1}{2}'.format(comp_type, name,
        options))
    return mgr.get_node([mgr.name, name + '.rtc'])


def add_to_composition(comp, rtcs, tree, verbose):
    # Set the exported ports
    current_ports = comp.conf_sets['default'].data['exported_ports'].split(',')
    current_ports = [x for x in current_ports if x]
    new_ports = current_ports
    for rtc in rtcs:
        c = rtcs[rtc][0]
        for p in rtcs[rtc][1]:
            # Port existence check has already been done
            p_name = rtcs[rtc][0].instance_name + '.' + p
            if p_name not in new_ports:
                if verbose:
                    print('Exporting port {0} from composition'.format(p_name),
                            file=sys.stderr)
                new_ports.append(p_name)
    if new_ports:
        new_ports = reduce(lambda x, y: x + ',' + y, new_ports)
        comp.set_conf_set_value('default', 'exported_ports', new_ports)
        comp.activate_conf_set('default')
    # Add the new RTCs to the composition
    to_add = []
    for rtc in rtcs:
        c = rtcs[rtc][0]
        if not comp.is_member(c):
            if verbose:
                print('Adding component {0} to composition'.format(rtc),
                        file=sys.stderr)
            to_add.append(c)
        elif verbose and not rtcs[rtc][1]:
            # Only print this message if the component didn't have any ports to
            # add
            print('Component {0} is already in composition'.format(rtc),
                    file=sys.stderr)
    comp.add_members(to_add)


def rem_from_composition(comp, rtcs, tree, verbose):
    current_ports = comp.conf_sets['default'].data['exported_ports'].split(',')
    current_ports = [x for x in current_ports if x]
    new_ports = current_ports
    for rtc in rtcs:
        if type(rtcs[rtc][0]) is str:
            inst_name = rtcs[rtc][0]
        else:
            inst_name = rtcs[rtc][0].instance_name
        for p in rtcs[rtc][1]:
            p_name = inst_name + '.' + p
            if p_name in new_ports:
                if verbose:
                    print('Hiding port {0} in composition'.format(p_name),
                            file=sys.stderr)
                new_ports.remove(p_name)
            elif verbose:
                print('Port {0} is already hidden in composition'.format(p_name),
                        file=sys.stderr)
    if new_ports:
        new_ports = reduce(lambda x, y: x + ',' + y, new_ports)
    else:
        new_ports = ''
    comp.set_conf_set_value('default', 'exported_ports', new_ports)
    comp.activate_conf_set('default')
    # Remove RTCs that have no ports specified from the composition
    to_remove = []
    for rtc in rtcs:
        if rtcs[rtc][1]:
            # Ignore components that had ports specified
            continue
        c = rtcs[rtc][0]
        if comp.is_member(c):
            if verbose:
                print('Removing component {0} from composition'.format(rtc),
                        file=sys.stderr)
            to_remove.append(c)
        elif verbose:
            print('Component {0} is not in composition'.format(rtc),
                    file=sys.stderr)
    comp.remove_members(to_remove)


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

    # Input sanity check: ensure all components and ports to be added exist
    add_rtcs = get_comp_objs(add_paths, tree)
    for rtc in add_rtcs:
        for p in add_rtcs[rtc][1]:
            if not add_rtcs[rtc][0].get_port_by_name(p):
                raise rts_exceptions.PortNotFoundError(rtc, p)
    # Ensure all ports to be removed that are on components that are alive
    # exist
    rem_rtcs, rem_zombies = get_potential_comp_objs(rem_paths, tree)
    for rtc in rem_rtcs:
        for p in rem_rtcs[rtc][1]:
            if not rem_rtcs[rtc][0].get_port_by_name(p):
                raise rts_exceptions.PortNotFoundError(rtc, p)

    if tgt_obj.is_manager:
        # Create composition
        if not tgt_suffix:
            tgt_suffix = 'CompositeRTC'
            tgt_raw_path += ':' + tgt_suffix
        # Check if this composition already exists
        comp = tgt_obj.get_node([tgt_obj.name, tgt_suffix + '.rtc'])
        if not comp:
            # Cannot remove components when creating a new composition
            if options.remove:
                raise rts_exceptions.CannotRemoveFromNewCompositionError()
            # No composition exists in this manager; make a new one
            if options.verbose:
                print('Creating new composition {0}'.format(tgt_raw_path),
                        file=sys.stderr)
            comp = create_composition(tgt_obj, tgt_suffix, options.options,
                    options.type)
        elif options.verbose:
            print('Editing existing composition {0}'.format(tgt_raw_path),
                    file=sys.stderr)
    elif tgt_obj.is_component:
        # Edit composition - there should be no suffix
        if tgt_suffix:
            raise rts_exceptions.NotAComponentError(tgt_raw_path)
        comp = tgt_obj
        if options.verbose:
            print('Editing existing composition {0}'.format(tgt_raw_path),
                    file=sys.stderr)
    else:
        raise rts_exceptions.NotAComponentOrManagerError(tgt_raw_path)
    if not comp.is_composite:
        raise rts_exceptions.NotACompositeComponentError(tgt_raw_path)

    if add_paths:
        add_to_composition(comp, add_rtcs, tree, options.verbose)
    if rem_paths:
        rem_rtcs.update(rem_zombies)
        rem_from_composition(comp, rem_rtcs, tree, options.verbose)
    if not comp.members[comp.organisations[0].org_id]:
        if options.verbose:
            print('Composition {0} has no members'.format(tgt_raw_path),
                    file=sys.stderr)


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
            'component on creation.')
    parser.add_option('-r', '--remove', dest='remove', action='append',
            type='string', default=[], help='A component or ports to remove '
            'from the composition.')
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
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    if len(args) != 1:
        print('{0}: No manager or existing composite component '\
            'specified.'.format(sys.argv[0]), file=sys.stderr)
        return 1
    full_path = path.cmd_path_to_full_path(args[0])

    try:
        manage_composition(args[0], full_path, options, tree=tree)
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(sys.argv[0], e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

