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

File: rtcat.py

Implementation of the command to display component information.

'''

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
from rtcshell.path import cmd_path_to_full_path


def format_component(object, use_colour=True, long=False, really_long=False):
    result = []
    result.append('{0}  {1}'.format(object.name,
            object.get_state_string(add_colour=use_colour)))

    indent = 2
    profile_items = [('Category', object.category),
                     ('Description', object.description),
                     ('Instance name', object.instance_name),
                     ('Type name', object.type_name),
                     ('Vendor', object.vendor),
                     ('Version', object.version)]
    if object.parent:
        profile_items.append(('Parent', object.parent_object))
    pad_length = max([len(item[0]) for item in profile_items]) + 2
    for item in profile_items:
        result.append('{0}{1}{2}'.format(''.ljust(indent),
                                         item[0].ljust(pad_length),
                                         item[1]))

    if object.properties:
        result.append('{0}Extra properties:'.format(''.ljust(indent)))
        indent += 2
        extra_props = object.properties
        keys = extra_props.keys()
        keys.sort()
        pad_length = max([len(key) for key in keys]) + 2
        for key in keys:
            result.append('{0}{1}{2}'.format(''.ljust(indent),
                                             key.ljust(pad_length),
                                             extra_props[key]))
        indent -= 2

    for ec in object.owned_ecs:
        if long:
            result.append('{0}Execution Context {1}'.format(\
                    '-'.rjust(indent), ec.handle))
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
                if really_long:
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
                if really_long:
                    result.append('{0}{1}'.format('-'.rjust(indent),
                        'Extra properties'.ljust(padding)))
                    indent += 2
                    keys = ec.properties.keys()
                    keys.sort()
                    pad_length = max([len(key) for key in keys]) + 2
                    for key in keys:
                        result.append('{0}{1}{2}'.format(''.ljust(indent),
                             key.ljust(pad_length), ec.properties[key]))
                    indent -= 2
                else:
                    result.appent('{0}{1}'.format('+'.rjust(indent),
                        'Extra properties'.ljust(padding)))
            indent -= 2
        else:
            result.append('{0}Execution Context {1}'.format(\
                    '+'.rjust(indent), ec.handle))

    for port in object.ports:
        if long:
            tag = '-'
        else:
            tag = '+'
        name_string = build_attr_string('bold', supported=use_colour) + \
                port.name + build_attr_string('reset', supported=use_colour)
        result.append('{0}{1}: {2}'.format(tag.rjust(indent), port.porttype,
                                           name_string))
        if long:
            indent += 2
            keys = port.properties.keys()
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
                if really_long:
                    tag2 = '-'
                else:
                    tag2 = '+'
                dest_ports = []
                for name, p in conn.ports:
                    if not object.get_port_by_ref(p.object):
                        dest_ports.append(name)
                        num_conns -= 1
                if dest_ports:
                    result.append('{0}Connected to  {1}'.format(\
                            tag2.rjust(indent),
                            build_attr_string('bold', supported=use_colour) +\
                            dest_ports[0] + \
                            build_attr_string('reset', supported=use_colour)))
                    if len(dest_ports) > 1:
                        for dp in dest_ports[1:]:
                            result.append('{0}{1}{2}'.format(''.ljust(indent),
                                                             ''.ljust(14),
                            build_attr_string('bold', supported=use_colour) +\
                            dp + \
                            build_attr_string('reset', supported=use_colour)))
                    if really_long:
                        indent += 2
                        keys = [k for k in conn.properties.keys() \
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


def format_manager(object, use_colour=True, long=False):
    def add_profile_entry(dest, title, key):
        if key in object.profile:
            dest.append('{0}: {1}'.format(title, object.profile[key]))
        else:
            print >>sys.stderr, '{0}: Warning: "{1}" profile entry is \
missing. Possible version conflict between rtcshell and OpenRTM-aist.'.format(\
                    sys.argv[0], key)

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
    for lm in object.loaded_modules:
        result.append('  Filepath: {0}'.format(lm['file_path']))
    # List loadable libraries
    result.append('Loadable modules:')
    for lm in object.loadable_modules:
        result.append('  {0}'.format(lm))

    return result


def cat_target(cmd_path, full_path, options, tree=None):
    use_colour = sys.stdout.isatty()

    path, port = parse_path(full_path)
    if port:
        # Can't cat a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        print >>sys.stderr, '{0}: {1}: Not an \
object'.format(sys.argv[0], cmd_path)
        return 1

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return tree

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    object = tree.get_node(path)
    if object.is_component:
        for l in format_component(object, use_colour=sys.stdout.isatty(),
                                  long=options.long,
                                  really_long=options.really_long):
            print l
    elif object.is_manager:
        for l in format_manager(object, use_colour=sys.stdout.isatty(),
                                long=options.long):
            print l
    else:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
Display information about a manager or component.

Equivalent to the POSIX 'cat' command.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-l', dest='long', action='store_true', default=False,
            help='Show more information. [Default: %default]')
    parser.add_option('--ll', dest='really_long', action='store_true',
            default=False, help='Show even more information. Implies -l. \
[Default: %default]')
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

    if options.really_long:
        options.long = True

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: Cannot cat a directory.'.format(sys.argv[0])
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = cmd_path_to_full_path(cmd_path)

    return cat_target(cmd_path, full_path, options, tree)


# vim: tw=79

