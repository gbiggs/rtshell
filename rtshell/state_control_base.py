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

Base for the scripts that change component state.

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


def alter_component_state(action, cmd_path, full_path, options, tree=None):
    path, port = rtctree.path.parse_path(full_path)
    if port:
        raise rts_exceptions.NotAComponentError(cmd_path)

    trailing_slash = False
    if not path[-1]:
        raise rts_exceptions.NotAComponentError(cmd_path)

    if not tree:
        tree = rtctree.tree.create_rtctree(paths=path, filter=[path])

    if not tree.has_path(path):
        raise rts_exceptions.NoSuchObjectError(cmd_path)
    object = tree.get_node(path)
    if object.is_zombie:
        raise rts_exceptions.ZombieObjectError(cmd_path)
    if not object.is_component:
        raise rts_exceptions.NotAComponentError(cmd_path)
    action(object, options.ec_index)


def base_main(description, action, argv=None, tree=None):
    usage = '''Usage: %prog [options] <path>
{0}

{1}'''.format(description, rtshell.RTSH_PATH_USAGE)
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-e', '--exec_context', dest='ec_index', type='int',
            action='store', default=0, help='Index of the execution context '\
            'to change state in. [Default: %default]')
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
        print >>sys.stderr, '{0}: No component specified.'.format(sys.argv[0])
        return 1
    elif len(args) == 1:
        cmd_path = args[0]
    else:
        print >>sys.stderr, usage
        return 1
    full_path = path.cmd_path_to_full_path(cmd_path)

    try:
        alter_component_state(action, cmd_path, full_path, options, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

