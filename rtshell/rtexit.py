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

Implementation of the command to make a component exit.

'''


import optparse
import os
import os.path
import rtctree.tree
import rtctree.path
import RTC
import sys
import traceback

import path
import rts_exceptions
import rtshell


def exit_target(cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotAComponentError(cmd_path)

    trailing_slash = False
    if not path[-1]:
        raise rts_exceptions.NotAComponentError(cmd_path)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=path, filter=[path])

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)
    if object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not object.is_component:
        raise rts_exceptions.NotAComponentError(cmd_path)

    object.exit()


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
Make a component exit.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        # If no path given then can't do anything.
        print >>sys.stderr, '{0}: No component specified.'.format(
                os.path.basename(sys.argv[0]))
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        exit_target(cmd_path, full_path, options, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

