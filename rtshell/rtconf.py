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

Implementation of the command to manage component configuration.

'''


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree, NoSuchConfSetError, \
                         NoSuchConfParamError
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, get_num_columns_and_rows, \
                          get_terminal_size
import sys

from rtshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtshell.path import cmd_path_to_full_path


def is_hidden(name):
    hidden_prefix = '__'
    hidden_suffix = '__'
    return name.startswith(hidden_prefix) and name.endswith(hidden_suffix)


def format_conf_set(set_name, set, is_active, use_colour, long):
    result = []
    indent = 0
    if long:
        tag = '-'
    else:
        tag = '+'
    if is_active:
        title = tag + build_attr_string(['bold', 'green'],
                                        supported=use_colour) + \
                set_name + '*' + build_attr_string('reset',
                                                   supported=use_colour)
        if set.description:
            title += ' ({0})'.format(set.description)
    else:
        title = tag + build_attr_string('bold', supported=use_colour) + \
                set_name + build_attr_string('reset', supported=use_colour)
        if set.description:
            title += '  ({0})'.format(set.description)
    result.append(title)

    if long:
        params = set.data.keys()
        if params:
            params.sort()
            padding = len(max(params, key=len)) + 2
            indent += 2
            for param in params:
                result.append('{0}{1}{2}'.format(''.ljust(indent),
                        param.ljust(padding), set.data[param]))
            indent -= 2

    return result


def format_conf_sets(sets, active_set_name, all, use_colour, long):
    result = []
    set_keys = [k for k in sets.keys() if not is_hidden(k) or all]
    set_keys.sort()
    for set_name in set_keys:
        result += format_conf_set(set_name, sets[set_name],
            set_name == active_set_name, use_colour, long)
    return result


def print_conf_sets(cmd_path, full_path, options, tree=None):
    use_colour = sys.stdout.isatty()

    path, port = parse_path(full_path)
    if port:
        # Can't configure a port
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
        tree = create_rtctree(paths=path, filter=[path])
    if not tree:
        return 1

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
component.'.format(sys.argv[0], cmd_path)
        return 1

    if options.set_name:
        if is_hidden(options.set_name) and not options.all:
            print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], options.set_name)
            return 1

        if not options.set_name in object.conf_sets:
            print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], options.set_name)
            return 1
        lines = format_conf_set(options.set_name,
                object.conf_sets[options.set_name],
                options.set_name == object.active_conf_set_name,
                use_colour, options.long)
        for l in lines:
            print l
    else:
        for l in format_conf_sets(object.conf_sets,
                object.active_conf_set_name, options.all,
                use_colour, options.long):
            print l

    return 0


def set_conf_value(param, new_value, cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't configure a port
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
        tree = create_rtctree(paths=path, filter=[path])
    if not tree:
        return 1

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
component.'.format(sys.argv[0], cmd_path)
        return 1

    if not options.set_name:
        options.set_name = object.active_conf_set_name

    if is_hidden(options.set_name) and not options.all:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], e)
        return 1

    try:
        object.set_conf_set_value(options.set_name, param, new_value)
    except NoSuchConfSetError, e:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], e)
        return 1
    except NoSuchConfParamError, e:
        print >>sys.stderr, '{0}: {1}: No such configuration \
parameter'.format(sys.argv[0], e)
        return 1
    if options.set_name == object.active_conf_set_name:
        # Re-activate the set to update the config param internally in the
        # component.
        object.activate_conf_set(options.set_name)

    return 0


def get_conf_value(param, cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't configure a port
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
        tree = create_rtctree(paths=path, filter=[path])
    if not tree:
        return 1

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
component.'.format(sys.argv[0], cmd_path)
        return 1

    if not options.set_name:
        options.set_name = object.active_conf_set_name

    if is_hidden(options.set_name) and not options.all:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], e)
        return 1

    if not options.set_name in object.conf_sets:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], options.set_name)
        return 1
    if not param in object.conf_sets[options.set_name].data:
        print >>sys.stderr, '{0}: {1}: No such configuration \
parameter'.format(sys.argv[0], param)
        return 1
    print object.conf_sets[options.set_name].data[param]

    return 0


def activate_set(set_name, cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't configure a port
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
        tree = create_rtctree(paths=path, filter=[path])
    if not tree:
        return 1

    object = tree.get_node(path)
    if not object:
        print >>sys.stderr, '{0}: Cannot access {1}: No such \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if object.is_zombie:
        print >>sys.stderr, '{0}: Zombie object.'.format(sys.argv[0])
        return 1
    if not object.is_component:
        print >>sys.stderr, '{0}: Cannot access {1}: Not a \
component.'.format(sys.argv[0], cmd_path)
        return 1

    if is_hidden(set_name) and not options.all:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], e)
        return 1

    try:
        object.activate_conf_set(set_name)
    except NoSuchConfSetError, e:
        print >>sys.stderr, '{0}: {1}: No such configuration \
set'.format(sys.argv[0], e)
        return 1

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog <path> [options] [command] [args]
Display and edit configuration parameters and sets.

A command should be one of:
    list, set, get, act
If no command is specified, the list command will be executed.

The list command takes no arguments.

The set command requires a parameter name and a value as arguments. If no set
is specified (using --set), the parameter is changed in the currently active
configuration set. For example:
    --set=outdoor set max_speed 4
    set max_speed 2

The get command requires an optional set name and a parameter name as
arguments. If no set is specified (using --set), the parameter value from the
currently activate configuration set is retrieved. For example:
    --set=outdoor get max_speed
        4
    get max_speed
        2

The act command requires a single argument: the name of a configuration
set to activate.

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-a', '--all', dest='all', action='store_true',
            default=False,
            help='Do not ignore hidden sets. [Default: %default]')
    parser.add_option('-l', dest='long', action='store_true', default=False,
            help='Show more information. [Default: %default]')
    parser.add_option('-s', '--set', dest='set_name', action='store',
            default='', help='Choose the configuration set to manipulate. \
[Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        print >>sys.stderr, usage
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
        cmd = 'list'
        args = args[1:]
    else:
        cmd_path = args[0]
        cmd = args[1]
        args = args[2:]
    full_path = cmd_path_to_full_path(cmd_path)

    if cmd == 'list':
        # Print the configuration sets
        return print_conf_sets(cmd_path, full_path, options, tree)
    elif cmd == 'set':
        # Need to get more arguments
        if len(args) == 2:
            param = args[0]
            new_value = args[1]
        else:
            print >>sys.stderr, usage
            return 1
        return set_conf_value(param, new_value, cmd_path, full_path, options,
                tree)
    elif cmd == 'get':
        #Need to get more arguments
        if len(args) == 1:
            param = args[0]
        else:
            print >>sys.stderr, usage
            return 1
        return get_conf_value(param, cmd_path, full_path, options, tree)
    elif cmd == 'act':
        if len(args) != 1:
            print >>sys.stderr, usage
            return 1
        return activate_set(args[0], cmd_path, full_path, options, tree)

    print >>sys.stderr, usage
    return 1


# vim: tw=79

