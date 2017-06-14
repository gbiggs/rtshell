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

Implementation of the command to display component information.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import rtctree.utils
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def format_port(port, comp, start_indent=0, use_colour=True, long=0):
    result = []
    indent = start_indent
    if long > 0:
        tag = '-'
    else:
        tag = '+'
    name_string = rtctree.utils.build_attr_string('bold',
            supported=use_colour) + port.name + \
                rtctree.utils.build_attr_string('reset', supported=use_colour)
    result.append('{0}{1}: {2}'.format(tag.rjust(indent), port.porttype,
                                       name_string))
    if long > 0:
        indent += 2
        keys = list(port.properties.keys())
        keys.sort()
        pad_length = max([len(key) for key in keys]) + 2
        for key in keys:
            result.append('{0}{1}{2}'.format(''.ljust(indent),
                    key.ljust(pad_length), port.properties[key]))
        if port.porttype == 'CorbaPort' and port.interfaces:
            for intf in port.interfaces:
                result.append('{0}Interface:'.format(''.ljust(indent)))
                pad_length = 15 # = len('Instance name') + 2
                indent += 2
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                        'Instance name'.ljust(pad_length),
                        intf.instance_name))
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                        'Type name'.ljust(pad_length),
                        intf.type_name))
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                        'Polarity'.ljust(pad_length),
                        intf.polarity_as_string(add_colour=use_colour)))
                indent -= 2
        num_conns = len(port.connections)
        for conn in port.connections:
            if long > 1:
                tag2 = '-'
            else:
                tag2 = '+'
            dest_ports = []
            for name, p in conn.ports:
                # Handle the case of unknown port owners
                if not p:
                    dest_ports.append(name)
                    num_conns -= 1
                # Filter out ports belonging to this comp
                elif not comp.get_port_by_ref(p.object):
                    dest_ports.append(name)
                    num_conns -= 1
            if dest_ports:
                result.append('{0}Connected to  {1}'.format(
                    tag2.rjust(indent), rtctree.utils.build_attr_string('bold',
                        supported=use_colour) + dest_ports[0] + \
                        rtctree.utils.build_attr_string('reset',
                            supported=use_colour)))
                if len(dest_ports) > 1:
                    for dp in dest_ports[1:]:
                        result.append('{0}{1}{2}'.format(''.ljust(indent),
                            ''.ljust(14),
                        rtctree.utils.build_attr_string('bold',
                            supported=use_colour) + dp + \
                                rtctree.utils.build_attr_string('reset',
                                    supported=use_colour)))
                if long > 1:
                    indent += 2
                    keys = [k for k in list(conn.properties.keys()) \
                            if not k.endswith('inport_ref') \
                            if not k.endswith('inport_ior')]
                    pad_length = max([len('Name')] + \
                                     [len(key) for key in keys]) + 2
                    result.append('{0}{1}{2}'.format(''.ljust(indent),
                            'Name'.ljust(pad_length), conn.name))
                    result.append('{0}{1}{2}'.format(''.ljust(indent),
                            'ID'.ljust(pad_length), conn.id))
                    for key in keys:
                        result.append('{0}{1}{2}'.format(''.ljust(indent),
                                key.ljust(pad_length),
                                conn.properties[key]))
                    indent -= 2
        if num_conns > 0:
            if num_conns > 1:
                plural = 's'
            else:
                plural = ''
            result.append('{0}({1} other connection{2})'.format(\
                    ''.rjust(indent), num_conns, plural))
        indent -= 2
    return result


def find_composite_comp(tree, member, inst_name):
    def get_fp(mgr, args):
        for c in mgr.components:
            if c.instance_name == inst_name:
                return c.full_path_str
        return None
    def is_correct_mgr(node):
        has_member = False
        has_inst_name = False
        for c in node.components:
            if c.instance_name == inst_name:
                has_inst_name = True
            elif c.instance_name == member.instance_name:
                has_member = True
        return has_member and has_inst_name
    return tree.iterate(get_fp, filter=['is_manager', is_correct_mgr])


def format_composite(comp, tree, start_indent=0, use_colour=True, long=0):
    result = []
    indent = start_indent
    for o in comp.organisations:
        if not o.sdo_id:
            sdo_id = 'Unknown'
        else:
            sdo_id = o.sdo_id
        id_str = rtctree.utils.build_attr_string('bold',
                supported=use_colour) + sdo_id + \
                        rtctree.utils.build_attr_string('reset',
                        supported=use_colour)
        if long > 0:
            tag = '-'
        else:
            tag = '+'
        result.append('{0}Composition {1}'.format(tag.rjust(indent),
            id_str))
        if long > 0:
            indent += 2
            padding = 8 # = len('Member') + 2
            result.append('{0}{1}{2}'.format(''.ljust(indent),
                'ID'.ljust(padding), o.org_id))
            for m in o.members:
                c_path = find_composite_comp(tree, comp, m)
                if c_path:
                    result.append('{0}{1}{2}'.format(''.ljust(indent),
                        'Member'.ljust(padding), c_path[0]))
                else:
                    result.append('{0}{1}{2}'.format(''.ljust(indent),
                        'Member'.ljust(padding), 'Unknown'))
            indent -= 2
    return result


