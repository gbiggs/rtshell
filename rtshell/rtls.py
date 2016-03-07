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

Implementation of the command to list naming contexts.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import rtctree.utils
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


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
            name = (rtctree.utils.build_attr_string(['bold', 'blue'],
                    supported=use_colour) + node.name +
                    rtctree.utils.build_attr_string(['reset'],
                    supported=use_colour))
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
            name = (rtctree.utils.build_attr_string(['bold', 'green'],
                    supported=use_colour) + node.name +
                    rtctree.utils.build_attr_string(['reset'],
                    supported=use_colour))
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
            coloured_string = (rtctree.utils.build_attr_string('bold',
                    supported=use_colour) + str(num_ports) +
                    rtctree.utils.build_attr_string('reset',
                    supported=use_colour) + '/' + str(num_connected))
            total_string = (coloured_string,
                    len(coloured_string) - len(total_string))

            num_ports = len(node.inports)
            num_connected = len(node.connected_inports)
            in_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(in_string) > in_width:
                in_width = len(in_string)
            coloured_string = (rtctree.utils.build_attr_string('bold',
                    supported=use_colour) + str(num_ports) +
                    rtctree.utils.build_attr_string('reset',
                    supported=use_colour) + '/' + str(num_connected))
            in_string = (coloured_string,
                    len(coloured_string) - len(in_string))

            num_ports = len(node.outports)
            num_connected = len(node.connected_outports)
            out_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(out_string) > out_width:
                out_width = len(out_string)
            coloured_string = (rtctree.utils.build_attr_string('bold',
                    supported=use_colour) + str(num_ports) +
                    rtctree.utils.build_attr_string('reset',
                    supported=use_colour) + '/' + str(num_connected))
            out_string = (coloured_string, len(coloured_string) - \
                                len(out_string))

            num_ports = len(node.svcports)
            num_connected = len(node.connected_svcports)
            svc_string = '{0}/{1}'.format(num_ports, num_connected)
            if len(svc_string) > svc_width:
                svc_width = len(svc_string)
            coloured_string = (rtctree.utils.build_attr_string('bold',
                    supported=use_colour) + str(num_ports) +
                    rtctree.utils.build_attr_string('reset',
                    supported=use_colour) + '/' + str(num_connected))
            svc_string = (coloured_string, len(coloured_string) - \
                                len(svc_string))

            info_strings.append((state_string, total_string, in_string,
                                 out_string, svc_string, node.name))
        elif node.is_zombie:
            # Zombies are treated like unknowns, but tagged with *
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
            name = (rtctree.utils.build_attr_string(['faint', 'white'],
                    supported=use_colour) + '*' + node.name +
                    rtctree.utils.build_attr_string(['reset'],
                    supported=use_colour))
            info_strings.append((('-', 0), ('-', 0), ('-', 0),
                                 ('-', 0), ('-', 0), name))
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
            name = (rtctree.utils.build_attr_string(['faint', 'white'],
                    supported=use_colour) + node.name +
                    rtctree.utils.build_attr_string(['reset'],
                    supported=use_colour))
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
    term_rows, term_cols = rtctree.utils.get_terminal_size()
    nrows, ncols, col_widths = rtctree.utils.get_num_columns_and_rows(
            [len(ii[1]) for ii in items], len(gap), term_cols)
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
    use_colour = rtctree.utils.colour_supported(sys.stdout)
    if long:
        lines = get_node_long_lines(listing, use_colour=use_colour)
        return lines
    else:
        items = []
        for entry in listing:
            if entry.is_directory:
                items.append((rtctree.utils.build_attr_string(['bold', 'blue'],
                        supported=use_colour) + entry.name + '/' + \
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour), entry.name))
            elif entry.is_component:
                items.append((entry.name, entry.name))
            elif entry.is_manager:
                items.append((rtctree.utils.build_attr_string(['bold',
                        'green'], supported=use_colour) + entry.name + \
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour), entry.name))
            elif entry.is_zombie:
                items.append((rtctree.utils.build_attr_string(['faint',
                        'white'], supported=use_colour) + '*' + entry.name + \
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour), '*' + entry.name))
            else:
                items.append((rtctree.utils.build_attr_string(['faint',
                        'white'], supported=use_colour) + entry.name + \
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour), entry.name))
        return format_items_list(items)


def list_target(cmd_path, full_path, options, tree=None):
    use_colour = rtctree.utils.colour_supported(sys.stdout)

    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.CannotDoToPortError('list')

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if tree.is_component(path) or tree.is_unknown(path) or \
            tree.is_zombie(path):
        # Path points to a single object: print it like 'ls <file>'.
        if trailing_slash:
            # If there was a trailing slash, complain that the object is not a
            # directory.
            raise rts_exceptions.NoSuchObjectError(cmd_path)
        if options.long:
            return get_node_long_lines([tree.get_node(path)], use_colour)
        else:
            if tree.is_component(path):
                return [path[-1]]
            elif tree.is_zombie(path):
                return [(rtctree.utils.build_attr_string(['faint', 'white'],
                        supported=use_colour) + '*' + path[-1] +
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour))]
            else:
                # Assume unknown
                return [(rtctree.utils.build_attr_string(['faint', 'white'],
                        supported=use_colour) + path[-1] +
                        rtctree.utils.build_attr_string(['reset'],
                        supported=use_colour))]
    elif tree.is_directory(path):
        # If recursing, need to list this directory and all its children
        if options.recurse:
            recurse_root = tree.get_node(path)
            recurse_root_path = recurse_root.full_path_str
            def get_name(node, args):
                if node.full_path_str.startswith(recurse_root_path):
                    result = node.full_path_str[len(recurse_root_path):]
                else:
                    result = node.full_path_str
                return result.lstrip('/')
            dir_names = ['.'] + recurse_root.iterate(get_name,
                    args=options.long, filter=['is_directory'])[1:]
            listings = recurse_root.iterate(list_directory,
                    args=options.long, filter=['is_directory'])
            result = []
            for dir, listing in zip(dir_names, listings):
                if dir == '.':
                    result.append('.:')
                else:
                    result.append('./' + dir + ':')
                result += listing
                result.append('')
            return result
        else:
            dir_node = tree.get_node(path)
            return list_directory(dir_node, options.long)
    else:
        raise rts_exceptions.UnknownObjectError(cmd_path)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [path]
List a name server, directory, manager or component.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-l', dest='long', action='store_true', default=False,
            help='Use a long listing format.')
    parser.add_option('-R', '--recurse', dest='recurse', action='store_true',
            default=False, help='List recursively. [Default: %default]')
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
        cmd_path = ''
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    result = []
    try:
        result = list_target(cmd_path, full_path, options, tree)
        for l in result:
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

