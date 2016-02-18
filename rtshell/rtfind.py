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

Implementation of the command to find components, managers, etc.

'''

from __future__ import print_function

import optparse
import os
import os.path
import re
import rtctree.tree
import rtctree.path
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def search(cmd_path, full_path, options, tree=None):
    def get_result(node, args):
        if node.full_path_str.startswith(cmd_path):
            result = node.full_path_str[len(cmd_path):]
            if not result:
                # This will happen if the search root is a component
                return node.name
            return node.full_path_str
        else:
            return node.full_path_str


    def matches_search(node):
        # Filter out types
        if options.type:
            if node.is_component and 'c' not in options.type:
                return False
            if node.is_manager and 'm' not in options.type and \
                    'd' not in options.type:
                return False
            if node.is_nameserver and 'n' not in options.type and \
                    'd' not in options.type:
                return False
            if node.is_directory and 'd' not in options.type and \
                    (not node.is_nameserver and not node.is_manager):
                return False
            if node.is_zombie and 'z' not in options.type:
                return False
        # Filter out depth
        if max_depth > 0 and node.depth > max_depth:
            return False
        if not name_res:
            return True
        # Check for name matches
        for name_re in name_res:
            if name_re.search(node.full_path_str):
                return True
        return False

    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotADirectoryError(cmd_path)

    trailing_slash = False
    if not path[-1]:
        # There was a trailing slash
        trailing_slash = True
        path = path[:-1]

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    # Find the root node of the search
    root = tree.get_node(path)
    if not root:
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    if root.is_component and trailing_slash:
        raise rts_exceptions.NotADirectoryError(cmd_path)

    if options.max_depth:
        max_depth = options.max_depth + len(path) - 1 # The root is 1-long
    else:
        max_depth = 0

    name_res = []
    for name in options.name:
        # Replace regex special characters
        name = re.escape (name)
        # * goes to .*?
        name = name.replace (r'\*', '.*?')
        # ? goes to .
        name = name.replace (r'\?', r'.')
        name_res.append(re.compile(name))
    for name in options.iname:
        # Replace regex special characters
        name = re.escape (name)
        # * goes to .*?
        name = name.replace (r'\*', '.*?')
        # ? goes to .
        name = name.replace (r'\?', r'.')
        name_res.append(re.compile(name, re.IGNORECASE))

    return root.iterate(get_result, filter=[matches_search])


def main(argv=None, tree=None):
    usage = '''Usage: %prog <search path> [options]
Find entries in the RTC tree matching given constraints.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-i', '--iname', dest='iname', action='append',
            type='string', default=[], help='Case-insensitive name pattern. '
            'This option can be specified multiple times.')
    parser.add_option('-m', '--maxdepth', dest='max_depth', action='store',
            type='int', default=0, help='Maximum depth to search down to in '
            'the tree. Set to 0 to disable. [Default: %default]')
    parser.add_option('-n', '--name', dest='name', action='append',
            type='string', default=[], help='Case-sensitive name pattern. '
            'This option can be specified multiple times.')
    parser.add_option('-t', '--type', dest='type', action='store',
            type='string', default='', help='Type of object: c (component), '
            'd (directory), m (manager), n (name server), z (zombie). '
            'Multiple types can be specified in a single entry, e.g. '
            '"--type=dmn".')
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

    if len(args) == 1:
        cmd_path = args[0]
    else:
        print(usage, file=sys.stderr)
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    matches = []
    try:
        matches = search(cmd_path, full_path, options, tree)
        for m in matches:
            print(m)
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