def format_comp_member(comp, tree, start_indent=0, use_colour=True, long=0):
    result = []
    indent = start_indent
    for po in comp.parent_organisations:
        if not po.sdo_id:
            sdo_id = 'Unknown'
        else:
            sdo_id = po.sdo_id
        id_str = rtctree.utils.build_attr_string('bold',
                supported=use_colour) + sdo_id + \
                        rtctree.utils.build_attr_string('reset',
                        supported=use_colour)
        if long > 0:
            tag = '-'
        else:
            tag = '+'
        result.append('{0}Parent composition {1}'.format(tag.rjust(indent),
            id_str))
        if long > 0:
            indent += 2
            padding = 6 # = len('Path') + 2
            result.append('{0}{1}{2}'.format(''.ljust(indent),
                'ID'.ljust(padding), po.org_id))
            composite_path = find_composite_comp(tree, comp, po.sdo_id)
            if composite_path:
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                    'Path'.ljust(padding), composite_path[0]))
            else:
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                    'Path'.ljust(padding), 'Unknown'))
            indent -= 2
    return result


def format_ec(ec, start_indent=0, use_colour=True, long=0):
    result = []
    indent = start_indent
    handle_str = rtctree.utils.build_attr_string('bold',
            supported=use_colour) + str(ec.handle) + \
                    rtctree.utils.build_attr_string('reset',
                    supported=use_colour)
    if long > 0:
        result.append('{0}Execution Context {1}'.format(\
                '-'.rjust(indent), handle_str))
        padding = 7 # = len('State') + 2
        indent += 2
        result.append('{0}{1}{2}'.format(''.ljust(indent),
            'State'.ljust(padding),
            ec.running_as_string(add_colour=use_colour)))
        result.append('{0}{1}{2}'.format(''.ljust(indent),
            'Kind'.ljust(padding),
            ec.kind_as_string(add_colour=use_colour)))
        result.append('{0}{1}{2}'.format(''.ljust(indent),
            'Rate'.ljust(padding), ec.rate))
        if ec.owner_name:
            result.append('{0}{1}{2}'.format(''.ljust(indent),
                'Owner'.ljust(padding), ec.owner_name))
        if ec.participant_names:
            if long > 1:
                    result.append('{0}{1}'.format('-'.rjust(indent),
                        'Participants'.ljust(padding)))
                    indent += 2
                    for pn in ec.participant_names:
                        result.append('{0}{1}'.format(''.ljust(indent),
                            pn))
                    indent -= 2
            else:
                result.append('{0}{1}'.format('+'.rjust(indent),
                    'Participants'.ljust(padding)))
        if ec.properties:
            if long > 1:
                result.append('{0}{1}'.format('-'.rjust(indent),
                    'Extra properties'.ljust(padding)))
                indent += 2
                keys = list(ec.properties.keys())
                keys.sort()
                pad_length = max([len(key) for key in keys]) + 2
                for key in keys:
                    result.append('{0}{1}{2}'.format(''.ljust(indent),
                         key.ljust(pad_length), ec.properties[key]))
                indent -= 2
            else:
                result.append('{0}{1}'.format('+'.rjust(indent),
                    'Extra properties'.ljust(padding)))
        indent -= 2
    else:
        result.append('{0}Execution Context {1}'.format(\
                '+'.rjust(indent), handle_str))
    return result


def format_component(comp, tree, use_colour=True, long=0):
    result = []
    result.append('{0}  {1}'.format(comp.name,
            comp.get_state_string(add_colour=use_colour)))

    indent = 2
    profile_items = [('Category', comp.category),
                     ('Description', comp.description),
                     ('Instance name', comp.instance_name),
                     ('Type name', comp.type_name),
                     ('Vendor', comp.vendor),
                     ('Version', comp.version)]
    if comp.parent:
        profile_items.append(('Parent', comp.parent_object))
    if comp.is_composite:
        if comp.is_composite_member:
            profile_items.append(('Type', 'Composite composite member'))
        else:
            profile_items.append(('Type', 'Composite'))
    elif comp.is_composite_member:
        profile_items.append(('Type', 'Monolithic composite member'))
    else:
        profile_items.append(('Type', 'Monolithic'))
    pad_length = max([len(item[0]) for item in profile_items]) + 2
    for item in profile_items:
        result.append('{0}{1}{2}'.format(''.ljust(indent),
                                         item[0].ljust(pad_length),
                                         item[1]))

    if comp.properties:
        if long > 1:
            result.append('{0}Extra properties:'.format(''.ljust(indent)))
            indent += 2
            extra_props = comp.properties
            keys = list(extra_props.keys())
            keys.sort()
            pad_length = max([len(key) for key in keys]) + 2
            for key in keys:
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                                                 key.ljust(pad_length),
                                                 extra_props[key]))
        else:
            result.append('{0}{1}'.format('+'.rjust(indent),
                'Extra properties'))
        indent -= 2

    if comp.is_composite:
        result += format_composite(comp, tree, start_indent=indent,
                use_colour=use_colour, long=long)
    if comp.is_composite_member:
        result += format_comp_member(comp, tree, start_indent=indent,
                use_colour=use_colour, long=long)
    for ec in comp.owned_ecs:
        result += format_ec(ec, start_indent=indent,
                use_colour=use_colour, long=long)
    for p in comp.ports:
        result += format_port(p, comp, start_indent=indent,
                use_colour=use_colour, long=long)

    return result


