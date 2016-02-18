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

Implementation of the command to manage component configuration.

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
        title = tag + rtctree.utils.build_attr_string(['bold', 'green'],
                supported=use_colour) + set_name + '*' + \
                rtctree.utils.build_attr_string('reset', supported=use_colour)
        if set.description:
            title += ' ({0})'.format(set.description)
    else:
        title = tag + rtctree.utils.build_attr_string('bold',
                supported=use_colour) + set_name + \
                rtctree.utils.build_attr_string('reset', supported=use_colour)
        if set.description:
            title += '  ({0})'.format(set.description)
    result.append(title)

    if long:
        params = list(set.data.keys())
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
    set_keys = [k for k in list(sets.keys()) if not is_hidden(k) or all]
    set_keys.sort()
    for set_name in set_keys:
        result += format_conf_set(set_name, sets[set_name],
            set_name == active_set_name, use_colour, long)
    return result


def get_comp(cmd_path, full_path, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        # Can't configure a port
        raise rts_exceptions.NotAComponentError(cmd_path)
    if not path[-1]:
        # There was a trailing slash
        raise rts_exceptions.NoSuchObjectError(cmd_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    comp = tree.get_node(path)
    if not comp:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if comp.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not comp.is_component:
        raise rts_exceptions.NotAComponentError(cmd_path)
    return tree, comp



def print_conf_sets(cmd_path, full_path, options, tree=None):
    use_colour = rtctree.utils.colour_supported(sys.stdout)
    tree, comp = get_comp(cmd_path, full_path, tree)

    if options.set_name:
        if is_hidden(options.set_name) and not options.all:
            raise rts_exceptions.NoConfSetError(options.set_name)
        if not options.set_name in comp.conf_sets:
            raise rts_exceptions.NoConfSetError(options.set_name)
        return format_conf_set(options.set_name,
                comp.conf_sets[options.set_name],
                options.set_name == comp.active_conf_set_name,
                use_colour, options.long)
    else:
        return format_conf_sets(comp.conf_sets,
                comp.active_conf_set_name, options.all,
                use_colour, options.long)


def set_conf_value(param, new_value, cmd_path, full_path, options, tree=None):
    tree, comp = get_comp(cmd_path, full_path, tree)

    if not options.set_name:
        options.set_name = comp.active_conf_set_name
    if is_hidden(options.set_name) and not options.all:
        raise rts_exceptions.NoConfSetError(options.set_name)
    comp.set_conf_set_value(options.set_name, param, new_value)
    if options.set_name == comp.active_conf_set_name:
        # Re-activate the set to update the config param internally in the
        # component.
        comp.activate_conf_set(options.set_name)


def get_conf_value(param, cmd_path, full_path, options, tree=None):
    tree, comp = get_comp(cmd_path, full_path, tree)

    if not options.set_name:
        options.set_name = comp.active_conf_set_name
    if is_hidden(options.set_name) and not options.all:
        raise rts_exceptions.NoConfSetError(options.set_name)

    if not options.set_name in comp.conf_sets:
        raise rts_exceptions.NoConfSetError(options.set_name)
    if not param in comp.conf_sets[options.set_name].data:
        raise rtctree.exceptions.NoSuchConfParamError(param)
    return [comp.conf_sets[options.set_name].data[param]]


def activate_set(cmd_path, full_path, options, tree=None):
    if is_hidden(options.set_name) and not options.all:
        raise rts_exceptions.NoConfSetError(options.set_name)
    tree, comp = get_comp(cmd_path, full_path, tree)
    if not options.set_name in comp.conf_sets:
        raise rts_exceptions.NoConfSetError(options.set_name)
    comp.activate_conf_set(options.set_name)


def main(argv=None, tree=None):
    usage = '''Usage: %prog <path> [options] [command] [args]
Display and edit configuration parameters and sets.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-a', '--all', dest='all', action='store_true',
            default=False,
            help='Do not ignore hidden sets. [Default: %default]')
    parser.add_option('-l', dest='long', action='store_true', default=False,
            help='Show more information. [Default: %default]')
    parser.add_option('-s', '--set', dest='set_name', action='store',
            default='', help='Choose the configuration set to manipulate. '\
            '[Default: %default]')
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

    if not args:
        print(usage, file=sys.stderr)
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
        cmd = 'list'
        args = args[1:]
    else:
        cmd_path = args[0]
        cmd = args[1]
        args = args[2:]
    full_path = path.cmd_path_to_full_path(cmd_path)

    result = []
    try:
        if cmd == 'list':
            # Print the configuration sets
            result = print_conf_sets(cmd_path, full_path, options, tree)
        elif cmd == 'set':
            # Need to get more arguments
            if len(args) == 2:
                param = args[0]
                new_value = args[1]
            else:
                print(usage, file=sys.stderr)
                return 1
            set_conf_value(param, new_value, cmd_path, full_path, options,
                    tree)
        elif cmd == 'get':
            #Need to get more arguments
            if len(args) == 1:
                param = args[0]
            else:
                print(usage, file=sys.stderr)
                return 1
            result = get_conf_value(param, cmd_path, full_path, options, tree)
        elif cmd == 'act':
            if len(args) != 0 or options.set_name == '':
                print(usage, file=sys.stderr)
                return 1
            activate_set(cmd_path, full_path, options, tree)
        else:
            print(usage, file=sys.stderr)
            return 1
    except Exception as e:
        if options.verbose:
            traceback.print_exc()
        print('{0}: {1}'.format(os.path.basename(sys.argv[0]), e),
                file=sys.stderr)
        return 1
    for l in result:
        print(l)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# vim: tw=79

