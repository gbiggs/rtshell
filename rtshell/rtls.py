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

File: rtls.py

Implementation of the command to list naming contexts.

'''

# $Source$


from optparse import OptionParser, OptionError
import os
from rtctree.exceptions import RtcTreeError
from rtctree.tree import create_rtctree, InvalidServiceError, \
                         FailedToNarrowRootNamingError, \
                         NonRootPathError
from rtctree.path import parse_path
from rtctree.utils import build_attr_string, colour_supported, \
                          get_num_columns_and_rows, get_terminal_size
import sys

from rtcshell import RTSH_PATH_USAGE, RTSH_VERSION
from rtcshell.path import cmd_path_to_full_path


def get_node_long_lines(nodes, use_colour=True):
    info_strings = []
    state_width = 0
    total_width = 0
    in_width = 0
    out_width = 0
    svc_width = 0
    for node in nodes:
        if node.is_directory:
            if state_width == 0:
                state_width = 1
            if total_width == 0:
                total_width = 1
            if in_width == 0:
                in_width = 1
            if out_width == 0:
                out_width = 1
            if svc_width == 0:
                svc_width = 1
            name = build_attr_string(['bold', 'blue'],
                        supported=use_colour) + \
                    node.name + build_attr_string(['reset'],
                        supported=use_colour)
            info_strings.append((('-', 0), ('-', 0), ('-', 0),
                                 ('-', 0), ('-', 0), name))
        elif node.is_manager:
            # Managers are not handled yet
            if state_width == 0:
                state_width = 1
            if total_width == 0:
                total_width = 1
            if in_width == 0:
                in_width = 1
            if out_width == 0:
                out_width = 1
            if svc_width == 0:
                svc_width = 1
            name = build_attr_string(['bold', 'green'],
                        supported=use_colour) + \
                    node.name + build_attr_string(['reset'],
                        supported=use_colour)
            info_strings.append((('-', 0), ('-', 0), ('-', 0),
                                 ('-', 0), ('-', 0), name))
        elif node.is_component:
            state = node.state
            state_string = node.plain_state_string
            if len(state_string) > state_width:
                state_width = len(state_string)
            state_string = (node.get_state_string(add_colour=use_colour),
                    len(node.get_state_string(add_colour=use_colour)) - \
                            len(state_string))

            num_ports = len(node.ports)
            num_connected = len(node.connected_ports)
            total_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(total_string) > total_width:
                total_width = len(total_string)
            coloured_string = build_attr_string('bold',
                                supported=use_colour) + \
                              str(num_ports) + \
                              build_attr_string('reset',
                                supported=use_colour) + '/' + \
                              str(num_connected)
            total_string = (coloured_string, len(coloured_string) - \
                                len(total_string))

            num_ports = len(node.inports)
            num_connected = len(node.connected_inports)
            in_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(in_string) > in_width:
                in_width = len(in_string)
            coloured_string = build_attr_string('bold',
                                supported=use_colour) + \
                              str(num_ports) + \
                              build_attr_string('reset',
                                supported=use_colour) + '/' + \
                              str(num_connected)
            in_string = (coloured_string, len(coloured_string) - \
                                len(in_string))

            num_ports = len(node.outports)
            num_connected = len(node.connected_outports)
            out_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(out_string) > out_width:
                out_width = len(out_string)
            coloured_string = build_attr_string('bold',
                                supported=use_colour) + \
                              str(num_ports) + \
                              build_attr_string('reset',
                                supported=use_colour) + '/' + \
                              str(num_connected)
            out_string = (coloured_string, len(coloured_string) - \
                                len(out_string))

            num_ports = len(node.svcports)
            num_connected = len(node.connected_svcports)
            svc_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(svc_string) > svc_width:
                svc_width = len(svc_string)
            coloured_string = build_attr_string('bold',
                                supported=use_colour) + \
                              str(num_ports) + \
                              build_attr_string('reset',
                                supported=use_colour) + '/' + \
                              str(num_connected)
            svc_string = (coloured_string, len(coloured_string) - \
                                len(svc_string))

            info_strings.append((state_string, total_string, in_string,
                                 out_string, svc_string, node.name))
        else:
            # Other types are unknowns
            if state_width == 0:
                state_width = 1
            if total_width == 0:
                total_width = 1
            if in_width == 0:
                in_width = 1
            if out_width == 0:
                out_width = 1
            if svc_width == 0:
                svc_width = 1
            name = build_attr_string(['faint', 'white'],
                        supported=use_colour) + \
                    node.name + build_attr_string(['reset'],
                        supported=use_colour)
            info_strings.append((('-', 0), ('-', 0), ('-', 0),
                                 ('-', 0), ('-', 0), name))
    state_width += 2
    total_width += 2
    in_width += 2
    out_width += 2
    svc_width += 2

    result = []
    for string in info_strings:
        result.append('{0}{1}{2}{3}{4}{5}'.format(
                string[0][0].ljust(state_width + string[0][1]),
                string[1][0].ljust(total_width + string[1][1]),
                string[2][0].ljust(in_width + string[2][1]),
                string[3][0].ljust(out_width + string[3][1]),
                string[4][0].ljust(svc_width + string[4][1]),
                string[5]))
    return result


def format_items_list(items):
    gap = '  '
    term_rows, term_cols = get_terminal_size()
    nrows, ncols, col_widths = get_num_columns_and_rows([len(ii[1]) \
            for ii in items], len(gap), term_cols)
    rows = [items[s:s + ncols] for s in range(0, len(items), ncols)]
    lines = []
    for r in rows:
        new_line = ''
        for ii, c in enumerate(r):
            new_line += '{0:{1}}'.format(c[0], col_widths[ii] + \
                    (len(c[0]) - len(c[1]))) + gap
        lines.append(new_line.rstrip())
    return lines


def list_directory(dir_node, long=False):
    listing = dir_node.children
    use_colour = colour_supported(sys.stdout)
    if long:
        lines = get_node_long_lines(listing, use_colour=use_colour)
        return lines
    else:
        items = []
        for entry in listing:
            if entry.is_directory:
                items.append((build_attr_string(['bold', 'blue'],
                                supported=use_colour) + \
                              entry.name + '/' + \
                              build_attr_string(['reset'],
                                supported=use_colour),
                             entry.name))
            elif entry.is_component:
                items.append((entry.name, entry.name))
            elif entry.is_manager:
                items.append((build_attr_string(['bold', 'green'],
                                supported=use_colour) + \
                              entry.name + \
                              build_attr_string(['reset'],
                                  supported=use_colour),
                             entry.name))
            else:
                items.append((build_attr_string(['faint', 'white'],
                                supported=use_colour) + \
                              entry.name + \
                              build_attr_string(['reset'],
                                  supported=use_colour),
                             entry.name))
        return format_items_list(items)


def list_target(cmd_path, full_path, options, tree=None):
    path, port = parse_path(full_path)
    if port:
        # Can't list a port
        print >>sys.stderr, '{0}: Cannot access {1}: No such directory or \
object.'.format(sys.argv[0], cmd_path)
        return 1

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]

    if not tree:
        tree = create_rtctree(paths=path)
    if not tree:
        return 1

    if not tree.has_path(path):
        print >>sys.stderr, '{0}: Cannot access {1}: No such directory or \
object.'.format(sys.argv[0], cmd_path)
        return 1
    if tree.is_component(path):
        # Path points to a single component: print it like 'ls <file>'.
        if trailing_slash:
            # If there was a trailing slash, complain that a component is not a
            # directory.
            print >>sys.stderr, '{0}: cannot access {1}: Not a \
directory.'.format(sys.argv[0], address)
            return 1
        if options.long:
            lines = get_node_long_lines([tree.get_node(path)],
                                        sys.stdout.isatty())
            for l in lines:
                print l
        else:
            print path[-1]
    elif tree.is_directory(path):
        # If recursing, need to list this directory and all its children
        if options.recurse:
            recurse_root = tree.get_node(path)
            recurse_root_path = recurse_root.full_path
            def get_name(node, args):
                if node.full_path.startswith(recurse_root_path):
                    result = node.full_path[len(recurse_root_path):]
                else:
                    result = node.full_path
                return result.lstrip('/')
            dir_names = ['.'] + recurse_root.iterate(get_name,
                    args=options.long, filter=['is_directory'])[1:]
            listings = recurse_root.iterate(list_directory,
                    args=options.long, filter=['is_directory'])
            for dir, listing in zip(dir_names, listings):
                if dir == '.':
                    print '.:'
                else:
                    print './' + dir + ':'
                for l in listing:
                    print l
                print
        else:
            dir_node = tree.get_node(path)
            lines = list_directory(dir_node, options.long)
            for l in lines:
                print l
    else:
        print >>sys.stderr, '{0}: cannot access {1}: Unknown object \
type.'.format(sys.argv[0], cmd_path)
        return 1

    return 0


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
List a name server, directory, manager or component.

Equivalent to the POSIX 'ls' command.

The long display shows the following information in columns:
State
Total number of ports/Total connected
Input ports/Inputs connected
Output ports/Outputs connected
Service ports/Service connected
Name

''' + RTSH_PATH_USAGE
    version = RTSH_VERSION
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('-l', dest='long', action='store_true', default=False,
            help='Use a long listing format.')
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
            default=False, help='Print debugging information. \
[Default: %default]')
    parser.add_option('-R', '--recurse', dest='recurse', action='store_true',
            default=False, help='List recursively. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except OptionError, e:
        print 'OptionError:', e
        return 1

    if not args:
        cmd_path = ''
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = cmd_path_to_full_path(cmd_path)

    return list_target(cmd_path, full_path, options, tree)


# vim: tw=79

