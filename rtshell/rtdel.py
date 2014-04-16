#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of deleting an object from a name server.

'''


import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions
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
        except Exception, e:
            if options.verbose:
                traceback.print_exc()
            print >>sys.stderr, '{0}: {1}'.format(sys.argv[0], e)
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
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    try:
        if not args:
            if not options.zombies:
                print >>sys.stderr, '{0}: No path given.'.format(sys.argv[0])
                return 1
            else:
                # If no path given, delete all zombies found
                delete_all_zombies(options, tree)
        elif len(args) == 1:
            full_path = path.cmd_path_to_full_path(args[0])
            # Some sanity checks
            if full_path == '/':
                print >>sys.stderr, '{0}: Cannot delete the root '\
                        'directory.'.format(sys.argv[0])
                return 1
            delete_object_reference(args[0], full_path, options, tree)
        else:
            print >>sys.stderr, usage
            return 1
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

