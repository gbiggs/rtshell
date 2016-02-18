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

Implementation of deleting an object from a name server.

'''

from __future__ import print_function

import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

from rtshell import path
from rtshell import rts_exceptions
import rtshell


def delete_object_reference(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.UndeletableObjectError(cmd_path)
    if not path[-1]:
        path = path[:-1]

    # Cannot delete name servers
    if len(path) == 2:
        raise rts_exceptions.UndeletableObjectError(cmd_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    if options.zombies and not tree.is_zombie(path):
        raise rts_exceptions.NotZombieObjectError(cmd_path)

    # There is no point in doing path checks for the path, as the path we are
    # deleting may not be in the tree if it's a zombie. Instead, we need to
    # find its parent, and use that to remove the name.
    parent = tree.get_node(path[:-1])
    if parent.is_manager:
        raise rts_exceptions.ParentNotADirectoryError(cmd_path)
    if not parent.is_directory:
        raise rts_exceptions.ParentNotADirectoryError(cmd_path)
    parent.unbind(path[-1])


def delete_all_zombies(options, tree=None):
    if not tree:
        tree = rtctree.tree.RTCTree()
    if not tree:
        return 1
    def del_zombie(node, args):
        try:
            node.parent.unbind(node.name)
        except Exception as e:
            if options.verbose:
                traceback.print_exc()
            print('{0}: {1}'.format(sys.argv[0], e), file=sys.stderr)
    tree.iterate(del_zombie, filter=['is_zombie'])


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Delete an object from a name server.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')
    parser.add_option('-z', '--zombies', dest='zombies', action='store_true',
            default=False, help='Delete only zombies. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError as e:
        print('OptionError:', e, file=sys.stderr)
        return 1

    try:
        if not args:
            if not options.zombies:
                print('{0}: No path given.'.format(sys.argv[0]),
                        file=sys.stderr)
                return 1
            else:
                # If no path given, delete all zombies found
                delete_all_zombies(options, tree)
        elif len(args) == 1:
            full_path = path.cmd_path_to_full_path(args[0])
            # Some sanity checks
            if full_path == '/':
                print('{0}: Cannot delete the root directory.'.format(sys.argv[0]),
                        file=sys.stderr)
                return 1
            delete_object_reference(args[0], full_path, options, tree)
        else:
            print(usage, file=sys.stderr)
            return 1
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