def format_manager(mgr, use_colour=True, long=0):
    def add_profile_entry(dest, title, key):
        if key in mgr.profile:
            dest.append('{0}: {1}'.format(title, mgr.profile[key]))
        else:
            print('{0}: Warning: "{1}" profile entry is \
missing. Possible version conflict between rtshell and OpenRTM-aist.'.format(\
                    sys.argv[0], key), file=sys.stderr)

    result = []
    add_profile_entry(result, 'Name', 'name')
    add_profile_entry(result, 'Instance name', 'instance_name')
    add_profile_entry(result, 'Process ID', 'pid')
    add_profile_entry(result, 'Naming format', 'naming_formats')
    add_profile_entry(result, 'Refstring path', 'refstring_path')
    add_profile_entry(result, 'Components precreate', 'components.precreate')
    result.append('Modules:')
    add_profile_entry(result, '  Load path', 'modules.load_path')
    add_profile_entry(result, '  Config path', 'modules.config_path')
    add_profile_entry(result, '  Preload', 'modules.preload')
    add_profile_entry(result, '  Init function prefix',
            'modules.init_func_prefix')
    add_profile_entry(result, '  Init function suffix',
            'modules.init_func_suffix')
    add_profile_entry(result, '  Download allowed',
            'modules.download_allowed')
    add_profile_entry(result, '  Absolute path allowed',
            'modules.abs_path_allowed')
    result.append('OS:')
    add_profile_entry(result, '  Version', 'os.version')
    add_profile_entry(result, '  Architecture', 'os.arch')
    add_profile_entry(result, '  Release', 'os.release')
    add_profile_entry(result, '  Host name', 'os.hostname')
    add_profile_entry(result, '  Name', 'os.name')
    # List loaded libraries
    result.append('Loaded modules:')
    for lm in mgr.loaded_modules:
        result.append('  Filepath: {0}'.format(lm['file_path']))
    # List loadable libraries
    result.append('Loadable modules:')
    for lm in mgr.loadable_modules:
        result.append('  {0}'.format(lm['module_file_path']))

    return result


def cat_target(cmd_path, full_path, options, tree=None):
    use_colour = rtctree.utils.colour_supported(sys.stdout)

    path, port = rtctree.path.parse_path(full_path)
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]
    else:
        trailing_slash = False

    if not tree:
        if options.long > 0:
            # Longer output needs to look around the tree, so don't filter
            filter = []
        else:
            filter = [path]
        tree = rtctree.tree.RTCTree(paths=path, filter=filter)

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)
    if port:
        if not object.is_component:
            raise rts_exceptions.NotAComponentError(cmd_path)
        if trailing_slash:
            raise rts_exceptions.NoSuchObjectError(cmd_path)
        p = object.get_port_by_name(port)
        if not p:
            raise rts_exceptions.PortNotFoundError(path, port)
        return format_port(p, object, start_indent=0,
                use_colour=use_colour, long=options.long)
    else:
        if object.is_component:
            if trailing_slash:
                raise rts_exceptions.NoSuchObjectError(cmd_path)
            return format_component(object, tree, use_colour=use_colour,
                    long=options.long)
        elif object.is_manager:
            return format_manager(object, use_colour=use_colour,
                    long=options.long)
        elif object.is_zombie:
            raise rts_exceptions.ZombieObjectError(cmd_path)
        else:
            raise rts_exceptions.NoSuchObjectError(cmd_path)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
Display information about a manager or component.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-l', dest='long', action='count', default=0,
            help='Show more information. Specify multiple times for even '\
            'more information. [Default: False]')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        # If no path given then can't do anything.
        print('{0}: Cannot cat a directory.'.format(
                os.path.basename(sys.argv[0])), file=sys.stderr)
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        output = cat_target(cmd_path, full_path, options, tree=tree)
        for l in output:
            print(l)
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

